import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DB_PATH = OUTPUT_DIR / "b3_factor.db"
load_dotenv(PROJECT_ROOT / ".env")
BASE_URL = "https://brapi.dev/api"
MIN_VOLUME = 1000000
TOP_N = 3


def get_token() -> str:
    token = os.getenv("BRAPI_TOKEN", "")
    if not token or token == "seu_token_aqui":
        print(
            "[ERRO] BRAPI_TOKEN não configurado.\n  1. Crie uma conta gratuita em https://brapi.dev/dashboard\n  2. Copie .env.example → .env\n  3. Substitua 'seu_token_aqui' pelo seu token real"
        )
        sys.exit(1)
    return token


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
