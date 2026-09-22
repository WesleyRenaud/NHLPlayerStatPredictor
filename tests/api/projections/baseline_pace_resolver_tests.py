from __future__ import annotations

from datetime import date

import pytest

from api.aging_factor import AgingFactor
from api.league_factor import LeagueFactor
from api.nhl_skater_season import NhlSkaterSeason
from api.other_league_skater_season import OtherLeagueSkaterSeason
import api.projections.baseline_pace_resolver as baseline_pace_resolver
from api.projections.baseline_pace_resolver import BaselinePaceResolver
from api.projections.season_pace import SeasonPace
from api.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skater import Skater
from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.team import Team


def _season( age: float, season_id: int = 20232024 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=1.0 )


def Test_Resolve_TestSeasons_ExpectAgedPace(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [ _season( 27.2 ), _season( 28.7 ) ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 28, -0.07, -0.044 ) ]
   target_season_id = 20232024
   pace = SeasonPace( 31.4, 42.1 )
   aged = SeasonPace( 10.4, 20.6 )
   league_factors: list[ LeagueFactor ] = []
   averaged: list[ tuple[
      list[ SkaterSeason ],
      list[ RecencyWeight ],
      int,
      list[ LeagueFactor ] ] ] = []
   adjusted: list[ tuple[
      SeasonPace,
      int,
      list[ AgingFactor ],
      list[ NhlSkaterSeason ] ] ] = []

   monkeypatch.setattr(
      baseline_pace_resolver.TranslatedPaceAverager,
      'average',
      lambda rows, recency_weights, target, leagues: averaged.append(
         ( rows, recency_weights, target, leagues ) ) or pace )
   monkeypatch.setattr(
      baseline_pace_resolver.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         ( recency_pace, completed_age, aging_factors, player_seasons ) ) or aged )

   assert BaselinePaceResolver.resolve(
      Skater( seasons ),
      weights,
      target_season_id,
      league_factors,
      factors ) == aged
   assert averaged == [
      ( seasons, weights, target_season_id, league_factors )
   ]
   assert adjusted == [
      ( pace, seasons[ Position.LAST ].completed_age(), factors, seasons )
   ]


def Test_Resolve_TestOtherLeagueOnly_ExpectOtherLeagueAge(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   other_age = 20.8
   seasons = [
      OtherLeagueSkaterSeason(
         player_id=7,
         season_id=20252026,
         league='AAA',
         position=SkaterPosition( 'C' ),
         age=other_age,
         games_played=46,
         goals=6,
         assists=13,
         points=19,
         g_pace=10.0,
         a_pace=20.0 )
   ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 20, 0.12, 0.09 ) ]
   target_season_id = 20262027
   pace = SeasonPace( 31.4, 42.1 )
   aged = SeasonPace( 10.4, 20.6 )
   adjusted: list[ tuple[
      SeasonPace,
      int,
      list[ AgingFactor ],
      list[ NhlSkaterSeason ] ] ] = []

   monkeypatch.setattr(
      baseline_pace_resolver.TranslatedPaceAverager,
      'average',
      lambda rows, recency_weights, target, leagues: pace )
   monkeypatch.setattr(
      baseline_pace_resolver.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         ( recency_pace, completed_age, aging_factors, player_seasons ) ) or aged )

   assert BaselinePaceResolver.resolve(
      Skater( seasons ),
      weights,
      target_season_id,
      [],
      factors ) == aged
   assert adjusted == [
      ( pace, int( other_age ), factors, [] )
   ]


def Test_Resolve_TestMissingPace_ExpectNone(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   adjusted: list[ SeasonPace ] = []
   monkeypatch.setattr(
      baseline_pace_resolver.TranslatedPaceAverager,
      'average',
      lambda rows, recency_weights, target, leagues: None )
   monkeypatch.setattr(
      baseline_pace_resolver.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         recency_pace ) )

   assert BaselinePaceResolver.resolve( Skater( [] ), [], 20262027, [], [] ) is None
   assert adjusted == []


def Test_Resolve_TestMixed_ExpectLastNhlAge(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   nhl = [ _season( 18.4, 20242025 ), _season( 19.4, 20252026 ) ]
   other = OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.4,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )
   seasons = [ *nhl, other ]
   weights = [ RecencyWeight( 0, 1.0 ) ]
   factors = [ AgingFactor( 19, 0.12, 0.09 ) ]
   pace = SeasonPace( 31.4, 42.1 )
   aged = SeasonPace( 10.4, 20.6 )
   adjusted: list[ tuple[
      SeasonPace,
      int,
      list[ AgingFactor ],
      list[ NhlSkaterSeason ] ] ] = []

   monkeypatch.setattr(
      baseline_pace_resolver.TranslatedPaceAverager,
      'average',
      lambda rows, recency_weights, target, leagues: pace )
   monkeypatch.setattr(
      baseline_pace_resolver.AgingPaceAdjuster,
      'adjust',
      lambda recency_pace, completed_age, aging_factors, player_seasons: adjusted.append(
         ( recency_pace, completed_age, aging_factors, player_seasons ) ) or aged )
   assert BaselinePaceResolver.resolve(
      Skater( seasons ),
      weights,
      20262027,
      [],
      factors ) == aged
   assert adjusted == [
      ( pace, nhl[ Position.LAST ].completed_age(), factors, nhl )
   ]
