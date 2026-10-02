from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from api.aging.league_factor import LeagueFactor
from api.projections.scoring_component_shares import ScoringComponentShares
from api.projections.scoring_stat import ScoringStat
from api.projections.translated_pace_averager import TranslatedPaceAverager
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _nhl(
      g_pace: float,
      a_pace: float,
      season_id: int,
   games_played: int = 82,
   power_play_goals: int = 0,
   power_play_points: int = 0,
   short_handed_goals: int = 0,
   short_handed_points: int = 0 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      even_strength_goals=int( g_pace ) - power_play_goals - short_handed_goals,
      even_strength_points=( int( g_pace + a_pace ) ) - power_play_points - short_handed_points,
      goals=int( g_pace ),
      assists=int( a_pace ),
      points=int( g_pace + a_pace ),
      schedule_games=82,
      pace_games=82,
      g_pace=Season.pace( int( g_pace ), games_played, 82 ),
      a_pace=Season.pace( int( a_pace ), games_played, 82 ),
      p_pace=Season.pace( int( g_pace + a_pace ), games_played, 82 ),
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=power_play_goals,
      power_play_points=power_play_points,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points,
      shots=0,
      penalty_minutes=0 )


def _other(
      g_pace: float,
      a_pace: float,
      season_id: int,
      league: str,
      games_played: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1,
      season_id=season_id,
      league=league,
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=games_played,
      goals=1,
      assists=1,
      points=2,
      g_pace=g_pace,
      a_pace=a_pace )


def Test_Year_TestMixedNhlAndOther_ExpectGamesWeightedBlend() -> None:
   league = 'AAA'
   factor = LeagueFactor( league, 0.40 )
   nhl_games = 1
   other_games = 46
   nhl = replace( _nhl( 84.0, 84.0, 20252026, nhl_games ), penalty_minutes=2 )
   other = _other( 10.96, 23.74, 20252026, league, other_games )
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )
   total_games = nhl_games + other_games

   year = TranslatedPaceAverager.year( [ nhl, other ], [ factor ], [ shares ] )

   assert year.games == total_games
   assert year.scoring.goals == pytest.approx(
      ( nhl_games * nhl.g_pace + other_games * other.g_pace * factor.rate )
      / total_games )
   assert year.scoring.assists == pytest.approx(
      ( nhl_games * nhl.a_pace + other_games * other.a_pace * factor.rate )
      / total_games )
   assert year.scoring.power_play_goals == pytest.approx(
      other_games * other.g_pace * factor.rate * shares.power_play_goals / total_games )
   assert year.scoring.power_play_assists == pytest.approx(
      other_games * other.a_pace * factor.rate * shares.power_play_assists / total_games )
   assert year.penalty_minutes == pytest.approx( nhl.penalty_minutes_pace() )


def Test_Year_TestOtherLeagueOnly_ExpectMissingPim() -> None:
   factor = LeagueFactor( 'AAA', 0.40 )
   other = _other( 10.96, 23.74, 20252026, factor.league, 46 )
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )

   year = TranslatedPaceAverager.year( [ other ], [ factor ], [ shares ] )

   assert year is not None
   assert year.penalty_minutes is None


def Test_Year_TestNhlStoredComponents_ExpectNoUseOfTotalPaces() -> None:
   nhl = replace( _nhl( 20.0, 30.0, 20252026, 82, 4, 10, 2, 3 ), g_pace=999.0, a_pace=999.0 )

   year = TranslatedPaceAverager.year( [ nhl ], [], [] )

   assert year is not None
   observed = nhl.scoring_paces()
   for stat in ScoringStat:
      assert getattr( year.scoring, stat.value ) == pytest.approx( getattr( observed, stat.value ) )


def Test_Year_TestOtherLeagueWithoutShares_ExpectNoAssumedBreakdown() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   other = _other( 40.0, 60.0, 20252026, factor.league, 40 )

   with pytest.raises( ValueError, match='empty' ):
      TranslatedPaceAverager.year( [ other ], [ factor ], [] )


def Test_Totals_TestMixedSources_ExpectOnlyTotalPacesUsed() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   nhl = replace( _nhl( 20.0, 30.0, 20252026, 10, 4, 10 ), g_pace=7.0, a_pace=11.0 )
   other = _other( 40.0, 60.0, nhl.season_id, factor.league, 40 )
   translated_totals = other.nhl_pace( [ factor ] )
   total_games = nhl.games_played + other.games_played

   totals = TranslatedPaceAverager.totals( [ nhl, other ], [ factor ] )

   assert totals is not None
   assert totals.goals == pytest.approx(
      ( nhl.games_played * nhl.g_pace + other.games_played * translated_totals.goals ) / total_games )
   assert totals.assists == pytest.approx(
      ( nhl.games_played * nhl.a_pace + other.games_played * translated_totals.assists ) / total_games )


def Test_Totals_TestUnknownLeague_ExpectSkipped() -> None:
   nhl = _nhl( 20.0, 30.0, 20252026 )
   other = _other( 100.0, 100.0, nhl.season_id, 'AAA', 40 )

   totals = TranslatedPaceAverager.totals( [ nhl, other ], [] )

   assert totals is not None
   assert totals.goals == pytest.approx( nhl.g_pace )
   assert totals.assists == pytest.approx( nhl.a_pace )


def Test_Totals_TestNoEligibleGames_ExpectNone() -> None:
   zero_games = replace( _nhl( 0.0, 0.0, 20252026 ), games_played=0 )

   assert TranslatedPaceAverager.totals( [ zero_games ], [] ) is None


def Test_Year_TestNhlPowerPlayTotals_ExpectSeparatePowerPlayPace() -> None:
   games_played = 10
   power_play_goals = 4
   power_play_points = 10
   nhl = _nhl(
      20.0,
      30.0,
      20252026,
      games_played,
      power_play_goals=power_play_goals,
      power_play_points=power_play_points )
   expected_power_play_goals = Season.pace(
      float( power_play_goals ),
      float( games_played ),
      nhl.pace_games )
   expected_power_play_assists = Season.pace(
      float( power_play_points - power_play_goals ),
      float( games_played ),
      nhl.pace_games )

   year = TranslatedPaceAverager.year( [ nhl ], [], [] )

   assert year.scoring.power_play_goals == pytest.approx( expected_power_play_goals )
   assert year.scoring.power_play_assists == pytest.approx( expected_power_play_assists )


def Test_Year_TestNhlShortHandedTotals_ExpectSeparateShortHandedPace() -> None:
   games_played = 10
   short_handed_goals = 2
   short_handed_points = 3
   nhl = _nhl(
      20.0,
      30.0,
      20252026,
      games_played,
      short_handed_goals=short_handed_goals,
      short_handed_points=short_handed_points )
   expected_goals = Season.pace(
      float( short_handed_goals ), float( games_played ), nhl.pace_games )
   expected_assists = Season.pace(
      float( short_handed_points - short_handed_goals ),
      float( games_played ),
      nhl.pace_games )

   year = TranslatedPaceAverager.year( [ nhl ], [], [] )

   assert year.scoring.short_handed_goals == pytest.approx( expected_goals )
   assert year.scoring.short_handed_assists == pytest.approx( expected_assists )


def Test_Year_TestNoGames_ExpectNone() -> None:
   year = TranslatedPaceAverager.year( [], [], [] )

   assert year is None


def Test_Year_TestZeroGameNhlSeason_ExpectNone() -> None:
   nhl = replace( _nhl( 0.0, 0.0, 20252026 ), games_played=0 )

   assert TranslatedPaceAverager.year( [ nhl ], [], [] ) is None


def Test_Year_TestMixedComponents_ExpectSharedWeightingAndNhlOnlyPim() -> None:
   factor = LeagueFactor( 'AAA', 0.5 )
   shares = ScoringComponentShares( 20, 0.75, 0.68, 0.2, 0.3, 0.05, 0.02 )
   nhl = replace( _nhl( 20.0, 30.0, 20252026, 10, 4, 10, 2, 3 ), penalty_minutes=6 )
   other = _other( 40.0, 60.0, nhl.season_id, factor.league, 40 )
   observed = nhl.scoring_paces()
   translated = other.nhl_pace( [ factor ] )
   inferred = shares.split( translated.goals, translated.assists )
   total_games = nhl.games_played + other.games_played

   year = TranslatedPaceAverager.year( [ nhl, other ], [ factor ], [ shares ] )

   assert year is not None
   for stat in ScoringStat:
      expected_pace = (
         nhl.games_played * getattr( observed, stat.value )
         + other.games_played * getattr( inferred, stat.value ) ) / total_games
      assert getattr( year.scoring, stat.value ) == pytest.approx( expected_pace )
   assert year.games == total_games
   assert year.nhl_games == nhl.games_played
   assert year.penalty_minutes == pytest.approx( nhl.penalty_minutes_pace() )


def Test_Year_TestMissingLeague_ExpectNhlOnly() -> None:
   nhl = _nhl( 20.0, 30.0, 20252026, 10 )
   other = _other( 100.0, 100.0, 20252026, 'AAA', 50 )

   year = TranslatedPaceAverager.year( [ nhl, other ], [], [] )

   assert year.games == nhl.games_played
   assert year.scoring.goals == nhl.g_pace
   assert year.scoring.assists == nhl.a_pace
