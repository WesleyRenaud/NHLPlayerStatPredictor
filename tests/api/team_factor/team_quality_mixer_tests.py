from __future__ import annotations

from api.availability.games_share import GamesShare
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.team import Team
from api.team_factor.club_games import ClubGames
from api.team_factor.team_factor import TeamFactor
from api.team_factor.team_factor_skater import TeamFactorSkater
from api.team_factor.team_quality_mixer import TeamQualityMixer


def _factor( season: int, team: Team, rate: float ) -> TeamFactor:
   return TeamFactor(
      season,
      team,
      rate,
      [ TeamFactorSkater( 99, 80.0, SkaterGroup( 'F' ), GamesShare.FULL, False, None ) ] )


def Test_Resolve_TestOneClub_ExpectTeammateRate() -> None:
   team = list( Team )[ Position.FIRST ]
   season = 20252026
   player_id = 7
   factor = _factor( season, team, 1.12 )

   resolved = TeamQualityMixer.resolve(
      [ factor ],
      season,
      player_id,
      [ ClubGames( team, 50 ) ] )

   assert resolved == TeamFactor.teammate_rate(
      [ factor ],
      season,
      team,
      player_id )


def Test_Resolve_TestSplitClubs_ExpectGamesWeightedRate() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season = 20252026
   player_id = 7
   first_games = 50
   second_games = 22
   factors = [
      _factor( season, first, 0.8 ),
      _factor( season, second, 1.2 ),
   ]
   first_rate = TeamFactor.teammate_rate( factors, season, first, player_id )
   second_rate = TeamFactor.teammate_rate( factors, season, second, player_id )

   resolved = TeamQualityMixer.resolve(
      factors,
      season,
      player_id,
      [ ClubGames( first, first_games ), ClubGames( second, second_games ) ] )

   assert resolved == (
      first_rate * first_games + second_rate * second_games
   ) / ( first_games + second_games )
