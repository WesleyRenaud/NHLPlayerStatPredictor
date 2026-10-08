from __future__ import annotations

from ..aging.league_factor import LeagueFactor
from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .scoring_component_shares import ScoringComponentShares
from .scoring_paces import ScoringPaces
from .scoring_stat import ScoringStat
from .season_pace import SeasonPace
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason
from .year_pace import YearPace


class TranslatedPaceAverager():
   @classmethod
   def year(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         component_shares: list[ ScoringComponentShares ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None ) -> YearPace | None:
      games = 0
      weighted_paces_by_stat = { stat: 0.0 for stat in ScoringStat }
      nhl_games = 0
      penalty_minutes = 0.0
      shots = 0.0

      for season in seasons:
         if not season.games_played:
            continue

         scoring = cls._scoring_paces( season, factors, component_shares )

         if scoring is None:
            continue

         games += season.games_played
         scale = (
            next( ( scale.multiplier for scale in player_ice_scales
               if scale.player_id == season.player_id and scale.season_id == season.season_id ), 1.0 )
            if player_ice_scales is not None and isinstance( season, NhlSkaterSeason ) else 1.0 )
         for stat in ScoringStat:
            weighted_paces_by_stat[ stat ] += season.games_played * getattr( scoring, stat.value ) * scale

         if isinstance( season, NhlSkaterSeason ):
            nhl_games += season.games_played
            penalty_minutes += season.games_played * season.penalty_minutes_pace() * scale
            shots += season.games_played * season.shots_pace() * scale

      if not games:
         return None

      return YearPace(
         scoring=ScoringPaces( **{
            stat.value: weighted_pace / games
            for stat, weighted_pace in weighted_paces_by_stat.items()
         } ),
         penalty_minutes=None if not nhl_games else penalty_minutes / nhl_games,
         games=games,
         nhl_games=nhl_games,
         shots=None if not nhl_games else shots / nhl_games )


   @classmethod
   def totals(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ] ) -> SeasonPace | None:
      games = 0
      weighted_goals = 0.0
      weighted_assists = 0.0

      for season in seasons:
         if not season.games_played:
            continue

         total_pace = (
            season.nhl_pace( factors ) if isinstance( season, OtherLeagueSkaterSeason )
            else SeasonPace( season.g_pace, season.a_pace ) )

         if total_pace is None:
            continue

         games += season.games_played
         weighted_goals += season.games_played * total_pace.goals
         weighted_assists += season.games_played * total_pace.assists

      if not games:
         return None

      return SeasonPace( weighted_goals / games, weighted_assists / games )


   @classmethod
   def _scoring_paces(
         cls,
         season: NhlSkaterSeason | OtherLeagueSkaterSeason,
         factors: list[ LeagueFactor ],
         component_shares: list[ ScoringComponentShares ] ) -> ScoringPaces | None:
      if isinstance( season, NhlSkaterSeason ):
         return season.scoring_paces()

      translated_totals = season.nhl_pace( factors )

      if translated_totals is None:
         return None

      shares = min( component_shares, key=lambda item: abs( item.age - season.age ) )
      return shares.split( translated_totals.goals, translated_totals.assists )
