from __future__ import annotations

from collections import defaultdict
import math

from .current_season_block_moments import CurrentSeasonBlockMoments
from .current_season_weight import CurrentSeasonWeight
from .current_season_weight_block import CurrentSeasonWeightBlock
from .prior_year import PriorYear
from .production_coefficient_fitter import ProductionCoefficientFitter
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class CurrentSeasonWeightFitter():
   """How much the full season follows the points per game so far.

   Each weight covers one block of the season. Every pace through a game in
   that block is one case, and a later block never receives a smaller weight.
   """

   BLOCK_PERCENT = 5

   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ CurrentSeasonWeight ]:
      if not seasons:
         return []

      moments = cls._moments( seasons )
      rows = [
         block
         for block in moments
         if block.samples >= ProductionCoefficientFitter.MIN_SUPPORT and block.denominator != 0.0
      ]

      return cls._fill( cls._nondecreasing( rows ) )


   @classmethod
   def _moments(
         cls,
         seasons: list[ NhlSkaterSeason ] ) -> list[ CurrentSeasonBlockMoments ]:
      by_player: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_player[ season.player_id ].append( season )

      moments = [
         CurrentSeasonBlockMoments( interval, 0, 0.0, 0.0 )
         for interval in range( 1, cls._intervals() + 1 )
      ]

      for player_seasons in by_player.values():
         for season in player_seasons:
            cls._add_season( moments, season, cls._prior_season( player_seasons, season ) )

      return moments


   @classmethod
   def _prior_season(
         cls,
         seasons: list[ NhlSkaterSeason ],
         season: NhlSkaterSeason ) -> NhlSkaterSeason | None:
      start_year = Season.start_year( season.season_id )
      prior = [
         candidate
         for candidate in seasons
         if Season.start_year( candidate.season_id ) == start_year - 1
      ]

      if not prior:
         return None

      return prior[ Position.FIRST ]


   @classmethod
   def _add_season(
         cls,
         moments: list[ CurrentSeasonBlockMoments ],
         season: NhlSkaterSeason,
         prior: NhlSkaterSeason | None ) -> None:
      if prior is None:
         return

      current = cls._points( season )
      previous = cls._points( prior )

      if len( previous ) < PriorYear.MIN_GAMES or len( current ) < PriorYear.MIN_GAMES:
         return

      prior_pace = cls._pace( previous )
      season_pace = cls._pace( current )
      season_gap = season_pace - prior_pace
      total = 0

      for counted, points in enumerate( current, start=1 ):
         total += points
         interval = cls._interval( counted, season.schedule_games )
         current_pace = total / counted
         gap = current_pace - prior_pace
         moments[ interval + Position.LAST ] = moments[ interval + Position.LAST ].adding(
            gap,
            season_gap )


   @classmethod
   def _intervals( cls ) -> int:
      return 100 // cls.BLOCK_PERCENT


   @classmethod
   def _interval( cls, games_played: int, season_games: int ) -> int:
      share = games_played / season_games

      if share > 1.0:
         share = 1.0

      interval = math.ceil( share * cls._intervals() )

      if interval > cls._intervals():
         return cls._intervals()

      return interval


   @classmethod
   def _season_share( cls, interval: int ) -> float:
      return interval * cls.BLOCK_PERCENT / 100


   @classmethod
   def _points( cls, season: NhlSkaterSeason ) -> list[ int ]:
      ordered = sorted( season.games, key=lambda game: game.game_number )
      return [ game.points for game in ordered ][ :season.schedule_games ]


   @classmethod
   def _pace( cls, points: list[ int ] ) -> float:
      return sum( points ) / len( points )


   @classmethod
   def _nondecreasing(
         cls,
         rows: list[ CurrentSeasonBlockMoments ] ) -> list[ CurrentSeasonWeightBlock ]:
      blocks: list[ CurrentSeasonWeightBlock ] = []

      for row in rows:
         blocks.append( CurrentSeasonWeightBlock.from_moments( row ) )

         while len( blocks ) > Position.SECOND:
            latest = blocks[ Position.LAST ]
            earlier = blocks[ Position.SECOND_LAST ]

            if latest.weight() >= earlier.weight():
               break

            blocks.pop()
            blocks[ Position.LAST ] = earlier.merging( latest )

      return blocks


   @classmethod
   def _fill( cls, blocks: list[ CurrentSeasonWeightBlock ] ) -> list[ CurrentSeasonWeight ]:
      if not blocks:
         return []

      known = {
         interval: block.weight()
         for block in blocks
         for interval in block.intervals
      }
      carried = blocks[ Position.FIRST ].weight()
      filled: list[ CurrentSeasonWeight ] = []

      for interval in range( 1, cls._intervals() + 1 ):
         if interval in known:
            carried = known[ interval ]

         filled.append( CurrentSeasonWeight( cls._season_share( interval ), carried ) )

      return filled
