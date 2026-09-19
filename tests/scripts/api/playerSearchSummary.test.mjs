import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerSearchSummary } from '../../../scripts/api/playerSearchSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const playerName = 'Stub Alpha';
   const firstSeason = '2023-24';
   const player = PlayerSearchSummary.normalize({
      playerId: 7,
      playerName: ` ${playerName} `,
      position: ' POS ',
      team: ' TM ',
      firstSeason: ` ${firstSeason} `,
   });
   assert.equal(player.playerId, 7);
   assert.equal(player.playerName, playerName);
   assert.equal(player.position, 'POS');
   assert.equal(player.team, 'TM');
   assert.equal(player.firstSeason, firstSeason);
});


test('Test_NormalizeAll_TestMissingName_ExpectDropped', () => {
   const complete = {
      playerId: 7,
      playerName: 'Stub Alpha',
      firstSeason: '2023-24',
   };
   assert.deepEqual(
      PlayerSearchSummary.normalizeAll([
         { playerId: 7, playerName: '', firstSeason: complete.firstSeason },
         complete,
      ]),
      [PlayerSearchSummary.normalize(complete)]
   );
});


test('Test_NormalizeAll_TestMissingPlayerId_ExpectDropped', () => {
   const complete = {
      playerId: 7,
      playerName: 'Stub Alpha',
      firstSeason: '2023-24',
   };
   assert.deepEqual(
      PlayerSearchSummary.normalizeAll([
         { playerName: complete.playerName, firstSeason: complete.firstSeason },
         complete,
      ]),
      [PlayerSearchSummary.normalize(complete)]
   );
});
