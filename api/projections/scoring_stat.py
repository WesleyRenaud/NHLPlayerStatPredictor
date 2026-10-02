from __future__ import annotations

from enum import Enum


class ScoringStat( str, Enum ):
   GOALS = 'goals'
   ASSISTS = 'assists'
   POWER_PLAY_GOALS = 'power_play_goals'
   POWER_PLAY_ASSISTS = 'power_play_assists'
   SHORT_HANDED_GOALS = 'short_handed_goals'
   SHORT_HANDED_ASSISTS = 'short_handed_assists'
