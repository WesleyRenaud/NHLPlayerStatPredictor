from __future__ import annotations

from enum import IntEnum

from .shared_enum_values import SharedEnumValues


Position = IntEnum(
   'Position',
   SharedEnumValues.load_integers( 'position.json' ),
)
