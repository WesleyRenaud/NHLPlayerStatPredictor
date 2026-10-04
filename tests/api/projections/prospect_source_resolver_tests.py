from __future__ import annotations

from dataclasses import replace

import pytest

from api.projections.prospect_source_resolver import ProspectSourceResolver
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition


def _source() -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=1, season_id=20252026, age=18.5, games_played=40,
      goals=10, assists=20, points=30, g_pace=21.0, a_pace=42.0,
      position=SkaterPosition.CENTER, league='SHL' )


@pytest.mark.parametrize( 'row', [
   replace( _source(), games_played=19 ), replace( _source(), league='Unknown' ),
   replace( _source(), age=24 ),
   replace( _source(), season_id=20262027 ),
] )
def Test_Latest_TestUnusableSource_ExpectNone( row: OtherLeagueSkaterSeason ) -> None:
   assert ProspectSourceResolver.latest( [ row ], 20262027, supported_leagues={ 'SHL' } ) is None


def Test_Latest_TestGapAndTranslation_ExpectLatestSupportedSource() -> None:
   old = replace( _source(), season_id=20212022 )
   latest = _source()

   assert ProspectSourceResolver.latest( [ old ], 20262027, supported_leagues={ 'SHL' } ) is None
   assert ProspectSourceResolver.latest( [ old ], 20262027, max_gap=5, supported_leagues={ 'SHL' } ) is old
   assert ProspectSourceResolver.latest( [ old, latest ], 20262027, max_gap=5, supported_leagues={ 'SHL' } ) is latest
   assert ProspectSourceResolver.latest( [ latest ], 20262027, supported_leagues={ 'OHL' } ) is None


def Test_Latest_TestDefenseSource_ExpectUsable() -> None:
   source = replace( _source(), position=SkaterPosition.DEFENSE )

   assert ProspectSourceResolver.latest( [ source ], 20262027, supported_leagues={ 'SHL' } ) is source


def Test_Latest_TestSameSeasonSources_ExpectGamesThenLeagueTieBreak() -> None:
   shl = _source()
   ohl = replace( shl, league='OHL' )
   larger = replace( shl, games_played=41 )

   assert ProspectSourceResolver.latest( [ shl, ohl ], 20262027, supported_leagues={ 'SHL', 'OHL' } ) is ohl
   assert ProspectSourceResolver.latest( [ ohl, larger ], 20262027, supported_leagues={ 'SHL', 'OHL' } ) is larger


def Test_Latest_TestEmptySupportedLeagues_ExpectNone() -> None:
   assert ProspectSourceResolver.latest( [ _source() ], 20262027, supported_leagues=set() ) is None
