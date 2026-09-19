from __future__ import annotations

from .tables import runtime_tables
from ..types import Types


class SchemaCreator():
   @classmethod
   def create( cls, cursor: Types.Cursor ) -> None:
      for table in runtime_tables:
         table.create_table( cursor )
