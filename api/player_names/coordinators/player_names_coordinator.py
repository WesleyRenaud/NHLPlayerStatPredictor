from __future__ import annotations

from ..data_access.player_name_provider import PlayerNameProvider
from ...paths import Paths
from ..player_name_summary import PlayerNameSummary


class PlayerNamesCoordinator():
   @classmethod
   def get_player_summaries( cls ) -> list[ PlayerNameSummary ]:
      return PlayerNameProvider.summaries( str( Paths.DB_PATH ) )
