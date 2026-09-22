from __future__ import annotations

from api.team_factor_skater import TeamFactorSkater


def Test_ToDict_TestSkater_ExpectPlayerIdAndContribution() -> None:
   skater = TeamFactorSkater( 97, 120.5 )
   assert skater.to_dict() == {
      'player_id': skater.player_id,
      'contribution': skater.contribution,
   }


def Test_FromRow_TestDict_ExpectSkater() -> None:
   skater = TeamFactorSkater( 29, 88.0 )
   assert TeamFactorSkater.from_row( skater.to_dict() ) == skater
