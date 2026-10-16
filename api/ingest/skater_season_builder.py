from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from ..config import Config
from ..draft_class import DraftClass
from .nhl_client import NhlClient
from ..season import Season
from ..season_length import SeasonLength
from .skater_game_log import SkaterGameLog
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_bio import SkaterBio
from ..skaters.skater_game import SkaterGame
from ..skaters.skater_season_key import SkaterSeasonKey
from ..skaters.skater_summary import SkaterSummary
from ..skaters.team import Team


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
         pace_games: int,
         games_by_player: dict[ int, list[ SkaterGame ] ] ) -> list[ NhlSkaterSeason ]:
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
         age = DraftClass.age( birth_date, season.season_id )
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
            penalty_minutes=summary.penalty_minutes,
            schedule_games=season.number_of_games,
            pace_games=pace_games,
            g_pace=Season.pace( goals, games_played, pace_games ),
            a_pace=Season.pace( assists, games_played, pace_games ),
            p_pace=Season.pace( points, games_played, pace_games ),
            gp_share=gp_share,
            power_play_goals=summary.power_play_goals,
            power_play_points=summary.power_play_points,
            short_handed_goals=summary.short_handed_goals,
            short_handed_points=summary.short_handed_points,
            even_strength_goals=summary.even_strength_goals,
            even_strength_points=summary.even_strength_points,
            shots=summary.shots,
            games=games_by_player[ summary.player_id ] ) )

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
      summaries = NhlClient.skater_summary( season.season_id, force=force )
      return cls.build_rows(
         summaries,
         NhlClient.skater_bios( season.season_id, force=force ),
         season,
         pace_games,
         cls._games_by_player( season.season_id, summaries, force ) )


   @classmethod
   def _games_by_player(
         cls,
         season_id: int,
         summaries: list[ SkaterSummary ],
         force: bool ) -> dict[ int, list[ SkaterGame ] ]:
      logs: dict[ int, list[ SkaterGameLog ] ] = {
         summary.player_id: []
         for summary in summaries
      }

      for team in Team:
         for row in NhlClient.skater_games( season_id, team.value, force ):
            log = SkaterGameLog.from_row( row )

            if log is None or log.player_id not in logs:
               continue

            logs[ log.player_id ].append( log )

      games: dict[ int, list[ SkaterGame ] ] = {}

      for player_id, player_logs in logs.items():
         games[ player_id ] = [
            SkaterGame( game_number, log.points )
            for game_number, log in enumerate(
               SkaterGameLog.in_played_order( player_logs ),
               start=1 )
         ]

      return games


   @classmethod
   def _seasons( cls, seasons: list[ SeasonLength ] ) -> list[ SeasonLength ]:
      return sorted(
         [
            season for season in seasons
            if season.season_id >= Config.FIRST_SEASON_ID
         ],
         key=lambda season: season.season_id )
