from __future__ import annotations

from datetime import date

import pytest

from api.recency.current_season_weight import CurrentSeasonWeight
from api.recency.current_season_weight_fitter import CurrentSeasonWeightFitter
from api.recency.prior_year import PriorYear
from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_game import SkaterGame
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


_PLAYERS = ProductionCoefficientFitter.MIN_SUPPORT
_PRIOR_SEASON = 20232024
_CURRENT_SEASON = 20242025


def _interval( games_played: int, season_games: int ) -> int:
   return CurrentSeasonWeightFitter._interval( games_played, season_games )


def _season_share( interval: int ) -> float:
   return CurrentSeasonWeightFitter._season_share( interval )


def _games( points: list[ int ] ) -> list[ SkaterGame ]:
   return [
      SkaterGame( game_number, scored )
      for game_number, scored in enumerate( points, start=1 )
   ]


def _season( player_id: int, season_id: int, points: list[ int ] ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28,
      team=list( Team )[ Position.FIRST ],
      games_played=len( points ),
      goals=0,
      assists=0,
      points=sum( points ),
      schedule_games=len( points ),
      pace_games=len( points ),
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      penalty_minutes=0,
      gp_share=None,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      even_strength_goals=0,
      even_strength_points=0,
      shots=0,
      games=_games( points ) )


def _paired( early_points: list[ int ], late_points: list[ int ] ) -> list[ NhlSkaterSeason ]:
   current_points = early_points + late_points
   seasons: list[ NhlSkaterSeason ] = []

   for player_id in range( _PLAYERS ):
      seasons.append( _season( player_id, _PRIOR_SEASON, [ 0 ] * PriorYear.MIN_GAMES ) )
      seasons.append( _season( player_id, _CURRENT_SEASON, current_points ) )

   return seasons


def _two_types( high_points: list[ int ], low_points: list[ int ] ) -> list[ NhlSkaterSeason ]:
   seasons: list[ NhlSkaterSeason ] = []
   players_of_each_type = _PLAYERS // 2

   for player_id in range( _PLAYERS ):
      points = high_points if player_id < players_of_each_type else low_points
      seasons.append( _season( player_id, _PRIOR_SEASON, [ 0 ] * PriorYear.MIN_GAMES ) )
      seasons.append( _season( player_id, _CURRENT_SEASON, points ) )

   return seasons


def _bounded( share: float ) -> float:
   return min( 1.0, max( 0.0, share ) )


def _prefix_moments(
      point_lists: list[ list[ int ] ],
      players_per_list: list[ int ],
      games_played: int ) -> tuple[ float, float ]:
   season_length = len( point_lists[ 0 ] )
   numerator = 0.0
   denominator = 0.0

   for players, points in zip( players_per_list, point_lists ):
      current_pace = sum( points[ :games_played ] ) / games_played
      season_pace = sum( points ) / season_length
      numerator += players * season_pace * current_pace
      denominator += players * current_pace * current_pace

   return numerator, denominator


def _interval_weights(
      point_lists: list[ list[ int ] ],
      players_per_list: list[ int ] ) -> list[ CurrentSeasonWeight ]:
   season_length = len( point_lists[ 0 ] )
   numerator_by_interval: dict[ int, float ] = {}
   denominator_by_interval: dict[ int, float ] = {}

   for games_played in range( 1, season_length + 1 ):
      numerator, denominator = _prefix_moments( point_lists, players_per_list, games_played )
      interval = _interval( games_played, season_length )
      numerator_by_interval[ interval ] = numerator_by_interval.get( interval, 0.0 ) + numerator
      denominator_by_interval[ interval ] = (
         denominator_by_interval.get( interval, 0.0 ) + denominator )

   carried = _bounded(
      numerator_by_interval[ min( numerator_by_interval ) ]
      / denominator_by_interval[ min( denominator_by_interval ) ] )
   weights: list[ CurrentSeasonWeight ] = []

   for interval in range( 1, CurrentSeasonWeightFitter._intervals() + 1 ):
      if interval in numerator_by_interval:
         carried = _bounded(
            numerator_by_interval[ interval ] / denominator_by_interval[ interval ] )

      weights.append( CurrentSeasonWeight( _season_share( interval ), carried ) )

   return weights


def Test_Fit_TestNoGames_ExpectNoWeights() -> None:
   assert CurrentSeasonWeightFitter.fit( [] ) == []


def Test_Fit_TestSeasonMatchesOpening_ExpectFullWeight() -> None:
   early_points = [ 1 ] * 5
   late_points = [ 1 ] * PriorYear.MIN_GAMES
   season_points = early_points + late_points
   season_pace = sum( season_points ) / len( season_points )
   opening_pace = sum( early_points ) / len( early_points )
   share = ( season_pace - 0.0 ) * ( opening_pace - 0.0 ) / ( opening_pace - 0.0 ) ** 2

   fitted = CurrentSeasonWeightFitter.fit( _paired( early_points, late_points ) )

   assert share == 1.0
   assert fitted == [
      CurrentSeasonWeight( _season_share( interval ), 1.0 )
      for interval in range( 1, CurrentSeasonWeightFitter._intervals() + 1 )
   ]


def Test_Fit_TestSplitScoring_ExpectFullSeasonWeight() -> None:
   matching_points = [ 1 ] + [ 1 ] * PriorYear.MIN_GAMES
   quiet_points = [ 1 ] + [ 0 ] * PriorYear.MIN_GAMES
   matching_players = _PLAYERS // 2
   quiet_players = _PLAYERS - matching_players
   expected = _interval_weights(
      [ matching_points, quiet_points ],
      [ matching_players, quiet_players ] )

   fitted = CurrentSeasonWeightFitter.fit( _two_types( matching_points, quiet_points ) )

   assert [ weight.season_share for weight in fitted ] == [
      weight.season_share for weight in expected ]
   assert [ weight.weight for weight in fitted ] == pytest.approx( [
      weight.weight for weight in expected ] )


def Test_Fit_TestSeasonAboveOpening_ExpectWeightCappedAtOne() -> None:
   early_points = [ 1 ]
   late_points = [ 2 ] * PriorYear.MIN_GAMES
   season_points = early_points + late_points
   season_pace = sum( season_points ) / len( season_points )
   opening_pace = sum( early_points ) / len( early_points )
   opening_share = season_pace / opening_pace
   expected = _interval_weights( [ season_points ], [ _PLAYERS ] )

   fitted = CurrentSeasonWeightFitter.fit( _paired( early_points, late_points ) )

   assert opening_share > 1.0
   assert fitted == expected


def Test_Fit_TestShortPriorSeason_ExpectNoWeights() -> None:
   assert CurrentSeasonWeightFitter.fit( [
      _season( 1, _PRIOR_SEASON, [ 0 ] * ( PriorYear.MIN_GAMES - 1 ) ),
      _season( 1, _CURRENT_SEASON, [ 1 ] * ( PriorYear.MIN_GAMES + 5 ) ),
   ] ) == []


def Test_Fit_TestSkippedSeason_ExpectNoWeights() -> None:
   assert CurrentSeasonWeightFitter.fit( [
      _season( 1, 20222023, [ 0 ] * PriorYear.MIN_GAMES ),
      _season( 1, _CURRENT_SEASON, [ 1 ] * ( PriorYear.MIN_GAMES + 5 ) ),
   ] ) == []


def Test_Fit_TestLaterCountLower_ExpectEarlierWeightHeld() -> None:
   played_games = PriorYear.MIN_GAMES - 2
   opening_points = [ 0, 3 ] + [ 0 ] * played_games
   steady_points = [ 1, 0 ] + [ 2 ] * played_games
   players = _PLAYERS // 2
   point_lists = [ opening_points, steady_points ]
   player_counts = [ players, players ]
   numerator_at_one, denominator_at_one = _prefix_moments( point_lists, player_counts, 1 )
   numerator_at_two, denominator_at_two = _prefix_moments( point_lists, player_counts, 2 )
   weight_at_one = _bounded( numerator_at_one / denominator_at_one )
   weight_at_two = _bounded( numerator_at_two / denominator_at_two )
   pooled = (
      weight_at_one * denominator_at_one + weight_at_two * denominator_at_two
   ) / ( denominator_at_one + denominator_at_two )
   later = _interval_weights( point_lists, player_counts )

   fitted = CurrentSeasonWeightFitter.fit( _two_types( opening_points, steady_points ) )

   assert _interval( 1, len( opening_points ) ) == 1
   assert _interval( 2, len( opening_points ) ) == 2
   assert weight_at_one > weight_at_two
   assert later[ 2 ].weight >= pooled
   assert fitted[ :2 ] == [
      CurrentSeasonWeight( _season_share( 1 ), pooled ),
      CurrentSeasonWeight( _season_share( 2 ), pooled ),
   ]
   assert fitted[ 2: ] == later[ 2: ]


def Test_Fit_TestOpeningSlice_ExpectFirstGamesShareOneWeight() -> None:
   season_games = PriorYear.MIN_GAMES * 2
   opening_points = [ 1 ] + [ 0 ] * ( season_games - 1 )
   steady_points = [ 1 ] * season_games
   players = _PLAYERS // 2
   point_lists = [ opening_points, steady_points ]
   player_counts = [ players, players ]
   numerator_at_one, denominator_at_one = _prefix_moments( point_lists, player_counts, 1 )
   numerator_at_two, denominator_at_two = _prefix_moments( point_lists, player_counts, 2 )
   opening_only = _bounded( numerator_at_one / denominator_at_one )
   pooled = _bounded(
      ( numerator_at_one + numerator_at_two ) / ( denominator_at_one + denominator_at_two ) )

   fitted = CurrentSeasonWeightFitter.fit( _two_types( opening_points, steady_points ) )

   assert _interval( 1, season_games ) == 1
   assert _interval( 2, season_games ) == 1
   assert _interval( 3, season_games ) == 2
   assert opening_only != pooled
   assert fitted[ 0 ] == CurrentSeasonWeight( _season_share( 1 ), pooled )
   assert fitted[ -1 ].season_share == _season_share( CurrentSeasonWeightFitter._intervals() )
