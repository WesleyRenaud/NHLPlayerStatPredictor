from __future__ import annotations

import pytest

import api.ingest.roster_skater_ingester as roster_skater_ingester
from api.ingest.roster_skater_ingester import RosterSkaterIngester
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_BuildRows_TestStandingsAndRoster_ExpectBuilderRows(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first_team = list( Team )[ Position.FIRST ]
   second_team = list( Team )[ Position.SECOND ]
   position = list( SkaterPosition )[ Position.FIRST ]
   expected = [
      RosterSkater( 1, 'First Skater', position, first_team ),
      RosterSkater( 2, 'Second Skater', position, second_team ),
   ]
   captured: list[ tuple[ Team, dict[ str, object ] ] ] = []
   payloads = {
      first_team.value: { 'team': first_team.value },
      second_team.value: { 'team': second_team.value },
   }
   monkeypatch.setattr(
      roster_skater_ingester.NhlClient,
      'standings',
      lambda force=False: {
         'standings': [
            { 'teamAbbrev': { 'default': second_team.value } },
            { 'teamAbbrev': { 'default': first_team.value } },
            { 'teamAbbrev': { 'default': first_team.value } },
         ]
      } )
   monkeypatch.setattr(
      roster_skater_ingester.NhlClient,
      'roster',
      lambda team_abbrev, force=False: payloads[ team_abbrev ] )
   monkeypatch.setattr(
      roster_skater_ingester.RosterSkaterBuilder,
      'build',
      lambda team, payload: captured.append( ( team, payload ) ) or [
         expected[ Position.FIRST if team == first_team else Position.SECOND ]
      ] )
   rows = RosterSkaterIngester.build_rows()
   assert rows == expected
   assert [ team for team, payload in captured ] == [ first_team, second_team ]
   assert [ payload for team, payload in captured ] == [
      payloads[ first_team.value ],
      payloads[ second_team.value ],
   ]
