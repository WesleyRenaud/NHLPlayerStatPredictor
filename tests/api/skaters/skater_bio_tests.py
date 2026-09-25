from __future__ import annotations

from datetime import date

from api.skaters.skater_bio import SkaterBio


def Test_FromRow_TestBioJson_ExpectFields() -> None:
   bio = SkaterBio( 8478402, date( 1997, 1, 13 ) )

   loaded = SkaterBio.from_row( {
      'playerId': bio.player_id,
      'birthDate': bio.birth_date.isoformat(),
   } )

   assert loaded == bio
