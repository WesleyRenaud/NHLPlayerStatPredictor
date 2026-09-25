from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from ..config import Config
from .nhl_client import NhlClient
from ..season import Season
from ..season_length import SeasonLength
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_bio import SkaterBio
from ..skaters.skater_season_key import SkaterSeasonKey
from ..skaters.skater_summary import SkaterSummary


class SkaterSeasonBuilder():
   SEASON_WORKERS = 4


   @classmethod
   def build_all( cls, force: bool = False ) -> list[ NhlSkaterSeason ]:
      seasons = NhlClient.seasons( force=force )
      pace_games = Season.pace_games( seasons )
      rows: list[ NhlSkaterSeason ] = []
      seen: set[ SkaterSeasonKey ] = set()

      for season_rows in cls._season_rows( cls._seasons( seasons ), pace_games, force ):
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
         pace_games: int ) -> list[ NhlSkaterSeason ]:
      bios_by_player = { bio.player_id: bio for bio in bios }
      rows: list[ NhlSkaterSeason ] = []

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
         gp_share = games_played / float( season.number_of_games )

         rows.append( NhlSkaterSeason(
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
   def _season_rows(
         cls,
         seasons: list[ SeasonLength ],
         pace_games: int,
         force: bool ) -> list[ list[ NhlSkaterSeason ] ]:
      with ThreadPoolExecutor( max_workers=SkaterSeasonBuilder.SEASON_WORKERS ) as executor:
         return list(
            executor.map(
               lambda season: cls._rows_for_season( season, pace_games, force ),
               seasons ) )


   @classmethod
   def _rows_for_season(
         cls,
         season: SeasonLength,
         pace_games: int,
         force: bool ) -> list[ NhlSkaterSeason ]:
      print( f'Fetching skaters { Season.label( season.season_id ) }...', flush=True )
      return cls.build_rows(
         NhlClient.skater_summary( season.season_id, force=force ),
         NhlClient.skater_bios( season.season_id, force=force ),
         season,
         pace_games )


   @classmethod
   def _seasons( cls, seasons: list[ SeasonLength ] ) -> list[ SeasonLength ]:
      return sorted(
         [
            season for season in seasons
            if season.season_id >= Config.FIRST_SEASON_ID
         ],
         key=lambda season: season.season_id )
