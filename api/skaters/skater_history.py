from __future__ import annotations

from dataclasses import dataclass

from .nhl_skater_season import NhlSkaterSeason
from .other_league_skater_season import OtherLeagueSkaterSeason
from ..projections.prospect_profile import ProspectProfile
from ..projections.prospect_source_resolver import ProspectSourceResolver
from .skater import Skater
from .skater_season import SkaterSeason


@dataclass( frozen=True )
class SkaterHistory():
   player_id: int
   seasons: list[ SkaterSeason ]
   profile: ProspectProfile


   def before( self, season_id: int ) -> Skater:
      return Skater( [ season for season in self.seasons if season.season_id < season_id ] )


   def nhl_seasons( self ) -> list[ NhlSkaterSeason ]:
      return [ season for season in self.seasons if isinstance( season, NhlSkaterSeason ) ]


   def other_league_seasons( self ) -> list[ OtherLeagueSkaterSeason ]:
      return [ season for season in self.seasons if isinstance( season, OtherLeagueSkaterSeason ) ]


   def latest_prospect_source(
         self,
         target_season_id: int,
         max_gap: int = ProspectSourceResolver.DEFAULT_MAX_GAP,
         *,
         supported_leagues: set[ str ] ) -> OtherLeagueSkaterSeason | None:
      return ProspectSourceResolver.latest(
         self.seasons, target_season_id, max_gap, supported_leagues=supported_leagues )
