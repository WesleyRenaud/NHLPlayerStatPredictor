from __future__ import annotations

from api.aging.league_factor import LeagueFactor
from api.projections.season_pace import SeasonPace
from api.skaters.other_league_season_key import OtherLeagueSeasonKey
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason


def Test_FromRow_TestDict_ExpectSeason() -> None:
   season = OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )

   loaded = OtherLeagueSkaterSeason.from_row( {
      'PLAYER_ID': season.player_id,
      'SEASON_ID': season.season_id,
      'LEAGUE': season.league,
      'POSITION': season.position.value,
      'AGE': season.age,
      'GAMES_PLAYED': season.games_played,
      'GOALS': season.goals,
      'ASSISTS': season.assists,
      'POINTS': season.points,
      'G_PACE': season.g_pace,
      'A_PACE': season.a_pace,
   } )

   assert loaded == season
   assert isinstance( loaded, SkaterSeason )


def Test_Key_TestSeason_ExpectPlayerSeasonLeague() -> None:
   season = OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )

   key = season.key()

   assert key == OtherLeagueSeasonKey(
      season.player_id,
      season.season_id,
      season.league )


def Test_NhlPace_TestKnownLeague_ExpectTranslated() -> None:
   season = OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )
   rate = 0.40
   factor = LeagueFactor( season.league, rate )

   pace = season.nhl_pace( [ factor ] )

   assert pace == SeasonPace(
      season.g_pace * factor.rate,
      season.a_pace * factor.rate )


def Test_NhlPace_TestUnknownLeague_ExpectNone() -> None:
   season = OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )
   factors: list[ LeagueFactor ] = []

   pace = season.nhl_pace( factors )

   assert pace is None
