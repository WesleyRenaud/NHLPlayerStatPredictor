from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.depth.nhl_history_ice_scaler import NhlHistoryIceScaler
from api.depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from api.ingest.nhl_client import NhlClient
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.types import Types


def _season() -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1, season_id=20242025, age=27.4, games_played=82,
      goals=20, assists=30, points=50, g_pace=20.0, a_pace=30.0,
      position=SkaterPosition( 'C' ), player_name='Stub', birth_date=date( 1997, 1, 13 ),
      team=Team( 'COL' ), schedule_games=82, pace_games=82, p_pace=50.0,
      penalty_minutes=20, gp_share=1.0, playoff_games=0, playoff_goals=0,
      playoff_assists=0, power_play_goals=0, power_play_points=0,
      short_handed_goals=0, short_handed_points=0,
      even_strength_goals=20, even_strength_points=50, shots=200 )


def Test_Scales_TestHistory_ExpectEachSeasonMinutesAndLimitedWindow(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   calls = []

   def _rows( season_id: int ) -> Types.JsonObjectList:
      calls.append( season_id )
      return [ { 'playerId': 1, 'timeOnIcePerGame': 1200 if season_id == 20242025 else 600,
         'gamesPlayed': 82, 'teamAbbrevs': 'COL', 'positionCode': 'C' } ]

   monkeypatch.setattr( NhlClient, 'skater_timeonice', _rows )
   seasons = [ replace( _season(), season_id=year * 10000 + year + 1 )
      for year in range( 2020, 2026 ) ]

   scales = NhlHistoryIceScaler.scales( seasons, 20252026, 20.0 )

   assert scales == [
      NhlPlayerSeasonIceScale( 1, 20242025, 1.0 ),
      NhlPlayerSeasonIceScale( 1, 20232024, 2.0 ),
      NhlPlayerSeasonIceScale( 1, 20222023, 2.0 ),
   ]
   assert calls == [ 20242025, 20232024, 20222023 ]


def Test_Scales_TestInvalidReference_ExpectExplicitError() -> None:
   with pytest.raises( ValueError, match='reference must be positive' ):
      NhlHistoryIceScaler.scales( [ _season() ], 20252026, 0.0 )
