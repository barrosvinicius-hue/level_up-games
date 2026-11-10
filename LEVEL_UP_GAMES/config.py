import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    DATABASE = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "levelup.db"))
