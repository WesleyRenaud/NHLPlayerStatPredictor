from __future__ import annotations

from datetime import date

from api.aging.league_factor import LeagueFactor
from api.projections.previous_season_group import PreviousSeasonGroup
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.previous_season_skater import PreviousSeasonSkater
from api.projections.previous_season_skater_builder import PreviousSeasonSkaterBuilder
from api.projections.season_pace import SeasonPace
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
      position=SkaterPosition( 'C' ),
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
   group = PreviousSeasonSkaterBuilder.build( [ nhl ], [], [] )
   assert group == PreviousSeasonGroup(
      [
         PreviousSeasonNhlSkater(
            nhl.player_id,
            nhl.games_played,
            SeasonPace( nhl.g_pace, nhl.a_pace ),
            nhl.position,
            nhl.team )
      ],
      [] )


def Test_Build_TestOtherLeagueOnly_ExpectTranslatedPaceWithoutNhlTeam() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   other = _other( 7, 20.0, 30.0, league, 46 )
   year = TranslatedPaceAverager.year( [ other ], [ factor ] )
   group = PreviousSeasonSkaterBuilder.build( [], [ other ], [ factor ] )
   assert group == PreviousSeasonGroup(
      [],
      [ PreviousSeasonSkater( other.player_id, year.games, year.pace, other.position ) ] )


def Test_Build_TestNhlAndOther_ExpectBlendedPaceAndNhlTeam() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   team = list( Team )[ Position.SECOND ]
   nhl = _nhl( 7, team, 84.0, 84.0, 1 )
   other = _other( 7, 10.96, 23.74, league, 46 )
   year = TranslatedPaceAverager.year( [ nhl, other ], [ factor ] )
   group = PreviousSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] )
   assert group == PreviousSeasonGroup(
      [ PreviousSeasonNhlSkater(
         nhl.player_id,
         year.games,
         year.pace,
         nhl.position,
         nhl.team ) ],
      [] )


def Test_Build_TestUnknownLeague_ExpectOmitted() -> None:
   other = _other( 7, 20.0, 30.0, 'AAA', 46 )
   assert PreviousSeasonSkaterBuilder.build( [], [ other ], [] ) == PreviousSeasonGroup( [], [] )


def Test_Build_TestZeroGames_ExpectOmitted() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl = _nhl( 1, list( Team )[ Position.FIRST ], 40.0, 50.0, 0 )
   other = _other( 2, 20.0, 30.0, league, 0 )
   assert PreviousSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] ) == PreviousSeasonGroup(
      [],
      [] )


def Test_Build_TestNhlAndOtherOnlyPlayers_ExpectBothRows() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   team = list( Team )[ Position.FIRST ]
   nhl = _nhl( 1, team, 40.0, 50.0 )
   other = _other( 2, 20.0, 30.0, league, 46 )
   year = TranslatedPaceAverager.year( [ other ], [ factor ] )
   group = PreviousSeasonSkaterBuilder.build( [ nhl ], [ other ], [ factor ] )
   assert group == PreviousSeasonGroup(
      [
         PreviousSeasonNhlSkater(
            nhl.player_id,
            nhl.games_played,
            SeasonPace( nhl.g_pace, nhl.a_pace ),
            nhl.position,
            nhl.team )
      ],
      [ PreviousSeasonSkater( other.player_id, year.games, year.pace, other.position ) ] )
