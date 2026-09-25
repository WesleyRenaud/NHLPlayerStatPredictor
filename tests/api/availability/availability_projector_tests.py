from __future__ import annotations

from datetime import date

from api.availability.availability_projector import AvailabilityProjector
from api.availability.games_share import GamesShare
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season(
      season_id: int,
      gp_share: float | None,
      games_played: int = 82 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=season_id,
      player_name='Stub',
      position=SkaterPosition( 'D' ),
      birth_date=date( 1997, 1, 13 ),
      age=28.7,
      team=list( Team )[ Position.FIRST ],
      games_played=games_played,
      goals=0,
      assists=0,
      points=0,
      schedule_games=1,
      pace_games=1,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      gp_share=gp_share )


def Test_Resolve_TestWeightedShares_ExpectAverage() -> None:
   recent_share = GamesShare.FULL
   older_share = 0.4
   recent_weight = 0.75
   older_weight = 0.25
   target = 20262027
   seasons = [ _season( 20252026, recent_share ), _season( 20242025, older_share ) ]
   weights = [
      RecencyWeight( Position.FIRST, recent_weight ),
      RecencyWeight( Position.SECOND, older_weight ),
   ]

   share = AvailabilityProjector.resolve( seasons, weights, target )

   assert share == (
      recent_weight * recent_share + older_weight * older_share
   ) / ( recent_weight + older_weight )


def Test_Resolve_TestMissingLag_ExpectRenormalized() -> None:
   share = 0.5
   present_weight = 0.75
   missing_weight = 0.25
   target = 20262027
   seasons = [ _season( 20252026, share ) ]
   weights = [
      RecencyWeight( Position.FIRST, present_weight ),
      RecencyWeight( Position.SECOND, missing_weight ),
   ]

   resolved = AvailabilityProjector.resolve( seasons, weights, target )

   assert resolved == share


def Test_Resolve_TestSkippedYear_ExpectRenormalizedWeights() -> None:
   recent_share = GamesShare.FULL
   older_share = 0.4
   skipped_weight = 0.5
   recent_weight = 0.3
   older_weight = 0.2
   target = 20262027
   seasons = [ _season( 20242025, recent_share ), _season( 20232024, older_share ) ]
   weights = [
      RecencyWeight( Position.FIRST, skipped_weight ),
      RecencyWeight( Position.SECOND, recent_weight ),
      RecencyWeight( Position.THIRD, older_weight ),
   ]

   resolved = AvailabilityProjector.resolve( seasons, weights, target )

   assert resolved == (
      recent_weight * recent_share + older_weight * older_share
   ) / ( recent_weight + older_weight )


def Test_Resolve_TestEmpty_ExpectFull() -> None:
   target = 20262027
   seasons: list[ NhlSkaterSeason ] = []
   weights = [ RecencyWeight( Position.FIRST, 1.0 ) ]

   share = AvailabilityProjector.resolve( seasons, weights, target )

   assert share == GamesShare.FULL


def Test_Resolve_TestMissingShare_ExpectFull() -> None:
   target = 20262027
   seasons = [ _season( 20252026, None ) ]
   weights = [ RecencyWeight( Position.FIRST, 1.0 ) ]

   share = AvailabilityProjector.resolve( seasons, weights, target )

   assert share == GamesShare.FULL


def Test_Resolve_TestInjuredNhlYear_ExpectShare() -> None:
   share = 0.07
   games_played = 6
   target = 20262027
   seasons = [ _season( 20252026, share, games_played=games_played ) ]
   weights = [ RecencyWeight( Position.FIRST, 1.0 ) ]

   resolved = AvailabilityProjector.resolve( seasons, weights, target )

   assert resolved == share
