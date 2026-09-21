from __future__ import annotations

from api.league_factor import LeagueFactor


def Test_ToDict_TestFactor_ExpectLeagueAndRate() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )
   assert factor.to_dict() == {
      'league': factor.league,
      'rate': factor.rate,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = LeagueFactor( 'BBB', 0.28 )
   assert LeagueFactor.from_row( factor.to_dict() ) == factor
