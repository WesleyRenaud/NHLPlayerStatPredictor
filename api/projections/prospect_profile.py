from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby
from typing import cast

from .draft_pick import DraftPick
from .nhl_season_games import NhlSeasonGames
from ..season import Season
from ..types import Types


@dataclass( frozen=True )
class ProspectProfile():
   player_id: int
   draft_year: int | None
   draft_pick: DraftPick
   nhl_games: list[ NhlSeasonGames ]


   def prior_games( self, target_season_id: int ) -> int:
      return sum( season.games_played for season in self.nhl_games if season.season_id < target_season_id )


   def draft_pick_before( self, target_season_id: int ) -> DraftPick:
      return (
         self.draft_pick
         if self.draft_year is not None and self.draft_year <= Season.start_year( target_season_id )
         else DraftPick( None ) )


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProspectProfile:
      year = row[ 'draft_year' ]
      pick = row[ 'draft_pick' ]
      games = cast( dict[ str, int ], row[ 'nhl_games' ] )
      return cls(
         int( row[ 'player_id' ] ),
         None if year is None else int( year ),
         DraftPick( None if pick is None else int( pick ) ),
         [ NhlSeasonGames( int( season ), int( count ) ) for season, count in games.items() ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'player_id': self.player_id,
         'draft_year': self.draft_year,
         'draft_pick': self.draft_pick.value,
         'nhl_games': { str( season.season_id ): season.games_played for season in self.nhl_games },
      }


   @classmethod
   def from_landing( cls, landing: Types.JsonObject ) -> ProspectProfile:
      draft = cast( Types.JsonObject | None, landing.get( 'draftDetails' ) )
      totals = cast( Types.JsonObjectList, landing[ 'seasonTotals' ] )
      return cls(
         int( str( landing[ 'playerId' ] ) ),
         None if draft is None else int( draft[ 'year' ] ),
         DraftPick( None if draft is None else int( draft[ 'overallPick' ] ) ),
         cls._nhl_season_games( totals ) )


   @classmethod
   def _nhl_season_games( cls, totals: Types.JsonObjectList ) -> list[ NhlSeasonGames ]:
      regular_seasons = [
         row for row in totals
         if row.get( 'leagueAbbrev' ) == 'NHL' and row.get( 'gameTypeId' ) == 2
      ]
      regular_seasons.sort( key=lambda row: int( row[ 'season' ] ) )
      games: list[ NhlSeasonGames ] = []
      for season_id, splits in groupby( regular_seasons, key=lambda row: int( row[ 'season' ] ) ):
         games_played = sum( int( split[ 'gamesPlayed' ] ) for split in splits )
         games.append( NhlSeasonGames( season_id, games_played ) )
      return games
