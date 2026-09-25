from __future__ import annotations

from typing import Protocol


class IceAvailable( Protocol ):
   player_id: int
   availability: float
