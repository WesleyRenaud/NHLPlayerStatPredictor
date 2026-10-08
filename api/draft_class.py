from __future__ import annotations

from datetime import date

from .season import Season


class DraftClass():
   ELIGIBILITY_MONTH = 9
   ELIGIBILITY_DAY = 15
   ELIGIBILITY_AGE = 18


   @classmethod
   def eligibility_year( cls, birth_date: date ) -> int:
      year = birth_date.year + cls.ELIGIBILITY_AGE
      born_by_cutoff = ( birth_date.month, birth_date.day ) <= (
         cls.ELIGIBILITY_MONTH,
         cls.ELIGIBILITY_DAY )
      return year if born_by_cutoff else year + 1


   @classmethod
   def age( cls, birth_date: date, season_id: int ) -> int:
      draft_year = cls.eligibility_year( birth_date )
      return cls.ELIGIBILITY_AGE + Season.start_year( season_id ) - draft_year
