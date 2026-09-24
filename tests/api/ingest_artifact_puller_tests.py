from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.aging_factor_store import AgingFactorStore
from api.availability_weight_store import AvailabilityWeightStore
from api.depth_chart_store import DepthChartStore
from api.github_cli_result import GithubCliResult
import api.ingest_artifact_puller as ingest_artifact_puller
from api.ingest_artifact_puller import IngestArtifactPuller
from api.league_factor_store import LeagueFactorStore
from api.scoring_weight_store import ScoringWeightStore
from api.shared.enums.position import Position
from api.skater_ice_store import SkaterIceStore
from api.slot_average_store import SlotAverageStore
from api.slot_chosen_share_store import SlotChosenShareStore
from api.team_factor_store import TeamFactorStore


def _bind_paths( monkeypatch: pytest.MonkeyPatch, root: Path ) -> None:
   paths = ingest_artifact_puller.Paths
   data_name = paths.DATA_DIR.name
   processed_name = paths.PROCESSED_DIR.name
   raw_name = paths.RAW_DIR.name
   db_name = paths.DB_PATH.name
   data = root / data_name
   processed = data / processed_name
   raw = data / raw_name
   monkeypatch.setattr( paths, 'ROOT', root )
   monkeypatch.setattr( paths, 'DATA_DIR', data )
   monkeypatch.setattr( paths, 'PROCESSED_DIR', processed )
   monkeypatch.setattr( paths, 'RAW_DIR', raw )
   monkeypatch.setattr( paths, 'DB_PATH', processed / db_name )


def _write_artifact( root: Path ) -> None:
   db_path = root / ingest_artifact_puller.Paths.DB_PATH.relative_to(
      ingest_artifact_puller.Paths.ROOT )
   raw_path = root / ingest_artifact_puller.Paths.RAW_DIR.relative_to(
      ingest_artifact_puller.Paths.ROOT )
   db_path.parent.mkdir( parents=True, exist_ok=True )
   db_path.write_bytes( b'sqlite' )
   raw_path.mkdir( parents=True, exist_ok=True )
   ( raw_path / 'seasons.json' ).write_text( '[]' )
   weights_path = root / ScoringWeightStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   weights_path.parent.mkdir( parents=True, exist_ok=True )
   weights_path.write_text( '[]' )
   availability_path = root / AvailabilityWeightStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   availability_path.parent.mkdir( parents=True, exist_ok=True )
   availability_path.write_text( '[]' )
   aging_path = root / AgingFactorStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   aging_path.parent.mkdir( parents=True, exist_ok=True )
   aging_path.write_text( '[]' )
   leagues_path = root / LeagueFactorStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   leagues_path.parent.mkdir( parents=True, exist_ok=True )
   leagues_path.write_text( '[]' )
   teams_path = root / TeamFactorStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   teams_path.parent.mkdir( parents=True, exist_ok=True )
   teams_path.write_text( '[]' )
   charts_path = root / DepthChartStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   charts_path.parent.mkdir( parents=True, exist_ok=True )
   charts_path.write_text( '[]' )
   slots_path = root / SlotAverageStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   slots_path.parent.mkdir( parents=True, exist_ok=True )
   slots_path.write_text( '[]' )
   ice_path = root / SkaterIceStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   ice_path.parent.mkdir( parents=True, exist_ok=True )
   ice_path.write_text( '[]' )
   chosen_path = root / SlotChosenShareStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   chosen_path.parent.mkdir( parents=True, exist_ok=True )
   chosen_path.write_text( '[]' )


def Test_ListedRunId_TestRuns_ExpectFirstId( monkeypatch: pytest.MonkeyPatch ) -> None:
   run_id = '42'
   captured: list[ list[ str ] ] = []

   def fake_invoke( args: list[ str ] ) -> GithubCliResult:
      captured.append( args )
      return GithubCliResult(
         Position.FIRST,
         json.dumps( [ { IngestArtifactPuller.RUN_ID_FIELD: run_id } ] ),
         '' )

   monkeypatch.setattr( ingest_artifact_puller.GithubCli, 'invoke', fake_invoke )
   assert IngestArtifactPuller._listed_run_id() == run_id
   assert IngestArtifactPuller.WORKFLOW in captured[ Position.FIRST ]
   assert IngestArtifactPuller.RUN_ID_FIELD in captured[ Position.FIRST ]


def Test_ListedRunId_TestEmptyList_ExpectEmpty( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      ingest_artifact_puller.GithubCli,
      'invoke',
      lambda args: GithubCliResult( Position.FIRST, json.dumps( [] ), '' ) )
   assert IngestArtifactPuller._listed_run_id() == ''


def Test_Main_TestEmptyList_ExpectSystemExit( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '' )

   with pytest.raises( SystemExit ) as exit_info:
      IngestArtifactPuller.main()

   assert exit_info.value.code == Position.SECOND


def Test_Install_TestArtifactTree_ExpectCopiedDbAndRaw(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   artifact_root = tmp_path / 'artifact'
   _write_artifact( artifact_root )
   IngestArtifactPuller.install( artifact_root )
   assert ingest_artifact_puller.Paths.DB_PATH.read_bytes() == b'sqlite'
   assert ( ingest_artifact_puller.Paths.RAW_DIR / 'seasons.json' ).read_text() == '[]'
   assert ScoringWeightStore.path().read_text() == '[]'
   assert AvailabilityWeightStore.path().read_text() == '[]'
   assert AgingFactorStore.path().read_text() == '[]'
   assert LeagueFactorStore.path().read_text() == '[]'
   assert TeamFactorStore.path().read_text() == '[]'
   assert DepthChartStore.path().read_text() == '[]'
   assert SlotAverageStore.path().read_text() == '[]'
   assert SlotChosenShareStore.path().read_text() == '[]'


def Test_ArtifactRoot_TestNestedArtifactDir_ExpectNested(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   download_dir = tmp_path / 'download'
   nested = download_dir / IngestArtifactPuller.ARTIFACT
   _write_artifact( nested )
   assert IngestArtifactPuller._artifact_root( download_dir ) == nested


def Test_Main_TestDownloadedArtifact_ExpectInstalled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )

   def fake_download( run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '99' )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )
   IngestArtifactPuller.main()
   assert ingest_artifact_puller.Paths.DB_PATH.read_bytes() == b'sqlite'
   assert IngestArtifactPuller._stamp_path().read_text() == '99'


def Test_Sync_TestMatchingStamp_ExpectDownloadSkipped(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   run_id = '99'
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( b'sqlite' )
   IngestArtifactPuller._stamp_path().write_text( run_id )
   downloaded: list[ str ] = []

   def fake_download( current_run_id: str, download_dir: Path ) -> bool:
      downloaded.append( current_run_id )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: run_id )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )
   IngestArtifactPuller.sync()
   assert downloaded == []


def Test_Sync_TestNewRun_ExpectPulled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( b'old' )
   IngestArtifactPuller._stamp_path().write_text( '1' )

   def fake_download( run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '2' )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )
   IngestArtifactPuller.sync()
   assert ingest_artifact_puller.Paths.DB_PATH.read_bytes() == b'sqlite'
   assert IngestArtifactPuller._stamp_path().read_text() == '2'


def Test_Sync_TestFailedList_ExpectSkipped( monkeypatch: pytest.MonkeyPatch ) -> None:
   pulled: list[ str ] = []

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '' )
   monkeypatch.setattr( IngestArtifactPuller, '_pull', lambda run_id: pulled.append( run_id ) )
   IngestArtifactPuller.sync()
   assert pulled == []
