"""
Gender inference utilities using a layered strategy.

Layer 1: gender-guesser (offline, ~45k names)
Layer 2: genderize.io API (fallback for unknowns)

All lookups are cached in data/gender_cache.json to avoid redundant API calls.
"""

import json
import os
from typing import Dict, Optional
import gender_guesser.detector as gender
import requests
from pathlib import Path


class GenderInference:
    """
    Infer gender from first names using a layered strategy.

    Returns probabilities: P_female in [0.0, 1.0] or None for unknown.
    """

    def __init__(self, cache_path: str = "data/gender_cache.json"):
        """
        Initialize gender inference engine.

        Args:
            cache_path: Path to gender cache JSON file
        """
        self.cache_path = cache_path
        self.detector = gender.Detector(case_sensitive=False)
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cached gender lookups from file."""
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as f:
                return json.load(f)
        return {}

    def save_cache(self):
        """Save gender cache to file."""
        os.makedirs(os.path.dirname(self.cache_path) or ".", exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f, indent=2)

    def infer_gender(self, first_name: str) -> Dict:
        """
        Infer gender from a first name.

        Returns dict with keys: name, gender, probability, source
        - gender: 'male', 'female', or 'unknown'
        - probability: float in [0.0, 1.0] or None for unknown
        - source: 'gender-guesser', 'genderize', or None

        Args:
            first_name: First name to infer gender from

        Returns:
            Dict with gender inference result
        """
        if not first_name or len(first_name) <= 1:
            return {
                "name": first_name,
                "gender": "unknown",
                "probability": None,
                "source": None
            }

        # Check cache first
        if first_name in self.cache:
            return self.cache[first_name]

        # Layer 1: gender-guesser (offline)
        result = self.detector.get_gender(first_name)

        if result == "female":
            out = {
                "name": first_name,
                "gender": "female",
                "probability": 1.0,
                "source": "gender-guesser"
            }
        elif result == "male":
            out = {
                "name": first_name,
                "gender": "male",
                "probability": 1.0,
                "source": "gender-guesser"
            }
        elif result == "mostly_female":
            out = {
                "name": first_name,
                "gender": "female",
                "probability": 0.75,
                "source": "gender-guesser"
            }
        elif result == "mostly_male":
            out = {
                "name": first_name,
                "gender": "male",
                "probability": 0.75,
                "source": "gender-guesser"
            }
        else:
            # Layer 2: genderize.io API for unknowns
            out = self._query_genderize(first_name)

        # Cache the result
        self.cache[first_name] = out
        return out

    def _query_genderize(self, first_name: str) -> Dict:
        """
        Query genderize.io API for gender inference.

        Only called for names gender-guesser couldn't resolve.

        Args:
            first_name: First name to infer gender from

        Returns:
            Dict with gender inference result
        """
        try:
            r = requests.get(f"https://api.genderize.io?name={first_name}")
            data = r.json()

            # Only accept if probability >= 0.7
            if data.get("gender") and data.get("probability", 0) >= 0.7:
                return {
                    "name": first_name,
                    "gender": data["gender"],
                    "probability": data["probability"],
                    "source": "genderize"
                }
        except Exception:
            pass

        return {
            "name": first_name,
            "gender": "unknown",
            "probability": None,
            "source": None
        }

    def infer_batch(self, first_names: list) -> list:
        """
        Infer gender for a batch of first names.

        Args:
            first_names: List of first names

        Returns:
            List of dicts with gender inference results
        """
        results = []
        for name in first_names:
            results.append(self.infer_gender(name))
        return results


def assign_positions(author_list: list) -> list:
    """
    Assign author positions based on author count.

    Replicates the original paper's position scheme:
    - 1 author: first
    - 2 authors: first, last
    - 3 authors: first, second, last
    - 4 authors: first, second, penultimate, last
    - 5+ authors: first, second, other, penultimate, last

    Args:
        author_list: List of author names

    Returns:
        List of (author_name, position) tuples
    """
    n = len(author_list)

    if n == 0:
        return []
    elif n == 1:
        return [(author_list[0], "first")]
    elif n == 2:
        return [(author_list[0], "first"), (author_list[1], "last")]
    elif n == 3:
        return [
            (author_list[0], "first"),
            (author_list[1], "second"),
            (author_list[2], "last")
        ]
    elif n == 4:
        return [
            (author_list[0], "first"),
            (author_list[1], "second"),
            (author_list[2], "penultimate"),
            (author_list[3], "last")
        ]
    else:  # 5+
        positions = (
            [(author_list[0], "first"), (author_list[1], "second")] +
            [(a, "other") for a in author_list[2:-2]] +
            [(author_list[-2], "penultimate"), (author_list[-1], "last")]
        )
        return positions
