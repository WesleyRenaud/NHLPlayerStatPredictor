from __future__ import annotations

from api.aging.league_factor import LeagueFactor


def Test_ToDict_TestFactor_ExpectLeagueAndRate() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )
   assert factor.to_dict() == {
      'league': factor.league,
      'rate': factor.rate,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = LeagueFactor( 'BBB', 0.28 )
   assert LeagueFactor.from_row( factor.to_dict() ) == factor


def Test_Rate_TestMatchingLeague_ExpectRate() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )
   assert LeagueFactor.rate( [ factor ], factor.league ) == factor.rate


def Test_Rate_TestMissingLeague_ExpectNone() -> None:
   assert LeagueFactor.rate( [ LeagueFactor( 'AAA', 0.44 ) ], 'BBB' ) is None
