"""
Gender Representation in Computational Biology Analysis Pipeline
"""

__version__ = "0.1.0"
__author__ = "Lina Faller, Ph.D."

from .pubmed_fetcher import PubMedFetcher
from .arxiv_fetcher import arXivFetcher
from .gender_utils import GenderInference
from .bootstrap import bootstrap_pfemale
from .plotting import plot_pfemale_by_position

__all__ = [
    "PubMedFetcher",
    "arXivFetcher",
    "GenderInference",
    "bootstrap_pfemale",
    "plot_pfemale_by_position",
]
