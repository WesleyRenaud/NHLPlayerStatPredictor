from __future__ import annotations

from ..data_access.player_name_provider import PlayerNameProvider
from ...paths import Paths


class PlayerNamesCoordinator():
   @classmethod
   def get_player_names( cls ) -> list[ str ]:
      return PlayerNameProvider.names( str( Paths.DB_PATH ) )
