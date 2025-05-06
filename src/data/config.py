import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '../../database/nf-goiana.db'))
KEY_GOIANA = os.environ.get("KEY_GOIANA")
