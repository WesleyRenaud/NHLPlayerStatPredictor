from __future__ import annotations

from collections import defaultdict

from .aging_factor import AgingFactor
from .league_factor import LeagueFactor
from .other_league_season import OtherLeagueSeason
from .season import Season
from .skater_season import SkaterSeason


class LeagueFactorFitter():
   @classmethod
   def fit(
         cls,
         nhl_seasons: list[ SkaterSeason ],
         other_seasons: list[ OtherLeagueSeason ],
         aging_factors: list[ AgingFactor ] ) -> list[ LeagueFactor ]:
      nhl_goals, nhl_assists, other_goals, other_assists = cls._paces(
         nhl_seasons,
         other_seasons,
         aging_factors )
      return cls._factors( nhl_goals, nhl_assists, other_goals, other_assists )


   @classmethod
   def _paces(
         cls,
         nhl_seasons: list[ SkaterSeason ],
         other_seasons: list[ OtherLeagueSeason ],
         aging_factors: list[ AgingFactor ] ) -> tuple[
            dict[ str, float ],
            dict[ str, float ],
            dict[ str, float ],
            dict[ str, float ] ]:
      nhl_by_player = cls._nhl_by_player_year( nhl_seasons )
      nhl_goals: dict[ str, float ] = defaultdict( float )
      nhl_assists: dict[ str, float ] = defaultdict( float )
      other_goals: dict[ str, float ] = defaultdict( float )
      other_assists: dict[ str, float ] = defaultdict( float )

      for other_season in other_seasons:
         nhl_season = cls._nhl_for(
            other_season,
            nhl_by_player.get( other_season.player_id, {} ) )

         if nhl_season is None:
            continue

         same_age_other_pace = cls._same_age_pace(
            other_season,
            nhl_season,
            aging_factors )

         if same_age_other_pace is None:
            continue

         same_age_goals, same_age_assists = same_age_other_pace
         nhl_goals[ other_season.league ] += nhl_season.g_pace
         nhl_assists[ other_season.league ] += nhl_season.a_pace
         other_goals[ other_season.league ] += same_age_goals
         other_assists[ other_season.league ] += same_age_assists

      return nhl_goals, nhl_assists, other_goals, other_assists


   @classmethod
   def _factors(
         cls,
         nhl_goals: dict[ str, float ],
         nhl_assists: dict[ str, float ],
         other_goals: dict[ str, float ],
         other_assists: dict[ str, float ] ) -> list[ LeagueFactor ]:
      return [
         LeagueFactor(
            league=league,
            goals=nhl_goals[ league ] / other_goals[ league ],
            assists=nhl_assists[ league ] / other_assists[ league ] )
         for league in sorted( nhl_goals )
         if cls._has_pace(
            nhl_goals[ league ],
            nhl_assists[ league ],
            other_goals[ league ],
            other_assists[ league ] )
      ]


   @classmethod
   def _has_pace(
         cls,
         nhl_goals: float,
         nhl_assists: float,
         other_goals: float,
         other_assists: float ) -> bool:
      return bool( nhl_goals and nhl_assists and other_goals and other_assists )


   @classmethod
   def _nhl_for(
         cls,
         other: OtherLeagueSeason,
         nhl_years: dict[ int, SkaterSeason ] ) -> SkaterSeason | None:
      year = Season.start_year( other.season_id )
      same_year = nhl_years.get( year )

      if same_year is not None:
         return same_year

      following = nhl_years.get( year + 1 )

      if following is not None:
         return following

      return nhl_years.get( year - 1 )


   @classmethod
   def _same_age_pace(
         cls,
         other: OtherLeagueSeason,
         nhl: SkaterSeason,
         aging_factors: list[ AgingFactor ] ) -> tuple[ float, float ] | None:
      if Season.start_year( other.season_id ) == Season.start_year( nhl.season_id ):
         return other.g_pace, other.a_pace

      return cls._age_to(
         other.g_pace,
         other.a_pace,
         int( other.age ),
         int( nhl.age ),
         aging_factors )


   @classmethod
   def _age_to(
         cls,
         goals: float,
         assists: float,
         from_age: int,
         to_age: int,
         aging_factors: list[ AgingFactor ] ) -> tuple[ float, float ] | None:
      if from_age == to_age:
         return goals, assists

      by_age = { factor.age: factor for factor in aging_factors }

      if to_age > from_age:
         return cls._grow( goals, assists, from_age, to_age, by_age )

      return cls._shrink( goals, assists, from_age, to_age, by_age )


   @classmethod
   def _grow(
         cls,
         goals: float,
         assists: float,
         from_age: int,
         to_age: int,
         by_age: dict[ int, AgingFactor ] ) -> tuple[ float, float ] | None:
      for age in range( from_age, to_age ):
         rates = cls._rates( by_age.get( age ) )

         if rates is None:
            return None

         goal_rate, assist_rate = rates
         goals *= goal_rate
         assists *= assist_rate

      return goals, assists


   @classmethod
   def _shrink(
         cls,
         goals: float,
         assists: float,
         from_age: int,
         to_age: int,
         by_age: dict[ int, AgingFactor ] ) -> tuple[ float, float ] | None:
      for age in range( to_age, from_age ):
         rates = cls._rates( by_age.get( age ) )

         if rates is None:
            return None

         goal_rate, assist_rate = rates
         goals /= goal_rate
         assists /= assist_rate

      return goals, assists


   @classmethod
   def _rates(
         cls,
         factor: AgingFactor | None ) -> tuple[ float, float ] | None:
      if factor is None:
         return None

      goals = 1.0 + factor.goals
      assists = 1.0 + factor.assists

      if goals == 0.0 or assists == 0.0:
         return None

      return goals, assists


   @classmethod
   def _nhl_by_player_year(
         cls,
         seasons: list[ SkaterSeason ] ) -> dict[ int, dict[ int, SkaterSeason ] ]:
      by_player: dict[ int, dict[ int, SkaterSeason ] ] = {}

      for season in seasons:
         years = by_player.setdefault( season.player_id, {} )
         years[ Season.start_year( season.season_id ) ] = season

      return by_player
