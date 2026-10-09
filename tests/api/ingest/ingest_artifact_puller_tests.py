from __future__ import annotations

import json
from pathlib import Path
import time
from unittest.mock import Mock, patch

import pytest

from api.aging.league_arrival_store import LeagueArrivalStore
from api.aging.league_factor_store import LeagueFactorStore
from api.availability.availability_weight_store import AvailabilityWeightStore
from api.depth.depth_chart_store import DepthChartStore
from api.depth.ice_chosen_share_store import IceChosenShareStore
from api.depth.skater_ice_store import SkaterIceStore
from api.depth.slot_average_store import SlotAverageStore
from api.ingest.github_cli_result import GithubCliResult
import api.ingest.ingest_artifact_puller as ingest_artifact_puller
from api.ingest.ingest_artifact_puller import IngestArtifactPuller
from api.projections.prospect_calibration_model import ProspectCalibrationModel
from api.projections.prospect_calibration_store import ProspectCalibrationStore
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pim_weight_store import PimWeightStore
from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_model_provider import ProductionModelProvider
from api.recency.production_model_recorder import ProductionModelRecorder
from api.recency.shots_weight_store import ShotsWeightStore
from api.shared.enums.position import Position
from api.team_factor.team_factor_store import TeamFactorStore


_SQLITE_BYTES = b'sqlite'
_EMPTY_JSON = '[]'
_REGRESSION_MODEL = PaceRegressionModel(
   [],
   pim_coefficients=[ ProductionCoefficient( 18, 19, 1.1, 0.8, 100 ) ],
   shots_coefficients=[ ProductionCoefficient( 18, 19, 1.2, 0.9, 100 ) ] )


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
   db_path.write_bytes( _SQLITE_BYTES )
   raw_path.mkdir( parents=True, exist_ok=True )
   ( raw_path / 'seasons.json' ).write_text( _EMPTY_JSON )
   model_directory = db_path.parent
   with patch.object( ingest_artifact_puller.Paths, 'PROCESSED_DIR', model_directory ):
      ProductionModelRecorder.write( _REGRESSION_MODEL )
      ProspectCalibrationStore.write( ProspectCalibrationModel( 20262027, [], [] ) )
   availability_path = root / AvailabilityWeightStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   availability_path.parent.mkdir( parents=True, exist_ok=True )
   availability_path.write_text( _EMPTY_JSON )
   leagues_path = root / LeagueFactorStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   leagues_path.parent.mkdir( parents=True, exist_ok=True )
   leagues_path.write_text( _EMPTY_JSON )
   arrivals_path = root / LeagueArrivalStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   arrivals_path.parent.mkdir( parents=True, exist_ok=True )
   arrivals_path.write_text( _EMPTY_JSON )
   teams_path = root / TeamFactorStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   teams_path.parent.mkdir( parents=True, exist_ok=True )
   teams_path.write_text( _EMPTY_JSON )
   charts_path = root / DepthChartStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   charts_path.parent.mkdir( parents=True, exist_ok=True )
   charts_path.write_text( _EMPTY_JSON )
   slots_path = root / SlotAverageStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   slots_path.parent.mkdir( parents=True, exist_ok=True )
   slots_path.write_text( _EMPTY_JSON )
   ice_path = root / SkaterIceStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   ice_path.parent.mkdir( parents=True, exist_ok=True )
   ice_path.write_text( _EMPTY_JSON )
   chosen_path = root / IceChosenShareStore.path().relative_to(
      ingest_artifact_puller.Paths.ROOT )
   chosen_path.parent.mkdir( parents=True, exist_ok=True )
   chosen_path.write_text( _EMPTY_JSON )


def _write_current( run_id: str ) -> None:
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( _SQLITE_BYTES )
   ProductionModelRecorder.write( _REGRESSION_MODEL )
   ProspectCalibrationStore.write( ProspectCalibrationModel( 20262027, [], [] ) )
   LeagueArrivalStore.path().write_text( _EMPTY_JSON )
   IngestArtifactPuller._write( IngestArtifactPuller._stamp_path(), run_id )


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

   listed = IngestArtifactPuller._listed_run_id()

   assert listed == run_id
   assert IngestArtifactPuller.WORKFLOW in captured[ Position.FIRST ]
   assert IngestArtifactPuller.RUN_ID_FIELD in captured[ Position.FIRST ]


def Test_ListedRunId_TestEmptyList_ExpectEmpty( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      ingest_artifact_puller.GithubCli,
      'invoke',
      lambda args: GithubCliResult( Position.FIRST, json.dumps( [] ), '' ) )

   listed = IngestArtifactPuller._listed_run_id()

   assert listed == ''


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
   stored_db = ingest_artifact_puller.Paths.DB_PATH.read_bytes()
   stored_seasons = ( ingest_artifact_puller.Paths.RAW_DIR / 'seasons.json' ).read_text()
   stored_availability = AvailabilityWeightStore.path().read_text()
   stored_leagues = LeagueFactorStore.path().read_text()
   stored_arrivals = LeagueArrivalStore.path().read_text()
   stored_teams = TeamFactorStore.path().read_text()
   stored_charts = DepthChartStore.path().read_text()
   stored_slots = SlotAverageStore.path().read_text()
   stored_chosen = IceChosenShareStore.path().read_text()

   assert stored_db == _SQLITE_BYTES
   assert stored_seasons == _EMPTY_JSON
   assert all( path.is_file() for path in ProductionModelProvider.paths() )
   assert ProductionModelProvider.read() == _REGRESSION_MODEL
   assert stored_availability == _EMPTY_JSON
   assert stored_leagues == _EMPTY_JSON
   assert stored_arrivals == _EMPTY_JSON
   assert stored_teams == _EMPTY_JSON
   assert stored_charts == _EMPTY_JSON
   assert stored_slots == _EMPTY_JSON
   assert stored_chosen == _EMPTY_JSON


def Test_ArtifactRoot_TestNestedArtifactDir_ExpectNested(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   download_dir = tmp_path / 'download'
   nested = download_dir / IngestArtifactPuller.ARTIFACT
   _write_artifact( nested )

   artifact_root = IngestArtifactPuller._artifact_root( download_dir )

   assert artifact_root == nested



def Test_Pull_TestArtifactRootedAtData_ExpectInstalled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path,
      capsys: pytest.CaptureFixture[ str ] ) -> None:
   run_id = '99'
   _bind_paths( monkeypatch, tmp_path / 'repo' )

   def fake_download( listed_run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      data = download_dir / 'data'

      for child in list( data.iterdir() ):
         child.rename( download_dir / child.name )

      data.rmdir()
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )

   assert IngestArtifactPuller._pull( run_id )
   stored_db = ingest_artifact_puller.Paths.DB_PATH.read_bytes()
   stored_stamp = IngestArtifactPuller._stamp_path().read_text()

   assert stored_db == _SQLITE_BYTES
   assert stored_stamp == run_id
   assert 'incomplete' not in capsys.readouterr().out


def Test_Main_TestDownloadedArtifact_ExpectInstalled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   run_id = '99'
   _bind_paths( monkeypatch, tmp_path / 'repo' )

   def fake_download( listed_run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: run_id )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )

   IngestArtifactPuller.main()
   stored_db = ingest_artifact_puller.Paths.DB_PATH.read_bytes()
   stored_stamp = IngestArtifactPuller._stamp_path().read_text()

   assert stored_db == _SQLITE_BYTES
   assert stored_stamp == run_id


def Test_Sync_TestMatchingStamp_ExpectDownloadSkipped(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   run_id = '99'
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( _SQLITE_BYTES )
   ProductionModelRecorder.write( _REGRESSION_MODEL )
   ProspectCalibrationStore.write( ProspectCalibrationModel( 20262027, [], [] ) )
   LeagueArrivalStore.path().write_text( _EMPTY_JSON )
   IngestArtifactPuller._write( IngestArtifactPuller._stamp_path(), run_id )
   downloaded: list[ str ] = []

   def fake_download( current_run_id: str, download_dir: Path ) -> bool:
      downloaded.append( current_run_id )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: run_id )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )

   IngestArtifactPuller.sync()

   assert downloaded == []
   assert IngestArtifactPuller._checked_path().is_file()



def Test_Sync_TestFreshCheck_ExpectListSkipped(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   _write_current( '99' )
   IngestArtifactPuller._mark_checked()
   listed: list[ str ] = []
   monkeypatch.setattr(
      IngestArtifactPuller,
      '_listed_run_id',
      lambda: listed.append( '99' ) or '' )

   IngestArtifactPuller.sync()

   assert listed == []



def Test_Sync_TestStaleCheck_ExpectListed(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   _write_current( '99' )
   checked_at = time.time() - IngestArtifactPuller.CHECK_INTERVAL_SECONDS - 1
   IngestArtifactPuller._write( IngestArtifactPuller._checked_path(), str( checked_at ) )
   listed: list[ str ] = []
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: listed.append( '99' ) or '99' )
   monkeypatch.setattr( IngestArtifactPuller, '_download', lambda run_id, download_dir: False )

   IngestArtifactPuller.sync()

   assert listed == [ '99' ]



def Test_Sync_TestFreshCheckWithMissingFile_ExpectListed(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   _write_current( '99' )
   IngestArtifactPuller._mark_checked()
   ShotsWeightStore.path().unlink()
   listed: list[ str ] = []
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: listed.append( '99' ) or '99' )
   monkeypatch.setattr( IngestArtifactPuller, '_download', lambda run_id, download_dir: False )

   IngestArtifactPuller.sync()

   assert listed == [ '99' ]


def Test_Sync_TestNewRun_ExpectPulled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   new_run_id = '2'
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( b'old' )
   IngestArtifactPuller._write( IngestArtifactPuller._stamp_path(), '1' )

   def fake_download( run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      return True

   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: new_run_id )
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )

   IngestArtifactPuller.sync()
   stored_db = ingest_artifact_puller.Paths.DB_PATH.read_bytes()
   stored_stamp = IngestArtifactPuller._stamp_path().read_text()

   assert stored_db == _SQLITE_BYTES
   assert stored_stamp == new_run_id


def Test_Sync_TestFailedList_ExpectSkipped( monkeypatch: pytest.MonkeyPatch ) -> None:
   pulled: list[ str ] = []
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '' )
   monkeypatch.setattr( IngestArtifactPuller, '_pull', lambda run_id: pulled.append( run_id ) )

   IngestArtifactPuller.sync()

   assert pulled == []


def Test_Sync_TestMatchingStampWithMissingModelFile_ExpectPulled(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( _SQLITE_BYTES )
   ProductionModelRecorder.write( _REGRESSION_MODEL )
   ShotsWeightStore.path().unlink()
   IngestArtifactPuller._write( IngestArtifactPuller._stamp_path(), '99' )
   pulled: list[ str ] = []
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '99' )
   monkeypatch.setattr( IngestArtifactPuller, '_pull', lambda run_id: pulled.append( run_id ) )

   IngestArtifactPuller.sync()

   assert pulled == [ '99' ]


def Test_Pull_TestMissingModelFile_ExpectRejectedBeforeInstall(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path,
      capsys: pytest.CaptureFixture[ str ] ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )

   def fake_download( run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      relative_path = PimWeightStore.path().relative_to( ingest_artifact_puller.Paths.ROOT )
      ( download_dir / relative_path ).unlink()
      return True

   installed: list[ Path ] = []
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )
   monkeypatch.setattr( IngestArtifactPuller, 'install', lambda root: installed.append( root ) )

   assert not IngestArtifactPuller._pull( '99' )
   assert installed == []
   assert not IngestArtifactPuller._stamp_path().exists()
   assert 'incomplete' in capsys.readouterr().out


def Test_Pull_TestMissingCalibration_ExpectRejectedBeforeInstall(
      monkeypatch: pytest.MonkeyPatch, tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )

   def fake_download( run_id: str, download_dir: Path ) -> bool:
      _write_artifact( download_dir )
      source = download_dir / ProspectCalibrationStore.path().relative_to( ingest_artifact_puller.Paths.ROOT )
      source.unlink()
      return True

   installed = Mock()
   monkeypatch.setattr( IngestArtifactPuller, '_download', fake_download )
   monkeypatch.setattr( IngestArtifactPuller, 'install', installed )

   assert not IngestArtifactPuller._pull( '99' )
   installed.assert_not_called()


def Test_Sync_TestMissingCalibration_ExpectPulled( monkeypatch: pytest.MonkeyPatch, tmp_path: Path ) -> None:
   _bind_paths( monkeypatch, tmp_path / 'repo' )
   ingest_artifact_puller.Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
   ingest_artifact_puller.Paths.DB_PATH.write_bytes( _SQLITE_BYTES )
   ProductionModelRecorder.write( _REGRESSION_MODEL )
   IngestArtifactPuller._write( IngestArtifactPuller._stamp_path(), '99' )
   pulled = []
   monkeypatch.setattr( IngestArtifactPuller, '_listed_run_id', lambda: '99' )
   monkeypatch.setattr( IngestArtifactPuller, '_pull', lambda run_id: pulled.append( run_id ) )

   IngestArtifactPuller.sync()

   assert pulled == [ '99' ]
