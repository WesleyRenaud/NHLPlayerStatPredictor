from __future__ import annotations

from api.depth.ice_pace_scaler import IcePaceScaler
from api.projections.season_pace import SeasonPace


def Test_Ratio_TestProjectedOverLast_ExpectScale() -> None:
   last = 20.0
   projected = 24.0

   ratio = IcePaceScaler.ratio( last, projected )

   assert ratio == projected / last


def Test_Adjust_TestHigherIce_ExpectScaledPace() -> None:
   last = 20.0
   projected = 24.0
   pace = SeasonPace( 30.0, 40.0 )

   scaled = IcePaceScaler.adjust( pace, last, projected )

   assert scaled == SeasonPace(
      pace.goals * projected / last,
      pace.assists * projected / last )


def Test_Adjust_TestSameIce_ExpectUnchanged() -> None:
   last = 20.0
   pace = SeasonPace( 30.0, 40.0 )

   scaled = IcePaceScaler.adjust( pace, last, last )

   assert scaled == pace
