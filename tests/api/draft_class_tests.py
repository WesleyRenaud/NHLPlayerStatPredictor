from __future__ import annotations

from datetime import date

from api.draft_class import DraftClass


def Test_Age_TestSameDraft_ExpectSameAge() -> None:
   season_id = 20252026
   late = date( 2007, 9, 30 )
   early = date( 2008, 3, 12 )

   assert DraftClass.age( late, season_id ) == DraftClass.age( early, season_id )
   assert DraftClass.age( late, 20262027 ) == DraftClass.age( early, 20262027 )


def Test_Age_TestDraftYear_ExpectEighteen() -> None:
   birth_date = date( 2007, 12, 20 )

   assert DraftClass.eligibility_year( birth_date ) == 2026
   assert DraftClass.age( birth_date, 20262027 ) == 18


def Test_Age_TestYearAfterDraft_ExpectNineteen() -> None:
   assert DraftClass.age( date( 2007, 12, 20 ), 20272028 ) == 19


def Test_EligibilityYear_TestBornAfterCutoff_ExpectNextYear() -> None:
   assert DraftClass.eligibility_year( date( 2007, 9, 16 ) ) == 2026


def Test_EligibilityYear_TestLeapDay_ExpectYearTheyTurnEighteen() -> None:
   assert DraftClass.eligibility_year( date( 2008, 2, 29 ) ) == 2026
