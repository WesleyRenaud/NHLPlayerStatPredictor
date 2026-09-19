from __future__ import annotations

from enum import Enum


class SkaterPosition( str, Enum ):
   CENTER = 'C'
   DEFENSE = 'D'
   LEFT_WING = 'L'
   RIGHT_WING = 'R'
