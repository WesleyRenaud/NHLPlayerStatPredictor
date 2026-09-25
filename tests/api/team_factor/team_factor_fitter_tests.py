from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_chart import DepthChart
from api.depth.depth_group import DepthGroup
from api.depth.ice_pace_scaler import IcePaceScaler
from api.depth.ice_skater import IceSkater
from api.depth.ice_usage import IceUsage
from api.depth.last_toi import LastToi
from api.depth.skater_ice import SkaterIce
from api.depth.slot_average import SlotAverage
from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.nhl_lineup_row import NhlLineupRow
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.projections.team_lineup import TeamLineup
from api.projections.team_quality_calculator import TeamQualityCalculator
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


def _pace_points( row: PreviousSeasonNhlSkater | CurrentSeasonNhlSkater ) -> float:
   return row.pace.goals + row.pace.assists


def _pace_total( rows: list[ PreviousSeasonNhlSkater | CurrentSeasonNhlSkater ] ) -> float:
   return sum( _pace_points( row ) for row in rows )


def _skaters(
      rows: list[ NhlLineupRow ],
      extra: bool = False,
      prior_availability: float | None = None ) -> list[ TeamFactorSkater ]:
   return [
      TeamFactorSkater(
         row.player_id,
         row.contribution,
         SkaterGroup.of( row.position ),
         GamesShare.FULL,
         extra,
         prior_availability )
      for row in rows ]


def _ice( row: CurrentSeasonNhlSkater ) -> IceSkater:
   return IceSkater(
      row.player_id,
      str( row.player_id ),
      row.position,
      row.team,
      row.contribution,
      None,
      GamesShare.FULL )


def _charts( rows: list[ CurrentSeasonNhlSkater ] ) -> list[ DepthChart ]:
   charts = []

   for lineup in TeamLineup.group( rows ):
      for group in ( DepthGroup.forwards(), DepthGroup.defense() ):
         matching = [
            _ice( skater )
            for skater in lineup.skaters
            if group.contains( skater.position )
         ]
         ranked = sorted(
            matching,
            key=lambda skater: LastToi.key( skater.player_id, skater.implied ) )
         count = group.dressed_count
         charts.append(
            DepthChart(
               lineup.team,
               [ ( skater, skater.implied ) for skater in ranked[ : count ] ],
               ranked[ count: count + group.extra_count ],
               [],
               group.skater_group ) )

   return charts


def _fit(
      current_season: int,
      previous_season_id: int,
      splits: list[ PreviousSeasonNhlSkater ],
      paces: list[ CurrentSeasonNhlSkater ],
      season_length: int,
      slots: list[ SlotAverage ] | None = None,
      usages: dict[ int, IceUsage ] | None = None ) -> list[ TeamFactor ]:
   return TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      splits,
      paces,
      season_length,
      [] if slots is None else slots,
      _charts( paces ),
      {} if usages is None else usages,
      {} )


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


def _from_lineup(
      season: int,
      team: Team,
      lineup: TeamLineup,
      league: float ) -> TeamFactor:
   return TeamFactor(
      season,
      team,
      lineup.total() / league,
      _skaters( lineup.skaters ) )


def _previous_factor(
      season: int,
      team: Team,
      rows: list[ NhlLineupRow ],
      league: float ) -> TeamFactor:
   skaters = _previous_skaters( rows )
   total = sum( skater.contribution for skater in skaters )
   return TeamFactor( season, team, total / league, skaters )


def _current_factor(
      season: int,
      team: Team,
      rows: list[ NhlLineupRow ],
      league: float ) -> TeamFactor:
   [ lineup ] = NhlLineupSelector.select( rows )
   return _from_lineup( season, team, lineup, league )


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
   now_rows = [
      _pace( player_id, now, player_points ),
      _pace( incoming, now, incoming_points ),
   ]
   last_league = (
      _pace_total( previous_rows ) + _pace_total( elsewhere_rows ) ) / 2.0
   expected = sorted(
      [
         _previous_factor( previous_season_id, previous, previous_rows, last_league ),
         _previous_factor( previous_season_id, elsewhere, elsewhere_rows, last_league ),
         _current_factor( current_season, now, now_rows, _total( now_rows ) ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert _fit(
      current_season,
      previous_season_id,
      [ *previous_rows, *elsewhere_rows ],
      now_rows,
      82 ) == expected


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
   now_rows = [
      _pace( player_id, now, 50.0 ),
      _pace( incoming, now, 100.0 ),
   ]
   last_league = (
      _pace_total( previous_rows ) + _pace_total( elsewhere_rows ) ) / 2.0
   elsewhere_forwards = sorted(
      elsewhere_rows,
      key=lambda row: ( -_pace_points( row ), row.player_id ) )
   expected = sorted(
      [
         _previous_factor( previous_season_id, previous, previous_rows, last_league ),
         _previous_factor(
            previous_season_id,
            elsewhere,
            elsewhere_forwards,
            last_league ),
         _current_factor( current_season, now, now_rows, _total( now_rows ) ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert _fit(
      current_season,
      previous_season_id,
      [ *previous_rows, *elsewhere_rows ],
      now_rows,
      82 ) == expected


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
   last_now = [ _split( veteran, now, veteran_last ) ]
   last_previous = [ _split( outsider, previous, outsider_last ) ]
   now_rows = [
      _pace( veteran, now, veteran_pace ),
      _pace( rookie, now, rookie_pace ),
   ]
   previous_now = [ _pace( outsider, previous, outsider_pace ) ]
   last_league = ( _pace_total( last_now ) + _pace_total( last_previous ) ) / 2.0
   current_league = ( _total( now_rows ) + _total( previous_now ) ) / 2.0
   expected = sorted(
      [
         _previous_factor( previous_season_id, now, last_now, last_league ),
         _previous_factor( previous_season_id, previous, last_previous, last_league ),
         _current_factor( current_season, now, now_rows, current_league ),
         _current_factor( current_season, previous, previous_now, current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert _fit(
      current_season,
      previous_season_id,
      [ *last_now, *last_previous ],
      [ *now_rows, *previous_now ],
      82 ) == expected


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
   factors = _fit(
      current_season,
      previous_season_id,
      [
         _split( 1, now, 50.0 ),
         _split( 2, previous, 50.0 ),
      ],
      [ *now_rows, *previous_rows ],
      82 )
   current = [
      factor for factor in factors if factor.season == current_season
   ]
   assert sum( factor.rate for factor in current ) / len( current ) == 1.0
   assert sorted(
      current,
      key=lambda factor: factor.team.value ) == sorted(
      [
         _current_factor( current_season, now, now_rows, league ),
         _current_factor( current_season, previous, previous_rows, league ),
      ],
      key=lambda factor: factor.team.value )


def Test_Fit_TestPreviousSeasonDepth_ExpectAllSweaterTotals() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   forwards = [
      _split( player_id, previous, 100.0 - player_id )
      for player_id in range( 1, NhlLineupSelector.FORWARDS + 2 )
   ]
   outsider = _split( 50, now, 40.0 )
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
   last_league = ( _pace_total( top ) + _pace_total( [ outsider ] ) ) / 2.0
   current_previous = [ _pace( 1, previous, 90.0 ) ]
   current_now = [ _pace( 50, now, 40.0 ) ]
   current_league = (
      _total( current_previous ) + _total( current_now ) ) / 2.0
   previous_factor = _previous_factor(
      previous_season_id,
      previous,
      top,
      last_league )
   expected = sorted(
      [
         TeamFactor(
            previous_factor.season,
            previous_factor.team,
            previous_factor.rate,
            [ *previous_factor.skaters, *extras ] ),
         _previous_factor( previous_season_id, now, [ outsider ], last_league ),
         _current_factor( current_season, previous, current_previous, current_league ),
         _current_factor( current_season, now, current_now, current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert _fit(
      current_season,
      previous_season_id,
      [ *forwards, outsider ],
      [ *current_previous, *current_now ],
      82 ) == expected


def Test_Fit_TestShortDefense_ExpectPaddedSeventh() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   slots = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]
   defense = [
      _pace(
         player_id,
         now,
         40.0 - player_id,
         position=SkaterPosition( 'D' ) )
      for player_id in range( 1, NhlLineupSelector.DEFENSE )
   ]
   outsider = _pace( 50, previous, 40.0, position=SkaterPosition( 'D' ) )
   factors = _fit(
      current_season,
      previous_season_id,
      [ _split( 50, previous, 40.0, position=SkaterPosition( 'D' ) ) ],
      [ *defense, outsider ],
      82,
      slots )
   current = next(
      factor
      for factor in factors
      if factor.season == current_season and factor.team == now )
   assert any(
      skater.extra and skater.contribution == slots[ Position.FIRST ].contribution
      for skater in current.skaters )
   regular_points = sum( row.contribution for row in defense )
   assert abs( current.dressed_total() - regular_points ) < 0.001


def Test_Fit_TestPreviousCallUp_ExpectGamesShare() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   season_length = 82
   callup_pace = 168.0
   defense = [
      _split( 1, previous, callup_pace, games=1, position=SkaterPosition( 'D' ) ),
      *[
         _split( player_id, previous, 20.0, position=SkaterPosition( 'D' ) )
         for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
      ],
      _split(
         NhlLineupSelector.DEFENSE,
         previous,
         10.0,
         position=SkaterPosition( 'D' ) ),
   ]
   usages = {
      1: IceUsage( 16.5, 1, previous, SkaterPosition( 'D' ) ),
      **{
         player_id: IceUsage( 15.0, season_length, previous, SkaterPosition( 'D' ) )
         for player_id in range( 2, NhlLineupSelector.DRESSED_DEFENSE + 1 )
      },
      NhlLineupSelector.DEFENSE: IceUsage(
         10.0,
         season_length,
         previous,
         SkaterPosition( 'D' ) ),
   }
   factors = _fit(
      current_season,
      previous_season_id,
      [ *defense, _split( 50, now, 40.0, position=SkaterPosition( 'D' ) ) ],
      [ _pace( 50, now, 40.0, position=SkaterPosition( 'D' ) ) ],
      season_length,
      usages=usages )
   last = next(
      factor
      for factor in factors
      if factor.season == previous_season_id and factor.team == previous )
   callup = next( skater for skater in last.skaters if skater.player_id == 1 )
   assert callup.availability == 1 / season_length
   present = callup_pace + 20.0 * ( NhlLineupSelector.DRESSED_DEFENSE - 1 )
   replacement = 20.0 * ( NhlLineupSelector.DRESSED_DEFENSE - 1 ) + 10.0
   expected = (
      present / season_length
      + replacement * ( season_length - 1 ) / season_length )
   assert abs( last.dressed_total() - expected ) < 0.001


def Test_Fit_TestPreviousDefense_ExpectHealthySix() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   defense = [
      _split(
         player_id,
         previous,
         20.0 if player_id < 7 else 10.0,
         position=SkaterPosition( 'D' ) )
      for player_id in range( 1, 8 )
   ]
   outsider = _split( 50, now, 40.0, position=SkaterPosition( 'D' ) )
   factors = _fit(
      current_season,
      previous_season_id,
      [ *defense, outsider ],
      [ _pace( 50, now, 40.0, position=SkaterPosition( 'D' ) ) ],
      82 )
   last = next(
      factor
      for factor in factors
      if factor.season == previous_season_id and factor.team == previous )
   assert abs( last.dressed_total() - 120.0 ) < 0.001


def Test_Fit_TestCurrentIce_ExpectLastToiScale() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   current_season = 20262027
   previous_season_id = 20252026
   player_id = 1
   points = 100.0
   last_toi = 20.0
   implied = 10.0
   projected = 24.0
   paces = [ _pace( player_id, now, points ) ]
   factors = TeamFactorFitter.fit(
      current_season,
      previous_season_id,
      [ _split( 2, previous, 40.0 ) ],
      paces,
      82,
      [],
      _charts( paces ),
      {},
      { player_id: SkaterIce( player_id, last_toi, implied, projected ) } )
   current = next(
      factor
      for factor in factors
      if factor.season == current_season and factor.team == now )
   scaled = points * IcePaceScaler.ratio( last_toi, projected )
   assert any(
      skater.player_id == player_id and abs( skater.contribution - scaled ) < 0.001
      for skater in current.skaters )
