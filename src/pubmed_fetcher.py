"""
PubMed data fetcher using NCBI E-utilities API.

Fetches Biology and Computational Biology papers from PubMed with author information.
"""

import os
import time
from typing import List, Dict, Optional
from Bio import Entrez
import pandas as pd
from tqdm import tqdm


class PubMedFetcher:
    """
    Fetches PubMed data for Biology and Computational Biology papers.

    Requires NCBI API key set in environment variable NCBI_API_KEY.
    """

    def __init__(self, email: str):
        """
        Initialize PubMed fetcher.

        Args:
            email: Email address for NCBI (required for E-utilities API).
                   NCBI API key should be in NCBI_API_KEY environment variable.
        """
        self.email = email
        Entrez.email = email
        self.api_key = os.getenv("NCBI_API_KEY")
        if self.api_key:
            Entrez.api_key = self.api_key

    def search_biology(self, start_year: int = 2015, end_year: int = 2024) -> List[str]:
        """
        Search for Biology papers on PubMed.

        Args:
            start_year: Start year for search (default 2015)
            end_year: End year for search (default 2024)

        Returns:
            List of PMIDs matching the query
        """
        query = (
            '"Biology"[Mesh] NOT ('
            'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
            'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
            '"Biography"[Publication Type]) '
            f'AND ("{start_year}/01/01"[PDAT]: "{end_year}/12/31"[PDAT]) '
            'AND english[language]'
        )
        return self._search_pmids(query)

    def search_computational_biology(self, start_year: int = 2015, end_year: int = 2024) -> List[str]:
        """
        Search for Computational Biology papers on PubMed.

        Args:
            start_year: Start year for search (default 2015)
            end_year: End year for search (default 2024)

        Returns:
            List of PMIDs matching the query
        """
        query = (
            '"Computational Biology"[Majr] NOT ('
            'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
            'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
            '"Biography"[Publication Type]) '
            f'AND ("{start_year}/01/01"[PDAT]: "{end_year}/12/31"[PDAT]) '
            'AND english[language]'
        )
        return self._search_pmids(query)

    def _search_pmids(self, query: str) -> List[str]:
        """
        Execute a PubMed search and return all matching PMIDs.

        Uses WebEnv and WebHistory for efficient batch searching.

        Args:
            query: PubMed search query

        Returns:
            List of PMIDs
        """
        print(f"Searching PubMed: {query[:80]}...")

        try:
            # Initial search to get count and WebEnv
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                usehistory="y",
                retmax=0  # We only need the count and WebEnv
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            count = int(search_results["Count"])
            web_env = search_results["WebEnv"]
            query_key = search_results["QueryKey"]

            print(f"Found {count} papers")

            if count == 0:
                return []

            # Fetch all PMIDs in batches using WebEnv
            pmids = []
            batch_size = 10000  # Fetch up to 10k at a time
            for start in range(0, count, batch_size):
                print(f"  Fetching PMIDs {start + 1} to {min(start + batch_size, count)}...")

                fetch_handle = Entrez.esearch(
                    db="pubmed",
                    term=query,
                    webenv=web_env,
                    query_key=query_key,
                    retstart=start,
                    retmax=batch_size
                )
                fetch_results = Entrez.read(fetch_handle)
                fetch_handle.close()

                pmids.extend(fetch_results["IdList"])
                time.sleep(0.1)  # Small delay to respect rate limits

            return pmids

        except Exception as e:
            print(f"Error during PubMed search: {e}")
            raise

    def fetch_paper_details(self, pmids: List[str], batch_size: int = 500) -> List[Dict]:
        """
        Fetch detailed information for a list of PMIDs.

        Args:
            pmids: List of PMIDs to fetch
            batch_size: Number of PMIDs per batch (default 500)

        Returns:
            List of dicts with paper information: PMID, year, journal, authors, etc.
        """
        papers = []
        total = len(pmids)

        print(f"Fetching details for {total} papers in batches of {batch_size}...")

        for i in tqdm(range(0, total, batch_size), desc="Fetching papers"):
            batch_pmids = pmids[i : i + batch_size]

            try:
                # Fetch XML records for this batch
                fetch_handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch_pmids),
                    rettype="xml"
                )
                records = Entrez.read(fetch_handle)
                fetch_handle.close()

                # Parse each article
                for article in records.get("PubmedArticle", []):
                    paper = self._parse_article(article)
                    if paper:
                        papers.append(paper)

                time.sleep(0.1)  # Delay to respect rate limits

            except Exception as e:
                print(f"Error fetching batch: {e}")
                continue

        print(f"Successfully fetched {len(papers)} papers")
        return papers

    def _parse_article(self, article: Dict) -> Optional[Dict]:
        """
        Parse a PubMed article XML record.

        Args:
            article: Parsed XML article from Entrez.read()

        Returns:
            Dict with paper info or None if parsing fails
        """
        try:
            medline_citation = article.get("MedlineCitation", {})
            article_data = medline_citation.get("Article", {})
            pub_data = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})

            # Extract basic info
            pmid = medline_citation.get("PMID", "")
            title = article_data.get("ArticleTitle", "")
            journal = article_data.get("Journal", {}).get("Title", "")

            # Extract publication year
            year = None
            if "Year" in pub_data:
                try:
                    year = int(pub_data["Year"])
                except (ValueError, TypeError):
                    pass

            # Extract authors and their first names
            authors = []
            author_list = article_data.get("AuthorList", [])
            for author in author_list:
                # Use LastName and ForeName from XML
                last_name = author.get("LastName", "")
                fore_name = author.get("ForeName", "")

                if fore_name and last_name:
                    # Format as "FirstName LastName"
                    full_name = f"{fore_name} {last_name}"
                    authors.append(full_name)
                elif last_name:
                    # Sometimes only LastName available
                    authors.append(last_name)

            if not authors or not year:
                return None  # Skip if missing critical info

            return {
                "pmid": str(pmid),
                "title": title,
                "journal": journal,
                "year": year,
                "authors": authors,
                "author_count": len(authors),
                "positions": []  # Will be filled by notebook
            }

        except Exception as e:
            print(f"Error parsing article: {e}")
            return None

    def save_to_csv(self, papers: List[Dict], output_path: str):
        """
        Save fetched papers to CSV.

        Args:
            papers: List of paper dicts
            output_path: Path to output CSV file
        """
        df = pd.DataFrame(papers)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} papers to {output_path}")
