from __future__ import annotations

from .other_league_season_seed_table import OtherLeagueSeasonSeedTable
from .player_status_seed_table import PlayerStatusSeedTable
from .roster_skater_seed_table import RosterSkaterSeedTable
from .skater_season_seed_table import SkaterSeasonSeedTable


runtime_tables = [
   SkaterSeasonSeedTable,
   OtherLeagueSeasonSeedTable,
   PlayerStatusSeedTable,
   RosterSkaterSeedTable,
]
