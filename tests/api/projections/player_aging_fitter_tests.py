from __future__ import annotations

from datetime import date

from api.projections.player_aging_fitter import PlayerAgingFitter
from api.projections.player_aging_rate import PlayerAgingRate
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season(
      season_id: int,
      g_pace: float,
      a_pace: float ) -> SkaterSeason:
   return SkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.0,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=g_pace,
      a_pace=a_pace,
      p_pace=g_pace + a_pace,
      gp_share=1.0 )


def Test_Fit_TestConsecutiveSeasons_ExpectRatioOfMeans() -> None:
   seasons = [
      _season( 20212022, 10.0, 20.0 ),
      _season( 20222023, 12.0, 22.0 ),
      _season( 20232024, 8.0, 18.0 ),
   ]
   goal_pace = 10.0 + 12.0
   assist_pace = 20.0 + 22.0
   assert PlayerAgingFitter.fit( seasons ) == PlayerAgingRate(
      2,
      ( ( 12.0 - 10.0 ) + ( 8.0 - 12.0 ) ) / goal_pace,
      ( ( 22.0 - 20.0 ) + ( 18.0 - 22.0 ) ) / assist_pace )


def Test_Fit_TestLowPaceSwing_ExpectRatioOfMeansNotMeanOfPercents() -> None:
   seasons = [
      _season( 20222023, 5.0, 5.0 ),
      _season( 20232024, 10.0, 10.0 ),
      _season( 20242025, 10.0, 10.0 ),
   ]
   goal_pace = 5.0 + 10.0
   assert PlayerAgingFitter.fit( seasons ) == PlayerAgingRate(
      2,
      ( ( 10.0 - 5.0 ) + ( 10.0 - 10.0 ) ) / goal_pace,
      ( ( 10.0 - 5.0 ) + ( 10.0 - 10.0 ) ) / goal_pace )


def Test_Fit_TestGapYear_ExpectSkipped() -> None:
   seasons = [
      _season( 20212022, 20.0, 20.0 ),
      _season( 20232024, 40.0, 40.0 ),
   ]
   assert PlayerAgingFitter.fit( seasons ) is None


def Test_Fit_TestOlderThanWindow_ExpectRecentPairsOnly() -> None:
   seasons = [
      _season( 20182019, 100.0, 100.0 ),
      _season( 20192020, 10.0, 10.0 ),
      _season( 20202021, 10.0, 10.0 ),
      _season( 20212022, 10.0, 10.0 ),
      _season( 20222023, 10.0, 10.0 ),
      _season( 20232024, 10.0, 10.0 ),
   ]
   window = seasons[ -PlayerAgingFitter.WINDOW - 1: ]
   assert PlayerAgingFitter.fit( seasons ) == PlayerAgingFitter.fit( window )
