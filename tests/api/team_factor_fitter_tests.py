from __future__ import annotations

from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.nhl_lineup_row import NhlLineupRow
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.projections.team_quality_calculator import TeamQualityCalculator
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_fitter import TeamFactorFitter


def _split(
      player_id: int,
      team: Team,
      points: float,
      games: int = 82,
      position: SkaterPosition = SkaterPosition( 'C' ) ) -> PreviousSeasonNhlSkater:
   return PreviousSeasonNhlSkater(
      player_id,
      games,
      SeasonPace( points / 2.0, points / 2.0 ),
      position,
      team )


def _pace(
      player_id: int,
      team: Team,
      points: float,
      position: SkaterPosition = SkaterPosition( 'C' ) ) -> CurrentSeasonNhlSkater:
   return CurrentSeasonNhlSkater(
      player_id,
      SeasonPace( points / 2.0, points / 2.0 ),
      team,
      position )


def _total( rows: list[ NhlLineupRow ] ) -> float:
   return TeamQualityCalculator.total( rows )


def Test_Fit_TestTeams_ExpectLeagueRelativeRates() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   elsewhere = list( Team )[ Position.THIRD ]
   current_season = 20262027
   previous_season_id = 20252026
   player_id = 1
   incoming = 2
   departed = 3
   outsider = 4
   player_points = 50.0
   incoming_points = 100.0
   departed_points = 20.0
   outsider_points = 40.0
   previous_rows = [
      _split( player_id, previous, player_points ),
      _split( departed, previous, departed_points ),
   ]
   elsewhere_rows = [
      _split( incoming, elsewhere, incoming_points ),
      _split( outsider, elsewhere, outsider_points ),
   ]
   last_league = (
      _total( previous_rows ) + _total( elsewhere_rows ) ) / 2.0
   expected = sorted(
      [
         TeamFactor(
            previous_season_id,
            previous,
            _total( previous_rows ) / last_league ),
         TeamFactor(
            previous_season_id,
            elsewhere,
            _total( elsewhere_rows ) / last_league ),
         TeamFactor( current_season, now, 1.0 ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      [ *previous_rows, *elsewhere_rows ],
      [
         _pace( player_id, now, player_points ),
         _pace( incoming, now, incoming_points ),
      ] ) == expected


def Test_Fit_TestSplitSeason_ExpectSweaterTotals() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   elsewhere = list( Team )[ Position.THIRD ]
   current_season = 20262027
   previous_season_id = 20252026
   player_id = 1
   incoming = 2
   departed = 3
   outsider = 4
   previous_rows = [
      _split( player_id, previous, 50.0 ),
      _split( departed, previous, 12.0 ),
   ]
   elsewhere_rows = [
      _split( incoming, elsewhere, 100.0 ),
      _split( departed, elsewhere, 8.0 ),
      _split( outsider, elsewhere, 40.0 ),
   ]
   last_league = (
      _total( previous_rows ) + _total( elsewhere_rows ) ) / 2.0
   expected = sorted(
      [
         TeamFactor(
            previous_season_id,
            previous,
            _total( previous_rows ) / last_league ),
         TeamFactor(
            previous_season_id,
            elsewhere,
            _total( elsewhere_rows ) / last_league ),
         TeamFactor( current_season, now, 1.0 ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      [ *previous_rows, *elsewhere_rows ],
      [
         _pace( player_id, now, 50.0 ),
         _pace( incoming, now, 100.0 ),
      ] ) == expected


def Test_Fit_TestRookie_ExpectLineupSum() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   veteran = 1
   rookie = 2
   outsider = 3
   veteran_last = 100.0
   outsider_last = 40.0
   veteran_pace = 90.0
   rookie_pace = 30.0
   outsider_pace = 60.0
   last_rows = [
      _split( veteran, now, veteran_last ),
      _split( outsider, previous, outsider_last ),
   ]
   now_rows = [
      _pace( veteran, now, veteran_pace ),
      _pace( rookie, now, rookie_pace ),
   ]
   previous_now = [ _pace( outsider, previous, outsider_pace ) ]
   last_league = (
      _total( [ last_rows[ Position.FIRST ] ] )
      + _total( [ last_rows[ Position.SECOND ] ] ) ) / 2.0
   current_league = ( _total( now_rows ) + _total( previous_now ) ) / 2.0
   expected = sorted(
      [
         TeamFactor(
            previous_season_id,
            now,
            _total( [ last_rows[ Position.FIRST ] ] ) / last_league ),
         TeamFactor(
            previous_season_id,
            previous,
            _total( [ last_rows[ Position.SECOND ] ] ) / last_league ),
         TeamFactor(
            current_season,
            now,
            _total( now_rows ) / current_league ),
         TeamFactor(
            current_season,
            previous,
            _total( previous_now ) / current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      last_rows,
      [ *now_rows, *previous_now ] ) == expected


def Test_Fit_TestUnequalRosters_ExpectUnitTeamMean() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   now_rows = [
      _pace( 1, now, 100.0 ),
      _pace( 2, now, 100.0 ),
   ]
   previous_rows = [ _pace( 3, previous, 40.0 ) ]
   league = ( _total( now_rows ) + _total( previous_rows ) ) / 2.0
   factors = TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      [
         _split( 1, now, 50.0 ),
         _split( 2, previous, 50.0 ),
      ],
      [ *now_rows, *previous_rows ] )
   current = [
      factor for factor in factors if factor.season == current_season
   ]
   assert sum( factor.rate for factor in current ) / len( current ) == 1.0
   assert sorted(
      current,
      key=lambda factor: factor.team.value ) == sorted(
      [
         TeamFactor( current_season, now, _total( now_rows ) / league ),
         TeamFactor(
            current_season,
            previous,
            _total( previous_rows ) / league ),
      ],
      key=lambda factor: factor.team.value )


def Test_Fit_TestExcessPreviousSeason_ExpectSweaterCut() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   forwards = [
      _split( player_id, previous, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 2 )
   ]
   kept = forwards[ :NhlLineupSelector.FORWARDS ]
   outsider = _split( 50, now, 40.0 )
   last_league = ( _total( kept ) + _total( [ outsider ] ) ) / 2.0
   current_rows = [
      _pace( 1, previous, 90.0 ),
      _pace( 50, now, 40.0 ),
   ]
   current_league = (
      _total( [ current_rows[ Position.FIRST ] ] )
      + _total( [ current_rows[ Position.SECOND ] ] ) ) / 2.0
   expected = sorted(
      [
         TeamFactor(
            previous_season_id,
            previous,
            _total( kept ) / last_league ),
         TeamFactor(
            previous_season_id,
            now,
            _total( [ outsider ] ) / last_league ),
         TeamFactor(
            current_season,
            previous,
            _total( [ current_rows[ Position.FIRST ] ] ) / current_league ),
         TeamFactor(
            current_season,
            now,
            _total( [ current_rows[ Position.SECOND ] ] ) / current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      [ *forwards, outsider ],
      current_rows ) == expected