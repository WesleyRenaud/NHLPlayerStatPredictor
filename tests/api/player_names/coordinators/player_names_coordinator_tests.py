from __future__ import annotations

from pathlib import Path

import pytest

from api.paths import Paths
import api.player_names.coordinators.player_names_coordinator as player_names_coordinator
from api.player_names.coordinators.player_names_coordinator import PlayerNamesCoordinator


def Test_GetPlayerNames_TestProvider_ExpectNames(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   stub_names = [ 'Stub Alpha', 'Stub Beta' ]
   db_path = tmp_path / 'skaters.sqlite'
   captured: list[ str ] = []

   def fake_names( path: str ) -> list[ str ]:
      captured.append( path )
      return stub_names

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr(
      player_names_coordinator.PlayerNameProvider,
      'names',
      fake_names )
   assert PlayerNamesCoordinator.get_player_names() == stub_names
   assert captured == [ str( db_path ) ]
