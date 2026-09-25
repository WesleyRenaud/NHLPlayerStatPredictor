from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.player_status import PlayerStatus
import api.skaters.player_status_hydrator as player_status_hydrator
from api.skaters.player_status_hydrator import PlayerStatusHydrator
from api.skaters.player_status_store import PlayerStatusStore
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season_store import SkaterSeasonStore
from api.skaters.team import Team


def _season( player_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=48,
      assists=90,
      points=138,
      schedule_games=82,
      pace_games=84,
      g_pace=48.0,
      a_pace=90.0,
      p_pace=138.0,
      gp_share=1.0 )


def Test_Hydrate_TestCachedLandings_ExpectStatusInserted(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   player_id = 7
   is_active = False
   landing = { 'playerId': player_id, 'isActive': is_active }
   inserted: list[ list[ PlayerStatus ] ] = []
   SkaterSeasonStore.insert_rows( [ _season( player_id ) ], db_path=db_path )
   monkeypatch.setattr(
      player_status_hydrator.PlayerLandingFetcher,
      'fetch',
      lambda player_ids, force=False: { player_id: landing } )
   monkeypatch.setattr(
      player_status_hydrator.PlayerStatusStore,
      'insert_rows',
      lambda rows, path: inserted.append( rows ) )

   PlayerStatusHydrator.hydrate( db_path )

   assert inserted == [ [ PlayerStatus( player_id, is_active ) ] ]


def Test_Hydrate_TestExistingStatus_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   player_id = 1
   is_active = True
   fetched: list[ bool ] = []
   SkaterSeasonStore.insert_rows( [ _season( player_id ) ], db_path=db_path )
   PlayerStatusStore.insert_rows(
      [ PlayerStatus( player_id, is_active ) ],
      db_path=db_path )
   monkeypatch.setattr(
      player_status_hydrator.PlayerLandingFetcher,
      'fetch',
      lambda player_ids, force=False: fetched.append( True ) or {} )

   PlayerStatusHydrator.hydrate( db_path )

   assert fetched == []


def Test_Hydrate_TestMissingSeasons_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   fetched: list[ bool ] = []
   monkeypatch.setattr(
      player_status_hydrator.PlayerLandingFetcher,
      'fetch',
      lambda player_ids, force=False: fetched.append( True ) or {} )

   PlayerStatusHydrator.hydrate( db_path )

   assert fetched == []
