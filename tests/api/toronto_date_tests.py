from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

import api.toronto_date as toronto_date
from api.toronto_date import TorontoDate


def Test_Today_TestTorontoClock_ExpectThatDate(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   now = datetime( 2026, 10, 2, 23, 30, tzinfo=ZoneInfo( 'America/Toronto' ) )
   clock = Mock()
   clock.now.return_value = now
   monkeypatch.setattr( toronto_date, 'datetime', clock )

   on_date = TorontoDate.today()

   assert on_date == now.date()
   clock.now.assert_called_once_with( ZoneInfo( 'America/Toronto' ) )
