from __future__ import annotations

from enum import Enum


class PriorSource( str, Enum ):
   NHL = 'nhl'
   TRANSLATED = 'translated'
