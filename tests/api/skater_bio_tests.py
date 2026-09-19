from __future__ import annotations

from datetime import date

from api.skater_bio import SkaterBio


def Test_FromRow_TestBioJson_ExpectFields() -> None:
   bio = SkaterBio.from_row( { 'playerId': 8478402, 'birthDate': '1997-01-13' } )
   assert bio.player_id == 8478402
   assert bio.birth_date == date( 1997, 1, 13 )
