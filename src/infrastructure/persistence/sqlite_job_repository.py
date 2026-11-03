from src.domain.entities.scraped_job import ScrapedJob
from src.domain.ports.job_repository_port import JobRepositoryPort
from datetime import datetime, timedelta, UTC
import sqlite3

class SqliteJobRepository(JobRepositoryPort):
    def __init__(self, db_path="scraper.db"):
        self.db_path = db_path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_jobs (
                    origin_page TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    PRIMARY KEY (origin_page, external_id)
                )
            """)
            conn.commit()

    def exists(self, job: ScrapedJob) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT 1
                FROM scraped_jobs
                WHERE origin_page = ?
                AND external_id = ?
            """, (job.origin_page, job.external_id)
            )
            return cursor.fetchone() is not None
        
    def exists_many(self, origin_page: str, external_ids: set[str]) -> set[str]:
        if not external_ids:
            return []

        placeholders = ",".join("?" * len(external_ids))

        query = f"""
            SELECT external_id
            FROM scraped_jobs
            WHERE origin_page = ?
            AND external_id IN ({placeholders})
        """

        params = [origin_page, *external_ids]

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return {
                row[0]
                for row in cursor.fetchall()
            }    
    
    def save(self, job: ScrapedJob):
        with self._connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO scraped_jobs
                (origin_page, external_id, first_seen_at, last_seen_at)
                VALUES (?, ?, ?, ?)
            """, (job.origin_page, job.external_id, job.first_seen_at, job.last_seen_at)
            )
            conn.commit()
    
    def save_many(self, jobs: list[ScrapedJob]):
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO scraped_jobs
                (origin_page, external_id, first_seen_at, last_seen_at)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        job.origin_page,
                        job.external_id,
                        job.first_seen_at,
                        job.last_seen_at
                    )
                    for job in jobs
                ]
            )        
    
    def touch(self, job: ScrapedJob):
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute("""
                UPDATE scraped_jobs
                SET last_seen_at = ?
                WHERE origin_page = ?
                AND external_id = ?
            """, (now, job.origin_page, job.external_id)
            )
            conn.commit()

    def find_expired(self, max_days: int):
        threshold = (datetime.now(UTC) - timedelta(days=max_days)).isoformat()

        with self._connect() as conn:
            conn.execute("""
                DELETE FROM scraped_jobs
                WHERE last_seen_at < ?
            """, (threshold,))