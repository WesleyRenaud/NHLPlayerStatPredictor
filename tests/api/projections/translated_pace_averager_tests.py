from __future__ import annotations

from datetime import date

from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.projections.career_pace import CareerPace
from api.projections.career_pace_averager import CareerPaceAverager
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _nhl(
      g_pace: float,
      a_pace: float,
      season_id: int,
      games_played: int = 82 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      goals=int( g_pace ),
      assists=int( a_pace ),
      points=int( g_pace + a_pace ),
      schedule_games=82,
      pace_games=82,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def _other(
      g_pace: float,
      a_pace: float,
      season_id: int,
      league: str,
      games_played: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=season_id,
      league=league,
      age=20.8,
      games_played=games_played,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Average_TestNhlOnly_ExpectMatchesCareerPaceAverager() -> None:
   later = _nhl( 10.0, 20.0, 20222023 )
   earlier = _nhl( 40.0, 50.0, 20212022 )
   target_season_id = 20232024
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   seasons = [ later, earlier ]
   assert TranslatedPaceAverager.average(
      seasons, [], weights, target_season_id, [] ) == CareerPaceAverager.average(
      seasons, weights, target_season_id )


def Test_Average_TestMixedYear_ExpectGamesWeightedBlend() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40, 0.50 )
   nhl_games = 1
   other_games = 46
   nhl = _nhl( 84.0, 84.0, 20252026, nhl_games )
   other = _other( 10.96, 23.74, 20252026, league, other_games )
   weights = [ RecencyWeight( 0, 1.0 ) ]
   pace = TranslatedPaceAverager.average(
      [ nhl ], [ other ], weights, 20262027, [ factor ] )
   total_games = float( nhl_games + other_games )
   assert pace == CareerPace(
      (
         nhl_games * nhl.g_pace
         + other_games * other.g_pace * factor.goals ) / total_games,
      (
         nhl_games * nhl.a_pace
         + other_games * other.a_pace * factor.assists ) / total_games )


def Test_Average_TestMissingLeague_ExpectNhlOnly() -> None:
   nhl = _nhl( 20.0, 30.0, 20252026, 10 )
   other = _other( 100.0, 100.0, 20252026, 'AAA', 50 )
   weights = [ RecencyWeight( 0, 1.0 ) ]
   assert TranslatedPaceAverager.average(
      [ nhl ], [ other ], weights, 20262027, [] ) == CareerPace(
      nhl.g_pace, nhl.a_pace )


def Test_Average_TestOtherOnlyYear_ExpectTranslatedPace() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.30, 0.25 )
   other = _other( 40.0, 80.0, 20242025, league, 52 )
   weights = [ RecencyWeight( 0, 1.0 ), RecencyWeight( 1, 1.0 ) ]
   pace = TranslatedPaceAverager.average(
      [], [ other ], weights, 20262027, [ factor ] )
   assert pace == CareerPace(
      other.g_pace * factor.goals,
      other.a_pace * factor.assists )
