from __future__ import annotations

from .aging_curve_fitter import AgingCurveFitter
from .aging_factor_store import AgingFactorStore
from .config import Config
from .nhl_client import NhlClient
from .paths import Paths
from .recency_decay_fitter import RecencyDecayFitter
from .recency_weight_store import RecencyWeightStore
from .season import Season
from .season_length import SeasonLength
from .skater_bio import SkaterBio
from .skater_season import SkaterSeason
from .skater_season_key import SkaterSeasonKey
from .skater_season_store import SkaterSeasonStore
from .skater_summary import SkaterSummary


class SkaterSeasonIngester():
   @classmethod
   def main( cls, force: bool = False ) -> None:
      rows = cls.build_all_rows( force=force )
      SkaterSeasonStore.insert_rows( rows, str( Paths.DB_PATH ) )
      RecencyWeightStore.write(
         RecencyDecayFitter.weights( RecencyDecayFitter.fit( rows ) ) )
      AgingFactorStore.write( AgingCurveFitter.fit( rows ) )
      print( f'Ingested { len( rows ) } skater-seasons.' )


   @classmethod
   def build_all_rows( cls, force: bool = False ) -> list[ SkaterSeason ]:
      seasons = NhlClient.seasons( force=force )
      pace_games = Season.pace_games( seasons )
      rows: list[ SkaterSeason ] = []
      seen: set[ SkaterSeasonKey ] = set()

      for season in cls._seasons( seasons ):
         print( f'Fetching skaters { Season.label( season.season_id ) }...' )
         season_rows = cls.build_rows(
            NhlClient.skater_summary( season.season_id, force=force ),
            NhlClient.skater_bios( season.season_id, force=force ),
            season,
            pace_games )

         for row in season_rows:
            key = row.key()

            if key in seen:
               continue

            seen.add( key )
            rows.append( row )

      return rows


   @classmethod
   def build_rows(
         cls,
         summaries: list[ SkaterSummary ],
         bios: list[ SkaterBio ],
         season: SeasonLength,
         pace_games: int ) -> list[ SkaterSeason ]:
      bios_by_player = { bio.player_id: bio for bio in bios }
      rows: list[ SkaterSeason ] = []

      for summary in summaries:
         if summary.player_id not in bios_by_player:
            continue

         bio = bios_by_player[ summary.player_id ]
         games_played = float( summary.games_played )
         goals = float( summary.goals )
         assists = float( summary.assists )
         points = float( summary.points )
         birth_date = bio.birth_date
         age = Season.age_on( birth_date, season.start_date )
         gp_share = (
            games_played / float( season.number_of_games )
            if season.number_of_games else None )

         rows.append( SkaterSeason(
            player_id=summary.player_id,
            season_id=season.season_id,
            player_name=summary.player_name,
            position=summary.position,
            birth_date=birth_date,
            age=age,
            team=Season.primary_team( summary.team_abbrevs ),
            games_played=summary.games_played,
            goals=summary.goals,
            assists=summary.assists,
            points=summary.points,
            schedule_games=season.number_of_games,
            pace_games=pace_games,
            g_pace=Season.pace( goals, games_played, pace_games ),
            a_pace=Season.pace( assists, games_played, pace_games ),
            p_pace=Season.pace( points, games_played, pace_games ),
            gp_share=gp_share ) )

      return rows


   @classmethod
   def _seasons( cls, seasons: list[ SeasonLength ] ) -> list[ SeasonLength ]:
      return sorted(
         [
            season for season in seasons
            if season.season_id >= Config.FIRST_SEASON_ID
         ],
         key=lambda season: season.season_id )


if __name__ == '__main__':
   SkaterSeasonIngester.main()
