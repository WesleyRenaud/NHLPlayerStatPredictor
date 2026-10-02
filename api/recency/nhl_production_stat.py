from __future__ import annotations

from enum import Enum


class NhlProductionStat( str, Enum ):
   PIM = 'pim_pace'
   SHOTS = 'shots_pace'
