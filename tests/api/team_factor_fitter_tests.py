from __future__ import annotations

from datetime import date

from api.nhl_skater_season import NhlSkaterSeason
from api.projections.career_pace import CareerPace
from api.projections.last_season_nhl_skater import LastSeasonNhlSkater
from api.roster_skater import RosterSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_fitter import TeamFactorFitter


def _roster( player_id: int, team: Team ) -> RosterSkater:
   return RosterSkater(
      player_id=player_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=team )


def _nhl(
      player_id: int,
      team: Team,
      points: float,
      season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=team,
      games_played=82,
      goals=int( points / 2.0 ),
      assists=int( points / 2.0 ),
      points=int( points ),
      schedule_games=82,
      pace_games=84,
      g_pace=points / 2.0,
      a_pace=points / 2.0,
      p_pace=points,
      gp_share=1.0 )


def _split(
      player_id: int,
      team: Team,
      points: float,
      games: float = 82.0 ) -> LastSeasonNhlSkater:
   return LastSeasonNhlSkater(
      player_id,
      games,
      CareerPace( points / 2.0, points / 2.0 ),
      team )


def Test_Fit_TestTeams_ExpectLeagueRelativeRates() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   elsewhere = list( Team )[ Position.THIRD ]
   current_season = 20262027
   last_season_id = 20252026
   player_id = 1
   incoming = 2
   departed = 3
   outsider = 4
   player_points = 50.0
   incoming_points = 100.0
   departed_points = 20.0
   outsider_points = 40.0
   last_league = (
      player_points + incoming_points + departed_points + outsider_points ) / 4.0
   current_league = ( player_points + incoming_points ) / 2.0
   roster = [
      _roster( player_id, now ),
      _roster( incoming, now ),
   ]
   nhl_seasons = [
      _nhl( player_id, previous, player_points, last_season_id ),
      _nhl( incoming, elsewhere, incoming_points, last_season_id ),
      _nhl( departed, previous, departed_points, last_season_id ),
      _nhl( outsider, elsewhere, outsider_points, last_season_id ),
   ]
   expected = sorted(
      [
         TeamFactor(
            last_season_id,
            previous,
            ( player_points + departed_points ) / 2.0 / last_league ),
         TeamFactor(
            last_season_id,
            elsewhere,
            ( incoming_points + outsider_points ) / 2.0 / last_league ),
         TeamFactor(
            current_season,
            now,
            ( player_points + incoming_points ) / 2.0 / current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      roster,
      nhl_seasons,
      [],
      [],
      current_season,
      last_season_id,
      [
         _split( player_id, previous, player_points ),
         _split( incoming, elsewhere, incoming_points ),
         _split( departed, previous, departed_points ),
         _split( outsider, elsewhere, outsider_points ),
      ] ) == expected


def Test_Fit_TestSplitSeason_ExpectSweaterRates() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   elsewhere = list( Team )[ Position.THIRD ]
   current_season = 20262027
   last_season_id = 20252026
   player_id = 1
   incoming = 2
   departed = 3
   outsider = 4
   player_points = 50.0
   incoming_points = 100.0
   departed_previous = 12.0
   departed_elsewhere = 8.0
   outsider_points = 40.0
   previous_points = player_points + departed_previous
   elsewhere_points = incoming_points + departed_elsewhere + outsider_points
   last_league = (
      previous_points + elsewhere_points ) / 5.0
   current_league = ( player_points + incoming_points ) / 2.0
   roster = [
      _roster( player_id, now ),
      _roster( incoming, now ),
   ]
   nhl_seasons = [
      _nhl( player_id, previous, player_points, last_season_id ),
      _nhl( incoming, elsewhere, incoming_points, last_season_id ),
      _nhl(
         departed,
         elsewhere,
         departed_previous + departed_elsewhere,
         last_season_id ),
      _nhl( outsider, elsewhere, outsider_points, last_season_id ),
   ]
   expected = sorted(
      [
         TeamFactor(
            last_season_id,
            previous,
            previous_points / 2.0 / last_league ),
         TeamFactor(
            last_season_id,
            elsewhere,
            elsewhere_points / 3.0 / last_league ),
         TeamFactor(
            current_season,
            now,
            ( player_points + incoming_points ) / 2.0 / current_league ),
      ],
      key=lambda factor: ( factor.season, factor.team.value ) )
   assert TeamFactorFitter.fit(
      roster,
      nhl_seasons,
      [],
      [],
      current_season,
      last_season_id,
      [
         _split( player_id, previous, player_points ),
         _split( incoming, elsewhere, incoming_points ),
         _split( departed, previous, departed_previous ),
         _split( departed, elsewhere, departed_elsewhere ),
         _split( outsider, elsewhere, outsider_points ),
      ] ) == expected
