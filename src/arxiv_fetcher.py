"""
arXiv data fetcher.

Fetches quantitative biology (q-bio) and computer science (cs) preprints from arXiv.
"""

from typing import List, Dict
import arxiv
import pandas as pd
from tqdm import tqdm


class arXivFetcher:
    """Fetches preprints from arXiv API."""

    def __init__(self, delay_seconds: float = 3.0):
        """
        Initialize arXiv fetcher.

        Args:
            delay_seconds: Delay between API requests (default 3.0)
        """
        self.client = arxiv.Client(
            page_size=1000,
            delay_seconds=delay_seconds,
            num_retries=5
        )

    def fetch_quantitative_biology(self, start_year: int = 2015, end_year: int = 2024) -> List[Dict]:
        """
        Fetch quantitative biology (q-bio) preprints.

        Args:
            start_year: Start year (default 2015)
            end_year: End year (default 2024)

        Returns:
            List of dicts with preprint information
        """
        return self._fetch_category(
            category="q-bio",
            start_year=start_year,
            end_year=end_year
        )

    def fetch_computer_science(self, start_year: int = 2015, end_year: int = 2024) -> List[Dict]:
        """
        Fetch computer science (cs) preprints.

        Args:
            start_year: Start year (default 2015)
            end_year: End year (default 2024)

        Returns:
            List of dicts with preprint information
        """
        return self._fetch_category(
            category="cs",
            start_year=start_year,
            end_year=end_year
        )

    def _fetch_category(self, category: str, start_year: int = 2015, end_year: int = 2024) -> List[Dict]:
        """
        Fetch preprints from a specific arXiv category.

        Args:
            category: arXiv category (e.g., 'q-bio', 'cs')
            start_year: Start year (default 2015)
            end_year: End year (default 2024)

        Returns:
            List of dicts with preprint information
        """
        preprints = []

        print(f"Fetching {category} preprints ({start_year}-{end_year})...")
        print("Note: This may take several minutes due to API rate limiting...")

        # Search for all papers in category from start_year to end_year
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=None,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        for result in tqdm(self.client.results(search), desc=f"Fetching {category}"):
            # Filter by year
            year = result.published.year
            if year < start_year or year > end_year:
                continue

            # Extract authors
            authors = [str(author) for author in result.authors]

            preprint = {
                "arxiv_id": result.entry_id.split("/abs/")[-1],
                "title": result.title,
                "year": year,
                "published_date": result.published,
                "authors": authors,
                "author_count": len(authors),
                "category": category,
                "positions": []  # Will be filled by notebook
            }
            preprints.append(preprint)

        print(f"Fetched {len(preprints)} {category} preprints")
        return preprints

    def _parse_arxiv_authors(self, authors: List) -> List[str]:
        """
        Parse author names from arXiv result.

        Note: arXiv author names are often "First Last" or "First Middle Last" format.
        They're already parsed as strings by the arxiv library.

        Args:
            authors: List of author objects from arxiv result

        Returns:
            List of author name strings
        """
        return [str(author) for author in authors]

    def save_to_csv(self, preprints: List[Dict], output_path: str):
        """
        Save fetched preprints to CSV.

        Args:
            preprints: List of preprint dicts
            output_path: Path to output CSV file
        """
        df = pd.DataFrame(preprints)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} preprints to {output_path}")
