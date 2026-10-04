from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.draft_pick import DraftPick
from api.projections.nhl_season_games import NhlSeasonGames
from api.projections.pace_values import PaceValues
from api.projections.prospect_calibration_model import ProspectCalibrationModel
from api.projections.prospect_calibration_resolver import ProspectCalibrationResolver
from api.projections.prospect_calibration_sample import ProspectCalibrationSample
from api.projections.prospect_calibration_store import ProspectCalibrationStore
from api.projections.prospect_profile import ProspectProfile
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater import Skater
from api.skaters.skater_position import SkaterPosition


def _source() -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1, season_id=20252026, age=18.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )


def _model( scoring_factor: float = 1.5 ) -> ProspectCalibrationModel:
   return ProspectCalibrationModel(
      20262027, [ ProspectProfile( 1, 2025, DraftPick( 3 ), [] ) ],
      [
         ProspectCalibrationSample( 2, 20242025, DraftPick( 1 ), 20.0, 20.0 * scoring_factor, 'SHL' ),
         ProspectCalibrationSample( 3, 20242025, DraftPick( 20 ), 40.0, 40.0 * scoring_factor, 'OHL' ),
         ProspectCalibrationSample( 1, 20242025, DraftPick( 3 ), 100.0, 0.0, 'SHL' ),
         ProspectCalibrationSample( 4, 20262027, DraftPick( 3 ), 100.0, 0.0, 'SHL' ),
      ] )


def _paces() -> PaceValues:
   return PaceValues( 10.0, 20.0, 2.0, 4.0, 1.0, 2.0, 30.0, 200.0 )


@pytest.mark.parametrize( 'nhl_games', [ [], [ NhlSeasonGames( 20242025, 25 ) ], [ NhlSeasonGames( 20262027, 26 ) ] ] )
@pytest.mark.parametrize( 'position', [ SkaterPosition.CENTER, SkaterPosition.DEFENSE ] )
def Test_Adjust_TestEligibleProspect_ExpectChronologicalCurveAndScoringOnly(
      monkeypatch: pytest.MonkeyPatch, nhl_games: list[ NhlSeasonGames ], position: SkaterPosition ) -> None:
   expected_factor = 1.5
   model = replace( _model( expected_factor ), profiles=[ ProspectProfile( 1, 2025, DraftPick( 3 ), nhl_games ) ] )
   monkeypatch.setattr( ProspectCalibrationStore, 'read', lambda: model )
   before = _paces()

   after = ProspectCalibrationResolver.adjust(
      Skater( [ replace( _source(), position=position ) ] ), 20262027, before, [ LeagueFactor( 'SHL', 0.5 ) ] )

   assert after == replace(
      before,
      even_strength_goals=before.even_strength_goals * expected_factor,
      even_strength_assists=before.even_strength_assists * expected_factor,
      power_play_goals=before.power_play_goals * expected_factor,
      power_play_assists=before.power_play_assists * expected_factor,
      short_handed_goals=before.short_handed_goals * expected_factor,
      short_handed_assists=before.short_handed_assists * expected_factor )
   assert after.penalty_minutes == before.penalty_minutes
   assert after.shots == before.shots


@pytest.mark.parametrize( 'pick, year, games', [ ( None, None, 0 ), ( 33, 2025, 0 ), ( 3, 2027, 0 ), ( 3, 2025, 26 ) ] )
def Test_Adjust_TestExcludedProfile_ExpectBaseline(
      monkeypatch: pytest.MonkeyPatch, pick: int | None, year: int | None, games: int ) -> None:
   model = replace( _model(), profiles=[ ProspectProfile( 1, year, DraftPick( pick ), [ NhlSeasonGames( 20242025, games ) ] ) ] )
   monkeypatch.setattr( ProspectCalibrationStore, 'read', lambda: model )
   before = _paces()

   assert ProspectCalibrationResolver.adjust(
      Skater( [ _source() ] ), 20262027, before, [ LeagueFactor( 'SHL', 0.5 ) ] ) is before


@pytest.mark.parametrize( 'source', [
   replace( _source(), games_played=19 ),
   replace( _source(), age=24 ),
   replace( _source(), season_id=20242025 ),
] )
def Test_Adjust_TestUnusableSource_ExpectBaselineWithoutArtifact(
      monkeypatch: pytest.MonkeyPatch, source: OtherLeagueSkaterSeason ) -> None:
   monkeypatch.setattr( ProspectCalibrationStore, 'read', Mock( side_effect=AssertionError() ) )
   before = _paces()

   assert ProspectCalibrationResolver.adjust(
      Skater( [ source ] ), 20262027, before, [ LeagueFactor( 'SHL', 0.5 ) ] ) is before


def Test_Adjust_TestUnsupportedTranslation_ExpectBaselineWithoutArtifact(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( ProspectCalibrationStore, 'read', Mock( side_effect=AssertionError() ) )
   before = _paces()

   assert ProspectCalibrationResolver.adjust( Skater( [ _source() ] ), 20262027, before, [] ) is before
