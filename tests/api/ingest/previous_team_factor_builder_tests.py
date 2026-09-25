from __future__ import annotations

from datetime import date

import pytest

import api.ingest.previous_team_factor_builder as previous_team_factor_builder
from api.ingest.previous_team_factor_builder import PreviousTeamFactorBuilder
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.team import Team
from api.team_factor.team_factor import TeamFactor


def Test_Build_TestSeasonIds_ExpectPreviousPerSeason(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first = 20242025
   second = 20252026
   team = list( Team )[ Position.FIRST ]
   first_games = 82
   second_games = 84
   pace_games = 84
   rate = 1.0
   splits: list[ int ] = []
   lengths: list[ int ] = []
   landings = {}
   slots = []
   usages = { first: {}, second: {} }
   seasons = [
      SeasonLength( first, first_games, date( 2024, 10, 4 ), date( 2025, 4, 17 ) ),
      SeasonLength( second, second_games, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ),
   ]
   monkeypatch.setattr(
      previous_team_factor_builder.NhlTeamSplitBuilder,
      'build',
      lambda landings, season_id, pace_games: splits.append( season_id ) or [] )
   monkeypatch.setattr(
      previous_team_factor_builder.TeamFactorFitter,
      'previous',
      lambda season, nhl_splits, slots, usages, season_length: (
         lengths.append( season_length )
         or [ TeamFactor( season, team, rate, [] ) ] ) )

   factors = PreviousTeamFactorBuilder.build(
      [ first, second ],
      landings,
      slots,
      usages,
      seasons,
      pace_games )

   assert factors == [
      TeamFactor( first, team, rate, [] ),
      TeamFactor( second, team, rate, [] ),
   ]
   assert splits == [ first, second ]
   assert lengths == [ first_games, second_games ]
