from __future__ import annotations

from api.availability.games_share import GamesShare
from api.skaters.skater_group import SkaterGroup
from api.team_factor.team_factor_skater import TeamFactorSkater


def Test_ToDict_TestSkater_ExpectPlayerIdAndContribution() -> None:
   skater = TeamFactorSkater( 97, 120.5, SkaterGroup( 'F' ), GamesShare.FULL, False, None )
   payload = skater.to_dict()
   assert payload[ 'player_id' ] == skater.player_id
   assert payload[ 'contribution' ] == skater.contribution
   assert payload[ 'prior_availability' ] is None


def Test_FromRow_TestDict_ExpectSkater() -> None:
   skater = TeamFactorSkater( 29, 88.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None )
   assert TeamFactorSkater.from_row( skater.to_dict() ) == skater
