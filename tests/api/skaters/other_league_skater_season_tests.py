from __future__ import annotations

from api.aging.league_factor import LeagueFactor
from api.projections.season_pace import SeasonPace
from api.skaters.other_league_season_key import OtherLeagueSeasonKey
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.skater_season import SkaterSeason


def Test_FromRow_TestDict_ExpectSeason() -> None:
   row = OtherLeagueSkaterSeason(
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
   assert OtherLeagueSkaterSeason.from_row( {
      'PLAYER_ID': row.player_id,
      'SEASON_ID': row.season_id,
      'LEAGUE': row.league,
      'POSITION': row.position.value,
      'AGE': row.age,
      'GAMES_PLAYED': row.games_played,
      'GOALS': row.goals,
      'ASSISTS': row.assists,
      'POINTS': row.points,
      'G_PACE': row.g_pace,
      'A_PACE': row.a_pace,
   } ) == row
   assert isinstance( row, SkaterSeason )


def Test_Key_TestSeason_ExpectPlayerSeasonLeague() -> None:
   row = OtherLeagueSkaterSeason(
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
   assert row.key() == OtherLeagueSeasonKey(
      row.player_id,
      row.season_id,
      row.league )


def Test_NhlPace_TestKnownLeague_ExpectTranslated() -> None:
   row = OtherLeagueSkaterSeason(
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
   factor = LeagueFactor( row.league, 0.40 )
   assert row.nhl_pace( [ factor ] ) == SeasonPace(
      row.g_pace * factor.rate,
      row.a_pace * factor.rate )


def Test_NhlPace_TestUnknownLeague_ExpectNone() -> None:
   row = OtherLeagueSkaterSeason(
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
   assert row.nhl_pace( [] ) is None
