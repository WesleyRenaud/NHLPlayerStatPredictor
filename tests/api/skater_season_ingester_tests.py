from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from api.aging_curve_fitter import AgingCurveFitter
from api.aging_factor_store import AgingFactorStore
from api.league_factor_fitter import LeagueFactorFitter
from api.league_factor_store import LeagueFactorStore
from api.nhl_skater_season import NhlSkaterSeason
from api.paths import Paths
from api.recency_decay_fitter import RecencyDecayFitter
from api.recency_weight_store import RecencyWeightStore
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skater_bio import SkaterBio
from api.skater_position import SkaterPosition
import api.skater_season_ingester as skater_season_ingester
from api.skater_season_ingester import SkaterSeasonIngester
from api.skater_summary import SkaterSummary
from api.team import Team


def _season( season_id: int, p_pace: float ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=1,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=p_pace,
      gp_share=1.0 )


def Test_BuildRows_TestRegularSeason_ExpectPacedTotals() -> None:
   team = list( Team )[ Position.FIRST ]
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         8478402,
         'Connor McDavid',
         list( SkaterPosition )[ Position.FIRST ],
         [ team ],
         82,
         44,
         79,
         123 ) ],
      [ SkaterBio( 8478402, date( 1997, 1, 13 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert len( rows ) == 1
   row = rows[ Position.FIRST ]
   assert row.g_pace == 44 / 82 * 84
   assert row.a_pace == 79 / 82 * 84
   assert row.p_pace == 123 / 82 * 84
   assert row.pace_games == 84
   assert row.team == team


def Test_BuildRows_TestShortSeason_ExpectPacedTotals() -> None:
   rows = SkaterSeasonIngester.build_rows(
      [ SkaterSummary(
         1,
         'Sample Player',
         list( SkaterPosition )[ Position.SECOND ],
         [ list( Team )[ Position.SECOND ] ],
         4,
         1,
         1,
         2 ) ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert rows[ Position.FIRST ].p_pace == 2 / 4 * 84


def Test_BuildRows_TestMissingBio_ExpectSkipped() -> None:
   team = list( Team )[ Position.FIRST ]
   position = list( SkaterPosition )[ Position.FIRST ]
   rows = SkaterSeasonIngester.build_rows(
      [
         SkaterSummary( 1, 'Has Bio', position, [ team ], 82, 1, 1, 2 ),
         SkaterSummary( 2, 'No Bio', position, [ team ], 82, 1, 1, 2 ),
      ],
      [ SkaterBio( 1, date( 1999, 1, 1 ) ) ],
      SeasonLength( 20242025, 82, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      84 )

   assert len( rows ) == 1
   assert rows[ Position.FIRST ].player_id == 1


def Test_Seasons_TestBeforeFirstSeason_ExpectExcluded(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( skater_season_ingester.Config, 'FIRST_SEASON_ID', 20102011 )
   meta = SkaterSeasonIngester._seasons(
      [
         SeasonLength( 20092010, 82, date( 2009, 10, 1 ), date( 2010, 4, 15 ) ),
         SeasonLength( 20102011, 82, date( 2010, 10, 7 ), date( 2011, 4, 17 ) ),
         SeasonLength( 20112012, 82, date( 2011, 10, 6 ), date( 2012, 4, 10 ) ),
      ] )

   assert [ item.season_id for item in meta ] == [ 20102011, 20112012 ]


def Test_Main_TestRows_ExpectInsertedAndWeightsAndFactorsStored(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   rows = [ _season( 20202021, 50.0 ), _season( 20212022, 80.0 ) ]
   db_path = tmp_path / 'skaters.sqlite'
   inserted: list[ tuple[ list[ NhlSkaterSeason ], str ] ] = []
   monkeypatch.setattr( Paths, 'DB_PATH', db_path )
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   monkeypatch.setattr(
      SkaterSeasonIngester,
      'build_all_rows',
      lambda force=False: rows )
   monkeypatch.setattr(
      skater_season_ingester.SkaterSeasonStore,
      'insert_rows',
      lambda written, path: inserted.append( ( written, path ) ) )
   monkeypatch.setattr(
      skater_season_ingester.OtherLeagueSeasonIngester,
      'build_rows',
      lambda player_ids, seasons, pace_games, force=False: [] )
   monkeypatch.setattr(
      skater_season_ingester.OtherLeagueSeasonStore,
      'insert_rows',
      lambda written, path: None )
   monkeypatch.setattr(
      skater_season_ingester.NhlClient,
      'seasons',
      lambda force=False: [] )
   monkeypatch.setattr(
      skater_season_ingester.Season,
      'pace_games',
      lambda seasons: 84 )
   SkaterSeasonIngester.main()
   assert inserted == [ ( rows, str( db_path ) ) ]
   assert RecencyWeightStore.read() == RecencyDecayFitter.weights(
      RecencyDecayFitter.fit( rows ) )
   aging_factors = AgingCurveFitter.fit( rows, [] )
   assert AgingFactorStore.read() == aging_factors
   assert LeagueFactorStore.read() == LeagueFactorFitter.fit(
      rows,
      [],
      aging_factors )
