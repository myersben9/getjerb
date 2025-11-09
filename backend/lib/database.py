import dotenv
import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import List, Dict, Union
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from dateutil.tz import gettz

from .models import JobInfo, Base
from .logger import logger


dotenv.load_dotenv()

PG_USER = os.getenv("PG_USER")  # default user in Supabase
PG_PASS = os.getenv("PG_PASS")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = 5432
PG_DB = "postgres"

DATABASE_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"



class JobDatabase:
    """Encapsulates all job database operations."""

    def __init__(self, db_url: str = DATABASE_URL, echo: bool = False):
        print("DATABASE_URL:", DATABASE_URL)
        self.engine = create_async_engine(db_url, echo=echo)
        self.SessionLocal = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    # ---------------------------------------------------------------------
    # Init / Close
    # ---------------------------------------------------------------------

    async def init_db(self):
        """Create all tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def close(self):
        """Close the database connection."""
        await self.engine.dispose()

    # ---------------------------------------------------------------------
    # Insert or Update
    # ---------------------------------------------------------------------

    async def add_or_update_job(self, job: JobInfo):
        """Insert a new job or update links if it already exists."""
        async with self.SessionLocal() as session:
            async with session.begin():
                stmt = select(JobInfo).filter(
                    JobInfo.company == job.company,
                    JobInfo.job_name == job.job_name
                )
                existing = (await session.execute(stmt)).scalar_one_or_none()

                if existing:
                    # Compare link sets
                    existing_links = {(l.location, l.link) for l in existing.links}
                    new_links = {(l.location, l.link) for l in job.links}

                    if existing_links != new_links:
                        # Replace old links entirely (delete-orphan cascade handles cleanup)
                        existing.links.clear()
                        for l in job.links:
                            existing.links.append(l)
                        logger.info(f"Updated links for: {job.company} - {job.job_name}")
                    else:
                        logger.debug(f"Skipped duplicate (no changes): {job.company} - {job.job_name}")
                else:
                    session.add(job)
                    logger.info(f"Inserted new job: {job.company} - {job.job_name}")

    async def add_or_update_job_list(self, jobs: List[JobInfo]) -> Dict[str, Union[str,int]]:
        """Insert or update multiple jobs efficiently."""
        async with self.SessionLocal() as session:
            async with session.begin():
                inserted, updated, skipped = 0, 0, 0

                for job in jobs:
                    stmt = (
                        select(JobInfo)
                        .options(selectinload(JobInfo.links))
                        .filter(JobInfo.company == job.company, JobInfo.job_name == job.job_name)
                    )
                    existing = (await session.execute(stmt)).scalar_one_or_none()

                    if existing:
                        existing_links = {(l.location, l.link) for l in existing.links}
                        new_links = {(l.location, l.link) for l in job.links}

                        if existing_links != new_links:
                            existing.links.clear()
                            for l in job.links:
                                existing.links.append(l)
                            updated += 1
                            logger.info(f"Updated links for: {job.company} - {job.job_name}")
                        else:
                            skipped += 1
                    else:
                        session.add(job)
                        inserted += 1
                        logger.info(f"Inserted new job: {job.company} - {job.job_name}")

                summary = {
                    "company": "Palantir",
                    "inserted": inserted,
                    "updated": updated,
                    "skipped": skipped,
                    "datetime" : datetime.now(tz=gettz('America/Los_Angeles')).strftime("%m/%d/%Y %I:%M:%S %p"),
                    "total_processed": inserted + updated + skipped,
                    "message": f"Palantir scrape completed. {inserted} inserted, {updated} updated, {skipped} skipped."
                }
                return summary
    # ---------------------------------------------------------------------
    # Query
    # ---------------------------------------------------------------------

    async def get_all_jobs(self, company: str | None = None):
        """Fetch all jobs (optionally filtered by company)."""
        async with self.SessionLocal() as session:
            stmt = select(JobInfo)
            if company:
                stmt = stmt.filter(JobInfo.company.ilike(f"%{company}%"))
            result = await session.execute(stmt)
            return result.scalars().unique().all()

    async def get_job(self, job_id: int):
        """Fetch a single job by ID."""
        async with self.SessionLocal() as session:
            stmt = select(JobInfo).filter(JobInfo.id == job_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()