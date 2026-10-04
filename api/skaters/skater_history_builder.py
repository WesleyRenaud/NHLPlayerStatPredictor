from __future__ import annotations

from itertools import groupby

from ..projections.prospect_profile import ProspectProfile
from .skater_history import SkaterHistory
from .skater_season import SkaterSeason


class SkaterHistoryBuilder():
   @classmethod
   def build(
         cls,
         seasons: list[ SkaterSeason ],
         profiles: list[ ProspectProfile ] ) -> list[ SkaterHistory ]:
      profiles_by_player = { profile.player_id: profile for profile in profiles }
      return [
         SkaterHistory( player_id, list( player_seasons ), profiles_by_player[ player_id ] )
         for player_id, player_seasons in groupby(
            sorted( seasons, key=lambda season: season.player_id ),
            key=lambda season: season.player_id )
      ]
