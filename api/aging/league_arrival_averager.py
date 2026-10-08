from __future__ import annotations

from .league_arrival import LeagueArrival
from .league_factor import LeagueFactor
from ..projections.scoring_component_shares import ScoringComponentShares
from ..projections.scoring_paces import ScoringPaces
from ..projections.weighted_scoring import WeightedScoring
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason


class LeagueArrivalAverager():
   @classmethod
   def scoring(
         cls,
         seasons: list[ SkaterSeason ],
         factors: list[ LeagueFactor ],
         arrivals: list[ LeagueArrival ],
         component_shares: list[ ScoringComponentShares ],
         age_step: float ) -> ScoringPaces | None:
      if not component_shares or age_step <= 0.0:
         return None

      other_league = [
         season for season in seasons
         if isinstance( season, OtherLeagueSkaterSeason )
      ]
      arrived = [
         season for season in other_league
         if season.games_played
         and LeagueArrival.rate( arrivals, season.league, season.age ) is not None
      ]

      if not arrived:
         return None

      weighted = WeightedScoring.empty()

      for season in [ season for season in seasons if isinstance( season, NhlSkaterSeason ) ]:
         weighted = weighted.adding( season.games_played, cls._nhl( season, age_step ) )

      for season in other_league:
         weighted = weighted.adding(
            season.games_played,
            cls._other_league( season, factors, arrivals, component_shares, age_step ) )

      return weighted.per_game()


   @classmethod
   def _nhl( cls, season: NhlSkaterSeason, age_step: float ) -> ScoringPaces | None:
      if not season.games_played:
         return None

      return season.scoring_paces().scaled( age_step )


   @classmethod
   def _other_league(
         cls,
         season: OtherLeagueSkaterSeason,
         factors: list[ LeagueFactor ],
         arrivals: list[ LeagueArrival ],
         component_shares: list[ ScoringComponentShares ],
         age_step: float ) -> ScoringPaces | None:
      if not season.games_played:
         return None

      rate = LeagueArrival.rate( arrivals, season.league, season.age )

      if rate is None:
         flat = LeagueFactor.rate( factors, season.league )

         if flat is None:
            return None

         rate = flat * age_step

      shares = min( component_shares, key=lambda share: abs( share.age - season.age ) )
      return shares.split( season.g_pace * rate, season.a_pace * rate )
