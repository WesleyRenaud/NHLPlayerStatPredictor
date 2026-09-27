from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.ice_usage import IceUsage
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.team_factor.team_factor import TeamFactor
from api.team_factor.team_factor_fitter import TeamFactorFitter
from api.team_factor.team_factor_skater import TeamFactorSkater


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


def _pace_points( row: PreviousSeasonNhlSkater ) -> float:
   return row.pace.goals + row.pace.assists


def _pace_total( rows: list[ PreviousSeasonNhlSkater ] ) -> float:
   return sum( _pace_points( row ) for row in rows )


def _previous_skaters(
      rows: list[ PreviousSeasonNhlSkater ] ) -> list[ TeamFactorSkater ]:
   return [
      TeamFactorSkater(
         row.player_id,
         _pace_points( row ),
         SkaterGroup.of( row.position ),
         GamesShare.FULL,
         False,
         None )
      for row in rows ]


def _previous_factor(
      season: int,
      team: Team,
      rows: list[ PreviousSeasonNhlSkater ],
      league: float ) -> TeamFactor:
   skaters = _previous_skaters( rows )
   total = sum( skater.contribution for skater in skaters )
   return TeamFactor( season, team, total / league, skaters )


def _previous(
      season: int,
      splits: list[ PreviousSeasonNhlSkater ],
      season_length: int = 82,
      usages: dict[ int, IceUsage ] | None = None ) -> list[ TeamFactor ]:
   return sorted(
      TeamFactorFitter.previous(
         season,
         splits,
         [],
         {} if usages is None else usages,
         season_length ),
      key=lambda factor: factor.team.value )


def _by_team( factors: list[ TeamFactor ] ) -> list[ TeamFactor ]:
   return sorted( factors, key=lambda factor: factor.team.value )


def Test_Previous_TestTeams_ExpectLeagueRelativeRates() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season = 20252026
   first_rows = [
      _split( 1, first, 50.0 ),
      _split( 2, first, 20.0 ),
   ]
   second_rows = [
      _split( 3, second, 100.0 ),
      _split( 4, second, 40.0 ),
   ]
   league = ( _pace_total( first_rows ) + _pace_total( second_rows ) ) / 2.0

   factors = _previous( season, [ *first_rows, *second_rows ] )

   assert factors == _by_team( [
      _previous_factor( season, first, first_rows, league ),
      _previous_factor( season, second, second_rows, league ),
   ] )


def Test_Previous_TestSplitSeason_ExpectSweaterTotals() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season = 20252026
   traded = 2
   first_rows = [
      _split( 1, first, 50.0 ),
      _split( traded, first, 12.0 ),
   ]
   second_rows = [
      _split( 3, second, 100.0 ),
      _split( traded, second, 8.0 ),
      _split( 4, second, 40.0 ),
   ]
   league = ( _pace_total( first_rows ) + _pace_total( second_rows ) ) / 2.0
   second_forwards = sorted(
      second_rows,
      key=lambda row: ( -_pace_points( row ), row.player_id ) )

   factors = _previous( season, [ *first_rows, *second_rows ] )

   assert factors == _by_team( [
      _previous_factor( season, first, first_rows, league ),
      _previous_factor( season, second, second_forwards, league ),
   ] )


def Test_Previous_TestDepth_ExpectAllSweaterTotals() -> None:
   deep = list( Team )[ Position.SECOND ]
   other = list( Team )[ Position.FIRST ]
   season = 20252026
   forwards = [
      _split( player_id, deep, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 2 )
   ]
   outsider = _split( 50, other, 40.0 )
   ranked = sorted(
      forwards,
      key=lambda row: ( -_pace_points( row ), row.player_id ) )
   top = ranked[ : NhlLineupSelector.DRESSED_FORWARDS ]
   extras = [
      TeamFactorSkater(
         row.player_id,
         _pace_points( row ),
         SkaterGroup.of( row.position ),
         GamesShare.FULL,
         True,
         None )
      for row in ranked[ NhlLineupSelector.DRESSED_FORWARDS: ]
   ]
   league = ( _pace_total( top ) + _pace_total( [ outsider ] ) ) / 2.0
   deep_factor = _previous_factor( season, deep, top, league )

   factors = _previous( season, [ *forwards, outsider ] )

   assert factors == _by_team( [
      TeamFactor(
         deep_factor.season,
         deep_factor.team,
         deep_factor.rate,
         [ *deep_factor.skaters, *extras ] ),
      _previous_factor( season, other, [ outsider ], league ),
   ] )


def Test_Previous_TestCallUp_ExpectGamesShare() -> None:
   team = list( Team )[ Position.SECOND ]
   other = list( Team )[ Position.FIRST ]
   season = 20252026
   season_length = 82
   callup_pace = 168.0
   defense = [
      _split( 1, team, callup_pace, games=1, position=SkaterPosition( 'D' ) ),
      *[
         _split( player_id, team, 20.0, position=SkaterPosition( 'D' ) )
         for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
      ],
      _split(
         NhlLineupSelector.DEFENSE,
         team,
         10.0,
         position=SkaterPosition( 'D' ) ),
   ]
   usages = {
      1: IceUsage( 16.5, 1, team, SkaterPosition( 'D' ) ),
      **{
         player_id: IceUsage( 15.0, season_length, team, SkaterPosition( 'D' ) )
         for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
      },
      NhlLineupSelector.DEFENSE: IceUsage(
         10.0,
         season_length,
         team,
         SkaterPosition( 'D' ) ),
   }

   factors = _previous(
      season,
      [ *defense, _split( 50, other, 40.0, position=SkaterPosition( 'D' ) ) ],
      season_length,
      usages )

   last = next( factor for factor in factors if factor.team == team )
   callup = next( skater for skater in last.skaters if skater.player_id == 1 )
   assert callup.availability == 1 / season_length
   present = callup_pace + 20.0 * ( NhlLineupSelector.DRESSED_DEFENSE - 1 )
   replacement = 20.0 * ( NhlLineupSelector.DRESSED_DEFENSE - 1 ) + 10.0
   expected = (
      present / season_length
      + replacement * ( season_length - 1 ) / season_length )
   assert abs( last.dressed_total() - expected ) < 0.001


def Test_Previous_TestDefense_ExpectHealthySix() -> None:
   team = list( Team )[ Position.SECOND ]
   other = list( Team )[ Position.FIRST ]
   season = 20252026
   defense = [
      _split(
         player_id,
         team,
         20.0 if player_id < 7 else 10.0,
         position=SkaterPosition( 'D' ) )
      for player_id in range( 1, 8 )
   ]
   outsider = _split( 50, other, 40.0, position=SkaterPosition( 'D' ) )

   factors = _previous( season, [ *defense, outsider ] )

   last = next( factor for factor in factors if factor.team == team )
   dressed = [
      skater
      for skater in last.skaters
      if not skater.extra
   ]
   assert abs(
      last.dressed_total()
      - sum( skater.contribution for skater in dressed ) ) < 0.001
