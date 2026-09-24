from __future__ import annotations

from api.ice_pace_scaler import IcePaceScaler
from api.projections.season_pace import SeasonPace


def Test_Ratio_TestProjectedOverLast_ExpectScale() -> None:
   assert IcePaceScaler.ratio( 20.0, 24.0 ) == 1.2


def Test_Adjust_TestHigherIce_ExpectScaledPace() -> None:
   pace = SeasonPace( 30.0, 40.0 )
   assert IcePaceScaler.adjust( pace, 20.0, 24.0 ) == SeasonPace( 36.0, 48.0 )


def Test_Adjust_TestSameIce_ExpectUnchanged() -> None:
   pace = SeasonPace( 30.0, 40.0 )
   assert IcePaceScaler.adjust( pace, 20.0, 20.0 ) == pace
