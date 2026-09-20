from __future__ import annotations

from api.league_factor import LeagueFactor


def Test_ToDict_TestFactor_ExpectLeagueGoalsAssists() -> None:
   factor = LeagueFactor( 'AAA', 0.44, 0.42 )
   assert factor.to_dict() == {
      'league': factor.league,
      'goals': factor.goals,
      'assists': factor.assists,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = LeagueFactor( 'BBB', 0.28, 0.30 )
   assert LeagueFactor.from_row( factor.to_dict() ) == factor
