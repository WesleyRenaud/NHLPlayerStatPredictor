from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class PlayerStatus():
   player_id: int
   is_active: bool
