from __future__ import annotations

from dataclasses import replace
from datetime import date

from api.ingest.nhl_client import NhlClient
from api.ingest.playoff_totals_merger import PlayoffTotalsMerger
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team
from api.types import Types


def _season( player_id: int, season_id: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=season_id,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=58,
      even_strength_goals=12,
      even_strength_points=22,
      goals=12,
      assists=10,
      points=22,
      schedule_games=82,
      pace_games=84,
      g_pace=17.4,
      a_pace=14.5,
      p_pace=31.9,
      gp_share=0.7,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      penalty_minutes=0 )


def _total(
      season_id: int,
      games_played: int,
      goals: int,
      assists: int,
      league: str = PlayoffTotalsMerger.NHL,
      game_type_id: int = NhlClient.PLAYOFF_GAME_TYPE_ID ) -> Types.JsonObject:
   return {
      'season': season_id,
      'leagueAbbrev': league,
      'gameTypeId': game_type_id,
      'gamesPlayed': games_played,
      'goals': goals,
      'assists': assists,
   }


def _landing( player_id: int, totals: Types.JsonObjectList ) -> Types.JsonObject:
   return { 'playerId': player_id, 'seasonTotals': totals }


def Test_Merge_TestMixedTotals_ExpectNhlPlayoffsForSeason() -> None:
   season = _season( 7, 20252026 )
   landing = _landing(
      7,
      [
         _total( 20252026, 22, 14, 4 ),
         _total( 20252026, 58, 12, 10, game_type_id=NhlClient.REGULAR_SEASON_GAME_TYPE_ID ),
         _total( 20252026, 6, 3, 3, league='AHL' ),
         _total( 20242025, 12, 2, 2 ),
      ] )

   merged = PlayoffTotalsMerger.merge( [ season ], { 7: landing } )

   assert merged == [ replace( season, playoff_games=22, playoff_goals=14, playoff_assists=4 ) ]


def Test_Merge_TestSplitPlayoffTotals_ExpectSummed() -> None:
   season = _season( 7, 20252026 )
   totals = [ _total( 20252026, 10, 3, 2 ), _total( 20252026, 4, 1, 1 ) ]
   landing = _landing( 7, totals )

   merged = PlayoffTotalsMerger.merge( [ season ], { 7: landing } )

   assert merged == [ replace(
      season,
      playoff_games=sum( total[ 'gamesPlayed' ] for total in totals ),
      playoff_goals=sum( total[ 'goals' ] for total in totals ),
      playoff_assists=sum( total[ 'assists' ] for total in totals ) ) ]


def Test_Merge_TestNoPlayoffs_ExpectUnchanged() -> None:
   season = _season( 7, 20252026 )
   landing = _landing( 7, [ _total( 20252026, 0, 0, 0 ) ] )

   merged = PlayoffTotalsMerger.merge( [ season ], { 7: landing } )

   assert merged == [ season ]


def Test_Merge_TestMissingLanding_ExpectUnchanged() -> None:
   season = _season( 7, 20252026 )

   merged = PlayoffTotalsMerger.merge( [ season ], {} )

   assert merged == [ season ]
