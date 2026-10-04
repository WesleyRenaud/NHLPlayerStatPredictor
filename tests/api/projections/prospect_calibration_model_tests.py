from __future__ import annotations

from dataclasses import replace
from datetime import date
import json
from pathlib import Path

import pytest

from api.aging.league_factor import LeagueFactor
from api.paths import Paths
from api.projections.draft_pick import DraftPick
from api.projections.nhl_season_games import NhlSeasonGames
from api.projections.pace_values import PaceValues
import api.projections.prospect_calibration_fitter as fitter
from api.projections.prospect_calibration_fitter import ProspectCalibrationFitter
from api.projections.prospect_calibration_model import ProspectCalibrationModel
from api.projections.prospect_calibration_sample import ProspectCalibrationSample
from api.projections.prospect_calibration_store import ProspectCalibrationStore
from api.projections.prospect_profile import ProspectProfile
from api.recency.pace_regression_model import PaceRegressionModel
from api.skaters.club_league import ClubLeague
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_history_builder import SkaterHistoryBuilder
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _source( player_id: int = 1 ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id, season_id=20212022, age=18.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )


def _nhl( player_id: int, season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id, season_id=season_id, age=19.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, player_name='Prospect', birth_date=date( 2000, 1, 1 ),
      team=Team.BOSTON_BRUINS, schedule_games=82, pace_games=84, p_pace=63.0, gp_share=0.5,
      playoff_games=0, playoff_goals=0, playoff_assists=0,
      even_strength_goals=10, even_strength_points=30,
      power_play_goals=0, power_play_points=0, short_handed_goals=0,
      short_handed_points=0, shots=100, penalty_minutes=20 )


@pytest.mark.parametrize( 'pick', [ None, 1, 3, 224, 288 ] )
def Test_Write_TestNumericPicks_ExpectRoundTrip(
      monkeypatch: pytest.MonkeyPatch, tmp_path: Path, pick: int | None ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   model = ProspectCalibrationModel(
      20262027, [ ProspectProfile( 1, None if pick is None else 2025, DraftPick( pick ), [ NhlSeasonGames( 20242025, 2 ) ] ) ],
      [ ProspectCalibrationSample( 1, 20252026, DraftPick( pick ), 20.0, 30.0, 'SHL' ) ] )

   ProspectCalibrationStore.write( model )

   assert ProspectCalibrationStore.read() == model
   assert json.loads( ProspectCalibrationStore.path().read_text() )[ 'samples' ][ 0 ][ 'draft_pick' ] == pick
   assert 'version' not in json.loads( ProspectCalibrationStore.path().read_text() )


def Test_Read_TestMissingStore_ExpectExplicitError( monkeypatch: pytest.MonkeyPatch, tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )

   with pytest.raises( FileNotFoundError ):
      ProspectCalibrationStore.read()


def Test_FromLanding_TestCareerSplitsAndFutureDraft_ExpectHistoricalInformation() -> None:
   first_split_games = 10
   second_split_games = 20
   target_season_games = 80
   expected_prior_games = first_split_games + second_split_games
   profile = ProspectProfile.from_landing( {
      'playerId': 1, 'draftDetails': { 'year': 2025, 'overallPick': 3 },
      'seasonTotals': [
         { 'leagueAbbrev': 'NHL', 'gameTypeId': 2, 'season': 20242025, 'gamesPlayed': first_split_games },
         { 'leagueAbbrev': 'SHL', 'gameTypeId': 2, 'season': 20242025, 'gamesPlayed': 40 },
         { 'leagueAbbrev': 'NHL', 'gameTypeId': 3, 'season': 20242025, 'gamesPlayed': 15 },
         { 'leagueAbbrev': 'NHL', 'gameTypeId': 2, 'season': 20262027, 'gamesPlayed': target_season_games },
         { 'leagueAbbrev': 'NHL', 'gameTypeId': 2, 'season': 20242025, 'gamesPlayed': second_split_games },
      ],
   } )

   assert profile.prior_games( 20262027 ) == expected_prior_games
   assert profile.nhl_games == [
      NhlSeasonGames( 20242025, expected_prior_games ), NhlSeasonGames( 20262027, target_season_games ) ]
   assert profile.draft_pick_before( 20242025 ) == DraftPick( None )
   assert profile.draft_pick_before( 20262027 ) == DraftPick( 3 )


def Test_FromLanding_TestUndraftedWithoutCareer_ExpectEmptyProfile() -> None:
   profile = ProspectProfile.from_landing( { 'playerId': 1, 'seasonTotals': [] } )

   assert profile == ProspectProfile( 1, None, DraftPick( None ), [] )
   assert profile.prior_games( 20262027 ) == 0


@pytest.mark.parametrize( 'position', [ SkaterPosition.CENTER, SkaterPosition.DEFENSE ] )
def Test_Fit_TestChronologicalEntrants_ExpectPriorOnlyAndOneVote(
      monkeypatch: pytest.MonkeyPatch, position: SkaterPosition ) -> None:
   nhl = [ _nhl( 99, 20202021 ), _nhl( 1, 20222023 ), _nhl( 1, 20232024 ), _nhl( 2, 20232024 ) ]
   other = [ _source( 1 ), _source( 2 ) ]
   nhl = [ replace( row, position=position ) for row in nhl ]
   other = [ replace( row, position=position ) for row in other ]
   profiles = [ ProspectProfile( player_id, 2022, DraftPick( 3 ), [] ) for player_id in [ 1, 2, 99 ] ]
   calls = []
   resolved = []
   monkeypatch.setattr( fitter.AgingCurveFitter, 'fit', lambda nhl, other: [] )
   monkeypatch.setattr( fitter.LeagueFactorFitter, 'fit', lambda nhl, other, aging: [ LeagueFactor( 'SHL', 0.5 ) ] )
   monkeypatch.setattr( fitter.PaceRegressionFitter, 'fit',
      lambda nhl, other, factors: calls.append( ( nhl, other ) ) or PaceRegressionModel( [] ) )
   monkeypatch.setattr( fitter.BaselinePaceResolver, 'resolve',
      lambda skater, target, factors, model: resolved.append( ( skater, target ) )
      or PaceValues( 10.0, 20.0, 2.0, 4.0, 1.0, 2.0, 30.0, 200.0 ) )

   pace_games = 84
   model = ProspectCalibrationFitter.fit( SkaterHistoryBuilder.build( [ *nhl, *other ], profiles ), 20262027, pace_games )

   assert [ ( row.player_id, row.season_id ) for row in model.samples ] == [ ( 1, 20222023 ), ( 2, 20232024 ) ]
   for sample in model.samples:
      outcome = next( row for row in nhl if row.player_id == sample.player_id and row.season_id == sample.season_id )
      expected_points = outcome.points / outcome.games_played * pace_games
      assert sample.actual_points == expected_points
      assert sample.draft_pick == DraftPick( 3 )
   for ( skater, target ), ( prior_nhl, prior_other ) in zip( resolved, calls ):
      assert all( row.season_id < target for row in [ *skater.seasons, *prior_nhl, *prior_other ] )
      assert any( row.player_id == 99 for row in prior_nhl )


def Test_Fit_TestAllLeagues_ExpectOneOutcomePerLeague( monkeypatch: pytest.MonkeyPatch ) -> None:
   leagues = [ league.value for league in ClubLeague ]
   other = [ replace( _source( player_id ), league=league ) for player_id, league in enumerate( leagues, 1 ) ]
   nhl = [ _nhl( 999, 20202021 ), *[ _nhl( row.player_id, 20222023 ) for row in other ] ]
   profiles = [ ProspectProfile( row.player_id, 2021, DraftPick( 5 ), [] ) for row in other ]
   profiles.append( ProspectProfile( 999, None, DraftPick( None ), [ NhlSeasonGames( 20202021, 40 ) ] ) )
   monkeypatch.setattr( fitter.AgingCurveFitter, 'fit', lambda nhl, other: [] )
   monkeypatch.setattr( fitter.LeagueFactorFitter, 'fit',
      lambda nhl, other, aging: [ LeagueFactor( league, 0.5 ) for league in leagues ] )
   monkeypatch.setattr( fitter.PaceRegressionFitter, 'fit', lambda nhl, other, factors: PaceRegressionModel( [] ) )
   monkeypatch.setattr( fitter.BaselinePaceResolver, 'resolve',
      lambda skater, target, factors, model: PaceValues( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None ) )

   model = ProspectCalibrationFitter.fit( SkaterHistoryBuilder.build( [ *nhl, *other ], profiles ), 20262027, 84 )

   assert len( model.samples ) == len( leagues )
   assert { row.source_league for row in model.samples } == set( leagues )
   assert all( row.predicted_points == 0.0 for row in model.samples )
