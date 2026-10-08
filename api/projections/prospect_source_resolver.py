from __future__ import annotations

from ..recency.prior_year import PriorYear
from ..season import Season
from ..skaters.club_league import ClubLeague
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason


class ProspectSourceResolver():
   MAX_SOURCE_AGE = 23
   DEFAULT_MAX_GAP = 1


   @classmethod
   def usable( cls, row: SkaterSeason, target_season_id: int ) -> bool:
      return (
         isinstance( row, OtherLeagueSkaterSeason ) and ClubLeague.contains( row.league )
         and row.season_id < target_season_id and row.games_played >= PriorYear.MIN_GAMES
         and row.age <= cls.MAX_SOURCE_AGE )


   @classmethod
   def latest(
         cls,
         seasons: list[ SkaterSeason ],
         target_season_id: int,
         max_gap: int = DEFAULT_MAX_GAP,
         *,
         supported_leagues: set[ str ] ) -> OtherLeagueSkaterSeason | None:
      sources = [
         row for row in seasons
         if isinstance( row, OtherLeagueSkaterSeason ) and cls.usable( row, target_season_id )
         and 1 <= Season.start_year( target_season_id ) - Season.start_year( row.season_id ) <= max_gap
         and row.league in supported_leagues
      ]
      return min( sources, key=lambda row: ( -row.season_id, -row.games_played, row.league ), default=None )
