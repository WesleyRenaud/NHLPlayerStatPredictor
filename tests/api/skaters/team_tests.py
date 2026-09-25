from __future__ import annotations

from api.skaters.team import Team


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   values = [ member.value for member in Team ]
   assert values
   assert len( values ) == len( set( values ) )

   for member in Team:
      assert isinstance( member.value, str )
      assert Team( member.value ) is member


def Test_FromName_TestAccentedName_ExpectTeam() -> None:
   assert Team.from_name( 'Montréal Canadiens' ) == Team( 'MTL' )


def Test_FromName_TestDottedName_ExpectTeam() -> None:
   assert Team.from_name( 'St. Louis Blues' ) == Team( 'STL' )
