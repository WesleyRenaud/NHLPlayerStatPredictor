from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from .prospect_calibration_sample import ProspectCalibrationSample
from .prospect_profile import ProspectProfile
from ..types import Types


@dataclass( frozen=True )
class ProspectCalibrationModel():
   target_season_id: int
   profiles: list[ ProspectProfile ]
   samples: list[ ProspectCalibrationSample ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProspectCalibrationModel:
      profiles = cast( Types.JsonObjectList, row[ 'profiles' ] )
      samples = cast( Types.JsonObjectList, row[ 'samples' ] )
      return cls(
         int( row[ 'target_season_id' ] ),
         [ ProspectProfile.from_row( profile ) for profile in profiles ],
         [ ProspectCalibrationSample.from_row( sample ) for sample in samples ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'target_season_id': self.target_season_id,
         'profiles': [ profile.to_dict() for profile in self.profiles ],
         'samples': [ sample.to_dict() for sample in self.samples ],
      }
