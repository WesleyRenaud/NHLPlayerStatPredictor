from __future__ import annotations

import sqlite3
from typing import TypeAlias


class Types():
   Connection: TypeAlias = sqlite3.Connection
   Cursor: TypeAlias = sqlite3.Cursor
   Row: TypeAlias = sqlite3.Row
   JsonObject: TypeAlias = dict[ str, object ]
   JsonObjectList: TypeAlias = list[ dict[ str, object ] ]
