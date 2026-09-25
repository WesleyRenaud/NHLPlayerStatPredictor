from __future__ import annotations

from api.skaters.team import Team


def Test_Members_TestValues_ExpectUniqueStrings() -> None:
   members = list( Team )

   values = [ member.value for member in members ]

   assert values
   assert len( values ) == len( set( values ) )
   assert all( isinstance( value, str ) for value in values )
   assert [ Team( value ) for value in values ] == members


def Test_FromName_TestAccentedName_ExpectTeam() -> None:
   name = 'Montréal Canadiens'

   team = Team.from_name( name )

   assert team == Team( 'MTL' )


def Test_FromName_TestDottedName_ExpectTeam() -> None:
   name = 'St. Louis Blues'

   team = Team.from_name( name )

   assert team == Team( 'STL' )


def Test_FromName_TestUtahHockeyClub_ExpectMammoth() -> None:
   name = 'Utah Hockey Club'

   team = Team.from_name( name )

   assert team == Team( 'UTA' )
