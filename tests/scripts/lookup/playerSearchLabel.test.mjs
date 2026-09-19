import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerSearchLabel } from '../../../scripts/lookup/playerSearchLabel.js';


test('Test_Meta_TestPlayer_ExpectPositionTeamAndSeason', () => {
   const player = {
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const meta = PlayerSearchLabel.meta(player);
   const career = PlayerSearchLabel.career(player);
   assert.ok(meta.includes(player.position));
   assert.ok(meta.includes(player.team));
   assert.ok(meta.includes(career));
   assert.ok(career.includes(player.firstSeason));
   assert.ok(career.includes(PlayerSearchLabel.PRESENT));
   assert.equal(meta.includes(player.playerName), false);
});


test('Test_Format_TestPlayer_ExpectNameAndMeta', () => {
   const player = {
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const label = PlayerSearchLabel.format(player);
   assert.ok(label.includes(player.playerName));
   assert.ok(label.includes(PlayerSearchLabel.meta(player)));
});
