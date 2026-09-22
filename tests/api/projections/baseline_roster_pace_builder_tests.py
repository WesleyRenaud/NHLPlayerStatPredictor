from __future__ import annotations

from datetime import date

import pytest

from api.aging_factor import AgingFactor
from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
import api.projections.baseline_roster_pace_builder as baseline_roster_pace_builder
from api.projections.baseline_roster_pace_builder import BaselineRosterPaceBuilder
from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.recency_weight import RecencyWeight
from api.roster_skater import RosterSkater
from api.shared.enums.position import Position
from api.skater import Skater
from api.skater_position import SkaterPosition
from api.team import Team


def _roster(
      player_id: int,
      team: Team,
      position: SkaterPosition = SkaterPosition( 'C' ) ) -> RosterSkater:
   return RosterSkater(
      player_id=player_id,
      player_name='Stub Skater',
      position=position,
      team=team )


def _nhl( player_id: int, team: Team ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=team,
      games_played=82,
      goals=0,
      assists=0,
      points=0,
      schedule_games=82,
      pace_games=84,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0 )


def _other( player_id: int ) -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=player_id,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=18.4,
      games_played=35,
      goals=15,
      assists=36,
      points=51,
      g_pace=36.0,
      a_pace=86.4 )


def Test_Build_TestRoster_ExpectEqualWeightPaces(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   veteran_id = 1
   rookie_id = 2
   veteran_pace = SeasonPace( 40.0, 50.0 )
   rookie_pace = SeasonPace( 10.0, 24.0 )
   weights = [ RecencyWeight( 0, 1.0 ) ]
   target_season_id = 20262027
   league_factors = [ LeagueFactor( 'AAA', 0.28 ) ]
   aging_factors = [ AgingFactor( 18, 0.12, 0.09 ) ]
   nhl_seasons = [ _nhl( veteran_id, previous ) ]
   other_seasons = [ _other( rookie_id ) ]
   resolved: list[ tuple[
      Skater,
      list[ RecencyWeight ],
      int,
      list[ LeagueFactor ],
      list[ AgingFactor ] ] ] = []
   paces = {
      veteran_id: veteran_pace,
      rookie_id: rookie_pace,
   }

   def resolve(
         skater: Skater,
         recency_weights: list[ RecencyWeight ],
         target: int,
         leagues: list[ LeagueFactor ],
         aging: list[ AgingFactor ] ) -> SeasonPace | None:
      resolved.append(
         ( skater, recency_weights, target, leagues, aging ) )
      return paces[ skater.seasons[ Position.FIRST ].player_id ]

   monkeypatch.setattr(
      baseline_roster_pace_builder.BaselinePaceResolver,
      'resolve',
      resolve )

   assert BaselineRosterPaceBuilder.build(
      [ _roster( veteran_id, now ), _roster( rookie_id, now ) ],
      nhl_seasons + other_seasons,
      weights,
      target_season_id,
      league_factors,
      aging_factors ) == [
         CurrentSeasonNhlSkater(
            veteran_id,
            veteran_pace,
            now,
            SkaterPosition( 'C' ) ),
         CurrentSeasonNhlSkater(
            rookie_id,
            rookie_pace,
            now,
            SkaterPosition( 'C' ) ),
      ]
   assert resolved == [
      ( Skater( nhl_seasons ), weights, target_season_id, league_factors, aging_factors ),
      ( Skater( other_seasons ), weights, target_season_id, league_factors, aging_factors ),
   ]


def Test_Build_TestMissingPace_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   team = list( Team )[ Position.FIRST ]
   pace = SeasonPace( 12.0, 18.0 )
   returns: list[ SeasonPace | None ] = [ pace, None ]
   monkeypatch.setattr(
      baseline_roster_pace_builder.BaselinePaceResolver,
      'resolve',
      lambda seasons, weights, target, leagues, aging: returns.pop( 0 ) )

   assert BaselineRosterPaceBuilder.build(
      [ _roster( 1, team ), _roster( 2, team ) ],
      [],
      [],
      20262027,
      [],
      [] ) == [
         CurrentSeasonNhlSkater( 1, pace, team, SkaterPosition( 'C' ) ),
      ]


def Test_Build_TestExcessForwards_ExpectAllPaces(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   team = list( Team )[ Position.FIRST ]
   roster = [ _roster( player_id, team ) for player_id in range( 1, 15 ) ]
   paces = (
      SeasonPace( 50.0 - player_id, 0.0 )
      for player_id in range( 1, 15 )
   )
   monkeypatch.setattr(
      baseline_roster_pace_builder.BaselinePaceResolver,
      'resolve',
      lambda seasons, weights, target, leagues, aging: next( paces ) )

   assert BaselineRosterPaceBuilder.build(
      roster,
      [],
      [],
      20262027,
      [],
      [] ) == [
         CurrentSeasonNhlSkater(
            player_id,
            SeasonPace( 50.0 - player_id, 0.0 ),
            team,
            SkaterPosition( 'C' ) )
         for player_id in range( 1, 15 )
      ]
