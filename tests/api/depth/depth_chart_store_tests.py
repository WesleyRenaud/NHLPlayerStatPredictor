from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.depth.depth_chart import DepthChart
from api.depth.depth_chart_store import DepthChartStore
from api.depth.ice_skater import IceSkater
from api.paths import Paths
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater( player_id: int ) -> IceSkater:
   return IceSkater(
      player_id,
      'A',
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      20.0,
      20.0,
      1.0 )


def Test_Write_TestCharts_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   team = list( Team )[ Position.FIRST ]
   charts = [
      DepthChart(
         team,
         [ ( _skater( 1 ), 25.0 ), ( _skater( 2 ), 23.0 ) ],
         [],
         [],
         SkaterGroup( 'D' ) ),
   ]
   DepthChartStore.write( charts )
   assert DepthChartStore.read() == [ charts[ Position.FIRST ].to_dict() ]
   assert DepthChartStore.path().read_text() == json.dumps(
      [ charts[ Position.FIRST ].to_dict() ],
      indent=2 )
