import os

from dotenv import load_dotenv

project_folder = os.path.abspath(os.path.dirname("configuration"))
load_dotenv(os.path.join(project_folder, '.env'))

BOT_TOKEN = os.getenv("BOT_TOKEN")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGDBNAME = os.getenv("PGDBNAME")
PGPORT = os.getenv("PGPORT")
