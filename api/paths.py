from pathlib import Path


class Paths():
   ROOT = Path( __file__ ).resolve().parent.parent
   DATA_DIR = ROOT / 'data'
   RAW_DIR = DATA_DIR / 'raw'
   PROCESSED_DIR = DATA_DIR / 'processed'
   DB_PATH = PROCESSED_DIR / 'skaters.sqlite'
