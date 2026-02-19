"""Database utilities for storing and querying gender inference data."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class GenderDatabase:
    """SQLite database for managing papers and authors with gender inference."""

    def __init__(self, db_path: str = "data/gender_data.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Papers table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY,
                pmid TEXT UNIQUE NOT NULL,
                title TEXT,
                year INTEGER NOT NULL,
                dataset TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Authors table (unique authors with gender info)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                p_female REAL,
                gender TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Author positions table (paper-author relationships)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS author_positions (
                id INTEGER PRIMARY KEY,
                paper_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                position TEXT NOT NULL,
                FOREIGN KEY (paper_id) REFERENCES papers(id),
                FOREIGN KEY (author_id) REFERENCES authors(id),
                UNIQUE(paper_id, author_id, position)
            )
            """
        )

        # Create indices for faster queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_papers_dataset ON papers(dataset)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_authors_gender ON authors(gender)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_author_positions_position ON author_positions(position)"
        )

        self.conn.commit()

    def insert_paper(self, pmid: str, title: str, year: int, dataset: str) -> int:
        """Insert a paper and return its ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO papers (pmid, title, year, dataset)
            VALUES (?, ?, ?, ?)
            """,
            (pmid, title, year, dataset),
        )
        self.conn.commit()

        # Return the ID
        cursor.execute("SELECT id FROM papers WHERE pmid = ?", (pmid,))
        return cursor.fetchone()[0]

    def insert_author(
        self, name: str, p_female: Optional[float], gender: str, source: str
    ) -> int:
        """Insert an author and return its ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO authors (name, p_female, gender, source)
            VALUES (?, ?, ?, ?)
            """,
            (name, p_female, gender, source),
        )
        self.conn.commit()

        # Return the ID
        cursor.execute("SELECT id FROM authors WHERE name = ?", (name,))
        return cursor.fetchone()[0]

    def insert_author_position(self, paper_id: int, author_id: int, position: str):
        """Insert an author position relationship."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO author_positions (paper_id, author_id, position)
            VALUES (?, ?, ?)
            """,
            (paper_id, author_id, position),
        )
        self.conn.commit()

    def batch_insert_author_data(
        self, author_data: List[Dict]
    ):
        """Batch insert author data from gender inference.

        Args:
            author_data: List of dicts with keys: author, p_female, gender, source
        """
        cursor = self.conn.cursor()
        for data in author_data:
            cursor.execute(
                """
                INSERT OR REPLACE INTO authors (name, p_female, gender, source)
                VALUES (?, ?, ?, ?)
                """,
                (data["author"], data["p_female"], data["gender"], data["source"]),
            )
        self.conn.commit()

    def batch_insert_positions(self, position_data: List[Dict]):
        """Batch insert author positions.

        Args:
            position_data: List of dicts with keys: pmid, author, position, year, dataset
        """
        cursor = self.conn.cursor()

        # Insert/update papers and get IDs
        paper_ids = {}
        for data in position_data:
            pmid = data["pmid"]
            if pmid not in paper_ids:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO papers (pmid, year, dataset)
                    VALUES (?, ?, ?)
                    """,
                    (pmid, data["year"], data["dataset"]),
                )
                cursor.execute("SELECT id FROM papers WHERE pmid = ?", (pmid,))
                paper_ids[pmid] = cursor.fetchone()[0]

        # Insert author positions
        for data in position_data:
            paper_id = paper_ids[data["pmid"]]
            cursor.execute(
                "SELECT id FROM authors WHERE name = ?", (data["author"],)
            )
            result = cursor.fetchone()
            if result:
                author_id = result[0]
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO author_positions (paper_id, author_id, position)
                    VALUES (?, ?, ?)
                    """,
                    (paper_id, author_id, data["position"]),
                )

        self.conn.commit()

    def get_author_data_as_dataframe(self) -> pd.DataFrame:
        """Get all author position data as a DataFrame for analysis."""
        query = """
            SELECT
                p.pmid,
                p.year,
                p.dataset,
                a.name as author,
                ap.position,
                a.p_female,
                a.gender,
                a.source
            FROM author_positions ap
            JOIN papers p ON ap.paper_id = p.id
            JOIN authors a ON ap.author_id = a.id
            ORDER BY p.year, p.dataset
        """
        return pd.read_sql_query(query, self.conn)

    def get_data_by_year_and_dataset(
        self, year_min: int, year_max: int
    ) -> pd.DataFrame:
        """Get author data filtered by year range."""
        query = """
            SELECT
                p.pmid,
                p.year,
                p.dataset,
                a.name as author,
                ap.position,
                a.p_female,
                a.gender,
                a.source
            FROM author_positions ap
            JOIN papers p ON ap.paper_id = p.id
            JOIN authors a ON ap.author_id = a.id
            WHERE p.year >= ? AND p.year <= ?
            ORDER BY p.year, p.dataset
        """
        return pd.read_sql_query(query, self.conn, params=(year_min, year_max))

    def count_unique_authors(self) -> int:
        """Count unique authors in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM authors")
        return cursor.fetchone()[0]

    def count_papers(self) -> int:
        """Count papers in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM papers")
        return cursor.fetchone()[0]

    def count_author_positions(self) -> int:
        """Count author-position relationships."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM author_positions")
        return cursor.fetchone()[0]

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
