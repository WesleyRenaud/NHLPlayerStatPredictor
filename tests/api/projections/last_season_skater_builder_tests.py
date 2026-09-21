from __future__ import annotations

from datetime import date

from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.projections.career_pace import CareerPace
from api.projections.last_season_group import LastSeasonGroup
from api.projections.last_season_nhl_skater import LastSeasonNhlSkater
from api.projections.last_season_skater import LastSeasonSkater
from api.projections.last_season_skater_builder import LastSeasonSkaterBuilder
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _nhl(
      player_id: int,
      team: Team,
      g_pace: float,
      a_pace: float,
      games_played: int = 82 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=team,
      games_played=games_played,
      goals=int( g_pace ),
      assists=int( a_pace ),
      points=int( g_pace + a_pace ),
      schedule_games=82,
      pace_games=84,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def _other(
      player_id: int,
      g_pace: float,
      a_pace: float,
      league: str,
      games_played: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      league=league,
      age=20.8,
      games_played=games_played,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Build_TestNhlOnDifferentTeam_ExpectPaceFromThatSeason() -> None:
   team = list( Team )[ Position.FIRST ]
   nhl = _nhl( 7, team, 40.0, 50.0 )
   group = LastSeasonSkaterBuilder.build( [ nhl ], [], [] )
   assert group == LastSeasonGroup(
      [
         LastSeasonNhlSkater(
            nhl.player_id,
            float( nhl.games_played ),
            CareerPace( nhl.g_pace, nhl.a_pace ),
            nhl.team )
      ],
      [] )


def Test_Build_TestOtherLeagueOnly_ExpectTranslatedPaceWithoutNhlTeam() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   other = _other( 7, 20.0, 30.0, league, 46 )
   pace, games = TranslatedPaceAverager.year( None, [ other ], [ factor ] )
   group = LastSeasonSkaterBuilder.build( [], [ other ], [ factor ] )
   assert group == LastSeasonGroup(
      [],
      [ LastSeasonSkater( other.player_id, games, pace ) ] )


def Test_Build_TestNhlAndOther_ExpectBlendedPaceAndNhlTeam() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   team = list( Team )[ Position.SECOND ]
   nhl = _nhl( 7, team, 84.0, 84.0, 1 )
   other = _other( 7, 10.96, 23.74, league, 46 )
   pace, games = TranslatedPaceAverager.year( nhl, [ other ], [ factor ] )
   group = LastSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] )
   assert group == LastSeasonGroup(
      [ LastSeasonNhlSkater( nhl.player_id, games, pace, nhl.team ) ],
      [] )


def Test_Build_TestUnknownLeague_ExpectOmitted() -> None:
   other = _other( 7, 20.0, 30.0, 'AAA', 46 )
   assert LastSeasonSkaterBuilder.build( [], [ other ], [] ) == LastSeasonGroup( [], [] )


def Test_Build_TestZeroGames_ExpectOmitted() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl = _nhl( 1, list( Team )[ Position.FIRST ], 40.0, 50.0, 0 )
   other = _other( 2, 20.0, 30.0, league, 0 )
   assert LastSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] ) == LastSeasonGroup(
      [],
      [] )


def Test_Build_TestNhlAndOtherOnlyPlayers_ExpectBothRows() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   team = list( Team )[ Position.FIRST ]
   nhl = _nhl( 1, team, 40.0, 50.0 )
   other = _other( 2, 20.0, 30.0, league, 46 )
   pace, games = TranslatedPaceAverager.year( None, [ other ], [ factor ] )
   group = LastSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] )
   assert group == LastSeasonGroup(
      [
         LastSeasonNhlSkater(
            nhl.player_id,
            float( nhl.games_played ),
            CareerPace( nhl.g_pace, nhl.a_pace ),
            nhl.team )
      ],
      [ LastSeasonSkater( other.player_id, games, pace ) ] )
