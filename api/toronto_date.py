from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo


class TorontoDate():
   @classmethod
   def today( cls ) -> date:
      return datetime.now( ZoneInfo( 'America/Toronto' ) ).date()
