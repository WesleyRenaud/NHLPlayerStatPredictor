from __future__ import annotations

from datetime import date

from api.aging.league_factor import LeagueFactor
from api.projections.season_pace import SeasonPace
from api.projections.season_pace_averager import SeasonPaceAverager
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=games_played,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Average_TestNhlOnly_ExpectMatchesSeasonPaceAverager() -> None:
   later = _nhl( 10.0, 20.0, 20222023 )
   earlier = _nhl( 40.0, 50.0, 20212022 )
   target_season_id = 20232024
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   seasons = [ later, earlier ]
   assert TranslatedPaceAverager.average(
      seasons, weights, target_season_id, [] ) == SeasonPaceAverager.average(
      seasons, weights, target_season_id )


def Test_Average_TestMixedYear_ExpectGamesWeightedBlend() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl_games = 1
   other_games = 46
   nhl = _nhl( 84.0, 84.0, 20252026, nhl_games )
   other = _other( 10.96, 23.74, 20252026, league, other_games )
   weights = [ RecencyWeight( 0, 1.0 ) ]
   pace = TranslatedPaceAverager.average(
      [ nhl, other ], weights, 20262027, [ factor ] )
   total_games = nhl_games + other_games
   weight = total_games / (
      total_games + TranslatedPaceAverager.GAMES_SCALE )
   goals = (
      nhl_games * nhl.g_pace
      + other_games * other.g_pace * factor.rate ) / total_games
   assists = (
      nhl_games * nhl.a_pace
      + other_games * other.a_pace * factor.rate ) / total_games
   assert pace == SeasonPace(
      goals * weight / weight,
      assists * weight / weight )


def Test_Average_TestMissingLeague_ExpectNhlOnly() -> None:
   nhl = _nhl( 20.0, 30.0, 20252026, 10 )
   other = _other( 100.0, 100.0, 20252026, 'AAA', 50 )
   weights = [ RecencyWeight( 0, 1.0 ) ]
   assert TranslatedPaceAverager.average(
      [ nhl, other ], weights, 20262027, [] ) == SeasonPace(
      nhl.g_pace, nhl.a_pace )


def Test_Average_TestNoUsableYears_ExpectNone() -> None:
   weights = [ RecencyWeight( 0, 1.0 ) ]
   assert TranslatedPaceAverager.average(
      [], weights, 20262027, [] ) is None


def Test_Average_TestOtherOnlyYear_ExpectTranslatedPace() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.30 )
   other = _other( 40.0, 80.0, 20242025, league, 52 )
   weights = [ RecencyWeight( 0, 1.0 ), RecencyWeight( 1, 1.0 ) ]
   pace = TranslatedPaceAverager.average(
      [ other ], weights, 20262027, [ factor ] )
   assert pace == SeasonPace(
      other.g_pace * factor.rate,
      other.a_pace * factor.rate )


def Test_Average_TestShortSeason_ExpectReliabilityWeighted() -> None:
   later_games = 1
   earlier_games = 82
   later = _nhl( 84.0, 84.0, 20222023, later_games )
   earlier = _nhl( 10.0, 20.0, 20212022, earlier_games )
   target_season_id = 20232024
   later_recency = 0.75
   earlier_recency = 0.25
   weights = [ RecencyWeight( 0, later_recency ), RecencyWeight( 1, earlier_recency ) ]
   later_weight = later_recency * (
      float( later_games )
      / ( float( later_games ) + TranslatedPaceAverager.GAMES_SCALE ) )
   earlier_weight = earlier_recency * (
      float( earlier_games )
      / ( float( earlier_games ) + TranslatedPaceAverager.GAMES_SCALE ) )
   total = later_weight + earlier_weight
   pace = TranslatedPaceAverager.average(
      [ later, earlier ], weights, target_season_id, [] )
   assert pace == SeasonPace(
      ( later.g_pace * later_weight + earlier.g_pace * earlier_weight ) / total,
      ( later.a_pace * later_weight + earlier.a_pace * earlier_weight ) / total )


def Test_Average_TestShortNhlWithOtherYear_ExpectYearGamesReliability() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl_games = 1
   other_games = 46
   earlier_games = 82
   later_nhl = _nhl( 84.0, 84.0, 20222023, nhl_games )
   later_other = _other( 10.96, 23.74, 20222023, league, other_games )
   earlier = _nhl( 10.0, 20.0, 20212022, earlier_games )
   later_recency = 0.75
   earlier_recency = 0.25
   later_games = float( nhl_games + other_games )
   later_pace = SeasonPace(
      (
         nhl_games * later_nhl.g_pace
         + other_games * later_other.g_pace * factor.rate ) / later_games,
      (
         nhl_games * later_nhl.a_pace
         + other_games * later_other.a_pace * factor.rate ) / later_games )
   later_weight = later_recency * (
      later_games / ( later_games + TranslatedPaceAverager.GAMES_SCALE ) )
   earlier_weight = earlier_recency * (
      float( earlier_games )
      / ( float( earlier_games ) + TranslatedPaceAverager.GAMES_SCALE ) )
   total = later_weight + earlier_weight
   pace = TranslatedPaceAverager.average(
      [ later_nhl, later_other, earlier ],
      [ RecencyWeight( 0, later_recency ), RecencyWeight( 1, earlier_recency ) ],
      20232024,
      [ factor ] )
   assert pace == SeasonPace(
      ( later_pace.goals * later_weight + earlier.g_pace * earlier_weight ) / total,
      ( later_pace.assists * later_weight + earlier.a_pace * earlier_weight ) / total )


def Test_Year_TestMixedNhlAndOther_ExpectGamesWeightedBlend() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl_games = 1
   other_games = 46
   nhl = _nhl( 84.0, 84.0, 20252026, nhl_games )
   other = _other( 10.96, 23.74, 20252026, league, other_games )
   year = TranslatedPaceAverager.year( [ nhl, other ], [ factor ] )
   total_games = nhl_games + other_games
   assert year.games == total_games
   assert year.pace == SeasonPace(
      ( nhl_games * nhl.g_pace + other_games * other.g_pace * factor.rate )
      / total_games,
      ( nhl_games * nhl.a_pace + other_games * other.a_pace * factor.rate )
      / total_games )


def Test_Year_TestNoGames_ExpectNone() -> None:
   assert TranslatedPaceAverager.year( [], [] ) is None
