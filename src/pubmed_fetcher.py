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
        Search for papers with automatic subdividing for years that exceed 9,999 limit.

        Uses recursive date subdivision: if a year has >9,999 papers, splits into quarters.
        If a quarter has >9,999, splits into months. And so on.

        Args:
            mesh_term: MeSH term (e.g., '"Biology"[Mesh]' or '"Computational Biology"[Majr]')
            start_year: Start year
            end_year: End year

        Returns:
            List of all PMIDs found
        """
        from datetime import datetime

        year_range = end_year - start_year + 1
        print(f"Searching {year_range} years ({start_year}-{end_year}) with auto-subdivision...")

        all_pmids = []
        for year in range(start_year, end_year + 1):
            # Search year and auto-subdivide if needed
            pmids = self._search_recursive(
                mesh_term=mesh_term,
                start_date=f"{year}/01/01",
                end_date=f"{year}/12/31",
                label=f"Year {year}"
            )
            all_pmids.extend(pmids)
            time.sleep(0.2)

        print(f"\nTotal PMIDs across all years: {len(all_pmids)}")
        return all_pmids

    def _search_recursive(self, mesh_term: str, start_date: str, end_date: str, label: str) -> List[str]:
        """
        Recursively search with auto-subdivision if result count exceeds 9,999.

        Args:
            mesh_term: MeSH term
            start_date: Start date (YYYY/MM/DD format)
            end_date: End date (YYYY/MM/DD format)
            label: Label for logging

        Returns:
            List of PMIDs for this date range
        """
        query = (
            f'{mesh_term} NOT ('
            'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
            'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
            '"Biography"[Publication Type]) '
            f'AND ("{start_date}"[PDAT]: "{end_date}"[PDAT]) '
            'AND english[language]'
        )

        try:
            # Check total count first (without fetching)
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=0
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            count = int(search_results.get("Count", 0))

            if count == 0:
                return []

            # If under limit, fetch all
            if count <= 9999:
                print(f"  {label}: {count} papers")
                return self._fetch_pmids(query)

            # If over limit, subdivide
            print(f"  {label}: {count} papers (exceeds 9,999 - subdividing...)")
            return self._subdivide_and_search(mesh_term, start_date, end_date, label)

        except Exception as e:
            print(f"  ⚠️  Error searching {label}: {e}")
            return []

    def _subdivide_and_search(self, mesh_term: str, start_date: str, end_date: str, label: str) -> List[str]:
        """
        Subdivide date range and search recursively.

        Tries quarters first, then months if needed.

        Args:
            mesh_term: MeSH term
            start_date: Start date (YYYY/MM/DD)
            end_date: End date (YYYY/MM/DD)
            label: Label for logging

        Returns:
            Combined list of PMIDs from subdivisions
        """
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")

        # First try: divide into quarters
        quarters = self._get_date_quarters(start, end)
        if len(quarters) > 1:
            all_pmids = []
            for i, (q_start, q_end) in enumerate(quarters, 1):
                q_label = f"{label} Q{i}"
                q_start_str = q_start.strftime("%Y/%m/%d")
                q_end_str = q_end.strftime("%Y/%m/%d")
                pmids = self._search_recursive(mesh_term, q_start_str, q_end_str, q_label)
                all_pmids.extend(pmids)
                time.sleep(0.1)
            return all_pmids

        # If quarters didn't help, try months
        months = self._get_date_months(start, end)
        if len(months) > 1:
            all_pmids = []
            for m_start, m_end in months:
                m_label = f"{label} {m_start.strftime('%b')}"
                m_start_str = m_start.strftime("%Y/%m/%d")
                m_end_str = m_end.strftime("%Y/%m/%d")
                pmids = self._search_recursive(mesh_term, m_start_str, m_end_str, m_label)
                all_pmids.extend(pmids)
                time.sleep(0.1)
            return all_pmids

        # If still limited, just return what we can get
        print(f"    (Capped at 9,999 - finest granularity reached)")
        return []

    def _fetch_pmids(self, query: str) -> List[str]:
        """
        Execute a single PubMed search and return all matching PMIDs.

        Fetches up to 9,999 records (NCBI ESearch limitation).

        Args:
            query: PubMed search query

        Returns:
            List of PMIDs found
        """
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
            return pmids

        except Exception as e:
            print(f"Error fetching PMIDs: {e}")
            raise

    @staticmethod
    def _get_date_quarters(start: 'datetime', end: 'datetime'):
        """Divide date range into quarters."""
        from datetime import datetime, timedelta
        quarters = []
        current = start
        while current <= end:
            # Move to next quarter
            month = ((current.month - 1) // 3 + 1) * 3 + 1
            year = current.year + (1 if month > 12 else 0)
            month = month % 12 or 12
            q_end = min(datetime(year, month, 1) - timedelta(days=1), end)
            quarters.append((current, q_end))
            current = q_end + timedelta(days=1)
        return quarters

    @staticmethod
    def _get_date_months(start: 'datetime', end: 'datetime'):
        """Divide date range into months."""
        from datetime import datetime, timedelta
        months = []
        current = start
        while current <= end:
            # Move to next month
            if current.month == 12:
                m_end = datetime(current.year + 1, 1, 1) - timedelta(days=1)
            else:
                m_end = datetime(current.year, current.month + 1, 1) - timedelta(days=1)
            m_end = min(m_end, end)
            months.append((current, m_end))
            current = m_end + timedelta(days=1)
        return months

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
