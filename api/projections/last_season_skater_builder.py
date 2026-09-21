from __future__ import annotations

from .last_season_group import LastSeasonGroup
from .last_season_nhl_skater import LastSeasonNhlSkater
from .last_season_skater import LastSeasonSkater
from ..league_factor import LeagueFactor
from ..nhl_skater_season import NhlSkaterSeason
from ..other_league_skater_season import OtherLeagueSkaterSeason
from ..shared.enums.position import Position
from .translated_pace_averager import TranslatedPaceAverager


class LastSeasonSkaterBuilder():
   @classmethod
   def build(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> LastSeasonGroup:
      nhl_played = [ season for season in nhl_seasons if season.games_played ]
      other_played = [ season for season in other_seasons if season.games_played ]
      others_by_id = cls._others_by_id( other_played, factors )
      nhl_rows: list[ LastSeasonNhlSkater ] = []

      for nhl in nhl_played:
         nhl_rows.append( cls._from_nhl(
            nhl,
            others_by_id.pop( nhl.player_id, [] ),
            factors ) )

      other_rows = [
         cls._from_other( others, factors )
         for others in others_by_id.values() ]
      return LastSeasonGroup( nhl_rows, other_rows )


   @classmethod
   def _others_by_id(
         cls,
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> dict[ int, list[ OtherLeagueSkaterSeason ] ]:
      leagues = { factor.league for factor in factors }
      others_by_id: dict[ int, list[ OtherLeagueSkaterSeason ] ] = {}

      for season in other_seasons:
         if season.league in leagues:
            others_by_id.setdefault( season.player_id, [] ).append( season )

      return others_by_id


   @classmethod
   def _from_nhl(
         cls,
         nhl: NhlSkaterSeason,
         others: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> LastSeasonNhlSkater:
      pace, games = TranslatedPaceAverager.year( nhl, others, factors )
      return LastSeasonNhlSkater( nhl.player_id, games, pace, nhl.team )


   @classmethod
   def _from_other(
         cls,
         others: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> LastSeasonSkater:
      pace, games = TranslatedPaceAverager.year( None, others, factors )
      return LastSeasonSkater( others[ Position.FIRST ].player_id, games, pace )
