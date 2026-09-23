from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile

from .aging_factor_store import AgingFactorStore
from .availability_weight_store import AvailabilityWeightStore
from .github_cli import GithubCli
from .league_factor_store import LeagueFactorStore
from .paths import Paths
from .scoring_weight_store import ScoringWeightStore
from .shared.enums.position import Position
from .team_factor_store import TeamFactorStore


class IngestArtifactPuller():
   WORKFLOW = 'Ingest'
   ARTIFACT = 'skaters'
   RUN_ID_FIELD = 'databaseId'
   STAMP_NAME = 'INGEST_RUN_ID'

   @classmethod
   def main( cls ) -> None:
      run_id = cls._listed_run_id()

      if not run_id or not cls._pull( run_id ):
         raise SystemExit( Position.SECOND )


   @classmethod
   def sync( cls ) -> None:
      run_id = cls._listed_run_id()

      if not run_id or not cls._needs_pull( run_id ):
         return

      cls._pull( run_id )


   @classmethod
   def install( cls, artifact_root: Path ) -> None:
      Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
      shutil.copy2( cls._source_db( artifact_root ), Paths.DB_PATH )
      shutil.copy2( cls._source_scoring( artifact_root ), ScoringWeightStore.path() )
      shutil.copy2(
         cls._source_availability( artifact_root ),
         AvailabilityWeightStore.path() )
      shutil.copy2( cls._source_aging( artifact_root ), AgingFactorStore.path() )
      shutil.copy2( cls._source_leagues( artifact_root ), LeagueFactorStore.path() )
      shutil.copy2( cls._source_teams( artifact_root ), TeamFactorStore.path() )

      if Paths.RAW_DIR.exists():
         shutil.rmtree( Paths.RAW_DIR )

      shutil.copytree( cls._source_raw( artifact_root ), Paths.RAW_DIR )
      print( Paths.DB_PATH )


   @classmethod
   def _pull( cls, run_id: str ) -> bool:
      download_dir = Path( tempfile.mkdtemp() )

      try:
         if not cls._download( run_id, download_dir ):
            return False

         artifact_root = cls._artifact_root( download_dir )

         if (
               not cls._source_db( artifact_root ).is_file()
               or not cls._source_raw( artifact_root ).is_dir()
               or not cls._source_scoring( artifact_root ).is_file()
               or not cls._source_availability( artifact_root ).is_file()
               or not cls._source_aging( artifact_root ).is_file()
               or not cls._source_leagues( artifact_root ).is_file()
               or not cls._source_teams( artifact_root ).is_file() ):
            return False

         cls.install( artifact_root )
         cls._stamp_path().write_text( run_id )
         return True
      finally:
         shutil.rmtree( download_dir, ignore_errors=True )


   @classmethod
   def _listed_run_id( cls ) -> str:
      result = GithubCli.invoke( [
         'run',
         'list',
         '--workflow',
         cls.WORKFLOW,
         '--status',
         'success',
         '--limit',
         str( Position.SECOND ),
         '--json',
         cls.RUN_ID_FIELD ] )

      if result.returncode != Position.FIRST:
         print( result.stderr )
         return ''

      return cls._run_id_from( result.stdout )


   @classmethod
   def _run_id_from( cls, stdout: str ) -> str:
      payload = json.loads( stdout )

      if not isinstance( payload, list ) or not payload:
         return ''

      row = payload[ Position.FIRST ]

      if not isinstance( row, dict ) or cls.RUN_ID_FIELD not in row:
         return ''

      return str( row[ cls.RUN_ID_FIELD ] )


   @classmethod
   def _download( cls, run_id: str, download_dir: Path ) -> bool:
      result = GithubCli.invoke( [
         'run',
         'download',
         run_id,
         '--name',
         cls.ARTIFACT,
         '--dir',
         str( download_dir ) ] )

      if result.returncode != Position.FIRST:
         print( result.stderr )
         return False

      return True


   @classmethod
   def _needs_pull( cls, run_id: str ) -> bool:
      if not Paths.DB_PATH.is_file():
         return True

      stamp_path = cls._stamp_path()

      if not stamp_path.is_file():
         return True

      return stamp_path.read_text() != run_id


   @classmethod
   def _stamp_path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.STAMP_NAME


   @classmethod
   def _artifact_root( cls, download_dir: Path ) -> Path:
      nested = download_dir / cls.ARTIFACT
      relative_db = Paths.DB_PATH.relative_to( Paths.ROOT )

      if ( nested / relative_db ).is_file():
         return nested

      return download_dir


   @classmethod
   def _source_db( cls, artifact_root: Path ) -> Path:
      return artifact_root / Paths.DB_PATH.relative_to( Paths.ROOT )


   @classmethod
   def _source_raw( cls, artifact_root: Path ) -> Path:
      return artifact_root / Paths.RAW_DIR.relative_to( Paths.ROOT )


   @classmethod
   def _source_scoring( cls, artifact_root: Path ) -> Path:
      return artifact_root / ScoringWeightStore.path().relative_to( Paths.ROOT )


   @classmethod
   def _source_availability( cls, artifact_root: Path ) -> Path:
      return artifact_root / AvailabilityWeightStore.path().relative_to( Paths.ROOT )


   @classmethod
   def _source_aging( cls, artifact_root: Path ) -> Path:
      return artifact_root / AgingFactorStore.path().relative_to( Paths.ROOT )


   @classmethod
   def _source_leagues( cls, artifact_root: Path ) -> Path:
      return artifact_root / LeagueFactorStore.path().relative_to( Paths.ROOT )


   @classmethod
   def _source_teams( cls, artifact_root: Path ) -> Path:
      return artifact_root / TeamFactorStore.path().relative_to( Paths.ROOT )
