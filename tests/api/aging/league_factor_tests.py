from __future__ import annotations

from api.aging.league_factor import LeagueFactor


def Test_ToDict_TestFactor_ExpectLeagueAndRate() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )

   payload = factor.to_dict()

   assert payload == {
      'league': factor.league,
      'rate': factor.rate,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = LeagueFactor( 'BBB', 0.28 )

   loaded = LeagueFactor.from_row( factor.to_dict() )

   assert loaded == factor


def Test_Rate_TestMatchingLeague_ExpectRate() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )

   rate = LeagueFactor.rate( [ factor ], factor.league )

   assert rate == factor.rate


def Test_Rate_TestMissingLeague_ExpectNone() -> None:
   factor = LeagueFactor( 'AAA', 0.44 )
   missing_league = 'BBB'

   rate = LeagueFactor.rate( [ factor ], missing_league )

   assert rate is None
