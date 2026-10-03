from .production_list_store import ProductionListStore
from ..projections.scoring_component_shares import ScoringComponentShares


class ScoringComponentShareStore( ProductionListStore ):
   FILE_NAME = 'scoring_component_shares.json'


   @classmethod
   def read( cls ) -> list[ ScoringComponentShares ]:
      return [ ScoringComponentShares.from_row( row ) for row in cls.read_rows() ]


   @classmethod
   def write( cls, shares: list[ ScoringComponentShares ] ) -> None:
      cls.write_rows( [ item.to_dict() for item in shares ] )
