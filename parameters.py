
MAX_REVISIONS = 2
RATE_LIMIT_DELAY = 30 # sleep parameter for free-tier limits abuse

from pathlib import Path
SCRIPT_DIR = Path(__file__).parent
PAPER_PATH = SCRIPT_DIR / "/paper.pdf"