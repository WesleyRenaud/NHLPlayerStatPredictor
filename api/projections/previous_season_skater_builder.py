from __future__ import annotations

from ..league_factor import LeagueFactor
from ..nhl_skater_season import NhlSkaterSeason
from ..other_league_skater_season import OtherLeagueSkaterSeason
from .previous_season_group import PreviousSeasonGroup
from .previous_season_nhl_skater import PreviousSeasonNhlSkater
from .previous_season_skater import PreviousSeasonSkater
from ..shared.enums.position import Position
from .translated_pace_averager import TranslatedPaceAverager


class PreviousSeasonSkaterBuilder():
   @classmethod
   def build(
         cls,
         nhl_seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> PreviousSeasonGroup:
      nhl_played = [ season for season in nhl_seasons if season.games_played ]
      other_played = [ season for season in other_seasons if season.games_played ]
      others_by_id = cls._others_by_id( other_played, factors )
      nhl_rows: list[ PreviousSeasonNhlSkater ] = []

      for nhl in nhl_played:
         nhl_rows.append( cls._from_nhl(
            nhl,
            others_by_id.pop( nhl.player_id, [] ),
            factors ) )

      other_rows = [
         cls._previous_season_skater( others, factors )
         for others in others_by_id.values() ]
      return PreviousSeasonGroup( nhl_rows, other_rows )


   @classmethod
   def _others_by_id(
         cls,
         other_seasons: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> dict[ int, list[ OtherLeagueSkaterSeason ] ]:
      others_by_id: dict[ int, list[ OtherLeagueSkaterSeason ] ] = {}

      for season in other_seasons:
         if LeagueFactor.rate( factors, season.league ) is None:
            continue

         others_by_id.setdefault( season.player_id, [] ).append( season )

      return others_by_id


   @classmethod
   def _from_nhl(
         cls,
         nhl: NhlSkaterSeason,
         others: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> PreviousSeasonNhlSkater:
      year = TranslatedPaceAverager.year( [ nhl, *others ], factors )
      return PreviousSeasonNhlSkater(
         nhl.player_id,
         year.games,
         year.pace,
         nhl.position,
         nhl.team )


   @classmethod
   def _previous_season_skater(
         cls,
         others: list[ OtherLeagueSkaterSeason ],
         factors: list[ LeagueFactor ] ) -> PreviousSeasonSkater:
      year = TranslatedPaceAverager.year( others, factors )
      first = others[ Position.FIRST ]
      return PreviousSeasonSkater( first.player_id, year.games, year.pace, first.position )
