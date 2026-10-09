from pathlib import Path


class Paths():
   ROOT = Path( __file__ ).resolve().parent.parent
   DATA_DIR = ROOT / 'data'
   RAW_DIR = DATA_DIR / 'raw'
   PROCESSED_DIR = DATA_DIR / 'processed'
   HISTORY = 'history'
   MULTIPLIERS = 'multipliers'
   WEIGHTS = 'weights'
   DEPTH = 'depth'
   TEAMS = 'teams'
   PROSPECTS = 'prospects'
   RECENCY = 'recency'
   INGEST = 'ingest'
   DB_PATH = PROCESSED_DIR / HISTORY / 'skaters.sqlite'
