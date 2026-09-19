from __future__ import annotations

from datetime import date
from pathlib import Path

from api.skater_position import SkaterPosition
from api.skater_season import SkaterSeason
from api.skater_season_finder import SkaterSeasonFinder
from api.skater_season_provider import SkaterSeasonProvider
from api.skater_season_store import SkaterSeasonStore
from api.team import Team


def Test_FormatTable_TestOneSeason_ExpectPaceColumns( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   SkaterSeasonStore.insert_rows(
      [ SkaterSeason(
         player_id=8478402,
         season_id=20252026,
         player_name='Connor McDavid',
         position=SkaterPosition.CENTER,
         birth_date=date( 1997, 1, 13 ),
         age=28.7,
         team=Team.EDMONTON_OILERS,
         games_played=82,
         goals=48,
         assists=90,
         points=138,
         schedule_games=82,
         pace_games=84,
         g_pace=49.170731707317074,
         a_pace=92.1951219512195,
         p_pace=141.3658536585366,
         gp_share=1.0 ) ],
      db_path=db_path )
   rows = SkaterSeasonProvider.seasons_for_name( 'Connor McDavid', db_path=db_path )
   table = SkaterSeasonFinder.format_table( rows )

   assert 'Connor McDavid (C, #8478402)' in table
   assert '2025-26' in table
   assert 'G/84' in table
   assert '141.4' in table
