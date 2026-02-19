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

        Splits search by year to overcome 9,999 record limit per query.

        Args:
            start_year: Start year for search (default 2015)
            end_year: End year for search (default 2024)

        Returns:
            List of PMIDs matching the query
        """
        return self._search_by_year_range(
            mesh_term='"Biology"[Mesh]',
            start_year=start_year,
            end_year=end_year
        )

    def search_computational_biology(self, start_year: int = 2015, end_year: int = 2024) -> List[str]:
        """
        Search for Computational Biology papers on PubMed.

        Splits search by year to overcome 9,999 record limit per query.

        Args:
            start_year: Start year for search (default 2015)
            end_year: End year for search (default 2024)

        Returns:
            List of PMIDs matching the query
        """
        return self._search_by_year_range(
            mesh_term='"Computational Biology"[Majr]',
            start_year=start_year,
            end_year=end_year
        )

    def _search_by_year_range(self, mesh_term: str, start_year: int, end_year: int) -> List[str]:
        """
        Search for papers year-by-year to overcome 9,999 record limit.

        Splits the search into individual year queries and combines results.

        Args:
            mesh_term: MeSH term (e.g., '"Biology"[Mesh]' or '"Computational Biology"[Majr]')
            start_year: Start year
            end_year: End year

        Returns:
            List of all PMIDs found across all years
        """
        all_pmids = []
        year_range = end_year - start_year + 1

        print(f"Searching {year_range} years ({start_year}-{end_year}) by year to retrieve all results...")

        for year in range(start_year, end_year + 1):
            query = (
                f'{mesh_term} NOT ('
                'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
                'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
                '"Biography"[Publication Type]) '
                f'AND ("{year}/01/01"[PDAT]: "{year}/12/31"[PDAT]) '
                'AND english[language]'
            )

            try:
                pmids = self._search_pmids(query, year=year)
                all_pmids.extend(pmids)
            except Exception as e:
                print(f"  ⚠️  Error searching year {year}: {e}")
                continue

            time.sleep(0.2)  # Delay between year queries

        print(f"\nTotal PMIDs across all years: {len(all_pmids)}")
        return all_pmids

    def _search_pmids(self, query: str, year: Optional[int] = None) -> List[str]:
        """
        Execute a single PubMed search and return all matching PMIDs.

        Fetches up to 9,999 records (NCBI ESearch limitation).

        Args:
            query: PubMed search query
            year: Year (for logging purposes)

        Returns:
            List of PMIDs found
        """
        year_str = f" ({year})" if year else ""
        print(f"  Searching{year_str}...", end=" ")

        try:
            # Execute search with retmax=9999 to get all available results
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=9999,  # Maximum allowed
                rettype="uilist",
                retmode="xml"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            pmids = search_results.get("IdList", [])
            count = int(search_results.get("Count", 0))

            print(f"Found {len(pmids)} papers (total: {count})")

            return pmids

        except Exception as e:
            print(f"Error")
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
