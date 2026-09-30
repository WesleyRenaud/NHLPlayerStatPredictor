from __future__ import annotations

from datetime import date

from api.projections.power_play_pace import PowerPlayPace
from api.projections.season_pace import SeasonPace
from api.recency.pace_sample import PaceSample
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _current( season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=26.4,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=0,
      assists=0,
      points=0,
      schedule_games=82,
      pace_games=82,
      g_pace=20.0,
      a_pace=30.0,
      p_pace=50.0,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0 )


def _prior( year: int, nhl_games: int = 82 ) -> PriorYear:
   return PriorYear(
      year,
      SeasonPace( 10.0, 20.0 ),
      PowerPlayPace.zero(),
      82,
      nhl_games,
      25.4,
      SeasonPace.zero() )


def Test_Source_TestLatestPrior_ExpectLatestSource() -> None:
   sample = PaceSample( _current( 20242025 ), [ _prior( 2023, 0 ), _prior( 2022 ) ] )

   assert sample.source() == PriorSource.TRANSLATED
   assert sample.target_age() == 26


def Test_Gap_TestMissedSeason_ExpectGapFromCurrentYear() -> None:
   consecutive = PaceSample( _current( 20242025 ), [ _prior( 2023 ) ] )
   returning = PaceSample( _current( 20242025 ), [ _prior( 2022 ) ] )

   assert consecutive.gap() == 0
   assert returning.gap() == 1


def Test_Truncated_TestWidth_ExpectLeadingPriors() -> None:
   priors = [ _prior( 2023 ), _prior( 2022 ), _prior( 2021 ) ]
   sample = PaceSample( _current( 20242025 ), priors )

   truncated = sample.truncated( 2 )

   assert truncated == PaceSample( sample.current, priors[ :2 ] )
