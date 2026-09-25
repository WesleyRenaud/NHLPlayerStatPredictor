from __future__ import annotations

from datetime import date

from .nhl_client import NhlClient
from ..season import Season
from ..season_length import SeasonLength
from ..shared.enums.position import Position
from ..skaters.club_league import ClubLeague
from ..skaters.other_league_season_key import OtherLeagueSeasonKey
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_position import SkaterPosition
from ..types import Types


class OtherLeagueSeasonBuilder():
   @classmethod
   def build(
         cls,
         landing: Types.JsonObject,
         seasons: list[ SeasonLength ],
         pace_games: int ) -> list[ OtherLeagueSkaterSeason ]:
      player_id = int( landing[ 'playerId' ] )
      position = SkaterPosition( str( landing[ 'position' ] ) )
      birth_date = date.fromisoformat(
         str( landing[ 'birthDate' ] ).split( 'T' )[ Position.FIRST ] )

      combined: dict[ OtherLeagueSeasonKey, OtherLeagueSkaterSeason ] = {}
      by_season_id = { season.season_id: season for season in seasons }

      for raw in cls._season_totals( landing ):
         parsed = cls._parse_total(
            player_id,
            position,
            birth_date,
            raw,
            by_season_id )

         if parsed is None:
            continue

         key = parsed.key()
         combined[ key ] = cls._adding( combined.get( key ), parsed )

      return [
         cls._paced( season, pace_games )
         for season in sorted(
            combined.values(),
            key=lambda season: ( season.season_id, season.league ) )
         if season.games_played
      ]


   @classmethod
   def _adding(
         cls,
         current: OtherLeagueSkaterSeason | None,
         incoming: OtherLeagueSkaterSeason ) -> OtherLeagueSkaterSeason:
      if current is None:
         return incoming

      return OtherLeagueSkaterSeason(
         player_id=incoming.player_id,
         season_id=incoming.season_id,
         league=incoming.league,
         position=incoming.position,
         age=incoming.age,
         games_played=current.games_played + incoming.games_played,
         goals=current.goals + incoming.goals,
         assists=current.assists + incoming.assists,
         points=current.points + incoming.points,
         g_pace=0.0,
         a_pace=0.0 )


   @classmethod
   def _paced(
         cls,
         season: OtherLeagueSkaterSeason,
         pace_games: int ) -> OtherLeagueSkaterSeason:
      games_played = float( season.games_played )
      return OtherLeagueSkaterSeason(
         player_id=season.player_id,
         season_id=season.season_id,
         league=season.league,
         position=season.position,
         age=season.age,
         games_played=season.games_played,
         goals=season.goals,
         assists=season.assists,
         points=season.points,
         g_pace=Season.pace( float( season.goals ), games_played, pace_games ),
         a_pace=Season.pace( float( season.assists ), games_played, pace_games ) )


   @classmethod
   def _parse_total(
         cls,
         player_id: int,
         position: SkaterPosition,
         birth_date: date,
         raw: Types.JsonObject,
         by_season_id: dict[ int, SeasonLength ] ) -> OtherLeagueSkaterSeason | None:
      league = str( raw[ 'leagueAbbrev' ] )

      if not ClubLeague.contains( league ):
         return None

      if not raw.get( 'gamesPlayed' ):
         return None

      games_played = int( raw[ 'gamesPlayed' ] )

      season_id = int( raw[ 'season' ] )
      season = by_season_id.get( season_id )

      if season is None:
         return None

      return OtherLeagueSkaterSeason(
         player_id=player_id,
         season_id=season_id,
         league=league,
         position=position,
         age=Season.age_on( birth_date, season.start_date ),
         games_played=games_played,
         goals=int( raw[ 'goals' ] ),
         assists=int( raw[ 'assists' ] ),
         points=int( raw[ 'points' ] ),
         g_pace=0.0,
         a_pace=0.0 )


   @classmethod
   def _season_totals( cls, landing: Types.JsonObject ) -> Types.JsonObjectList:
      raw_rows = landing.get( 'seasonTotals' ) or []

      if not isinstance( raw_rows, list ):
         return []

      return [
         row for row in raw_rows
         if isinstance( row, dict )
         and row[ 'gameTypeId' ] == NhlClient.REGULAR_SEASON_GAME_TYPE_ID
      ]
