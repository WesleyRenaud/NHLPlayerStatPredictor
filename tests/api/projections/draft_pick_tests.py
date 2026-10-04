from __future__ import annotations

import pytest

from api.projections.draft_pick import DraftPick


@pytest.mark.parametrize( 'value', [ None, 1, 32, 224, 225, 288 ] )
def Test_DraftPick_TestValidValue_ExpectPreserved( value: int | None ) -> None:
   assert DraftPick( value ).value == value


@pytest.mark.parametrize( 'value', [ 0, -1 ] )
def Test_DraftPick_TestNonpositiveValue_ExpectError( value: int ) -> None:
   with pytest.raises( ValueError, match='positive integer' ):
      DraftPick( value )


def Test_DraftPick_TestBoolean_ExpectError() -> None:
   with pytest.raises( ValueError, match='positive integer' ):
      DraftPick( True )
