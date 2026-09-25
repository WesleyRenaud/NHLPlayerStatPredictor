from __future__ import annotations

from pathlib import Path

import pytest

from api.paths import Paths
import api.player_names.coordinators.player_names_coordinator as player_names_coordinator
from api.player_names.coordinators.player_names_coordinator import PlayerNamesCoordinator
from api.player_names.player_name_summary import PlayerNameSummary
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_GetPlayerSummaries_TestProvider_ExpectSummaries(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   stub_summaries = [
      PlayerNameSummary(
         1,
         'Stub Alpha',
         list( SkaterPosition )[ Position.FIRST ],
         list( Team )[ Position.FIRST ],
         20202021 ),
   ]
   db_path = tmp_path / 'skaters.sqlite'
   target_season_id = 20262027
   captured: list[ tuple[ str, int ] ] = []

   def fake_summaries( path: str, season_id: int ) -> list[ PlayerNameSummary ]:
      captured.append( ( path, season_id ) )
      return stub_summaries

   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr(
      player_names_coordinator.RecencyTargetResolver,
      'resolve',
      lambda: target_season_id )
   monkeypatch.setattr(
      player_names_coordinator.PlayerNameProvider,
      'summaries',
      fake_summaries )
   assert PlayerNamesCoordinator.get_player_summaries() == stub_summaries
   assert captured == [ ( str( db_path ), target_season_id ) ]
