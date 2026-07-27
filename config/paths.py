"""Central path and settings definitions for the job scraper.

THE ONLY PLACE paths are defined. Every other module imports from here.
All paths are derived from the repository root, so the project works
regardless of where it is cloned (laptop, GitHub Actions runner, etc.).
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Roots
# ---------------------------------------------------------------------------

# Repo root = parent of the config/ directory this file lives in.
ROOT: Path = Path(__file__).resolve().parent.parent

CONFIG_DIR: Path = ROOT / "config"
DATA_DIR: Path = ROOT / "data"
SCRAPERS_DIR: Path = ROOT / "scrapers"
LOGS_DIR: Path = DATA_DIR / "logs"
DIGESTS_DIR: Path = DATA_DIR / "digests"

# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

COMPANIES_FILE: Path = CONFIG_DIR / "companies.json"
JOBS_SEEN_FILE: Path = DATA_DIR / "jobs_seen.csv"
HEALTH_FILE: Path = DATA_DIR / "scraper_health.csv"
BOARD_HTML_FILE: Path = DATA_DIR / "job_board.html"
BOARD_CSV_FILE: Path = DATA_DIR / "job_board.csv"
NEW_JOBS_COUNT_FILE: Path = DATA_DIR / "NEW_JOBS_COUNT"

# ---------------------------------------------------------------------------
# Settings (kept here so there is a single config import everywhere)
# ---------------------------------------------------------------------------

USER_AGENT: str = "job-scraper/0.1 (personal job-search tool)"
REQUEST_TIMEOUT_SECONDS: int = 20
SLEEP_BETWEEN_COMPANIES_SECONDS: float = 1.5
MAX_RETRIES: int = 1


def ensure_dirs() -> None:
    """Create runtime directories if missing. Call once at startup."""
    for d in (DATA_DIR, LOGS_DIR, DIGESTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
