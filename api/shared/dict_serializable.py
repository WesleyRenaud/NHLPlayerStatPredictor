from __future__ import annotations

from typing import Protocol


class DictSerializable( Protocol ):
   def to_dict( self ) -> dict[ str, object ]:
      ...
