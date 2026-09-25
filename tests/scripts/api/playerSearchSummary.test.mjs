import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerSearchSummary } from '../../../scripts/api/playerSearchSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const playerId = 7;
   const playerName = 'Stub Alpha';
   const position = 'POS';
   const team = 'TM';
   const firstSeason = '2023-24';
   const row = {
      playerId,
      playerName: ` ${playerName} `,
      position: ` ${position} `,
      team: ` ${team} `,
      firstSeason: ` ${firstSeason} `,
   };

   const player = PlayerSearchSummary.normalize(row);

   assert.equal(player.playerId, playerId);
   assert.equal(player.playerName, playerName);
   assert.equal(player.position, position);
   assert.equal(player.team, team);
   assert.equal(player.firstSeason, firstSeason);
});


test('Test_NormalizeAll_TestMissingName_ExpectDropped', () => {
   const complete = {
      playerId: 7,
      playerName: 'Stub Alpha',
      firstSeason: '2023-24',
   };
   const missingName = {
      playerId: complete.playerId,
      playerName: '',
      firstSeason: complete.firstSeason,
   };
   const rows = [missingName, complete];

   const normalized = PlayerSearchSummary.normalizeAll(rows);

   assert.deepEqual(normalized, [PlayerSearchSummary.normalize(complete)]);
});


test('Test_NormalizeAll_TestMissingPlayerId_ExpectDropped', () => {
   const complete = {
      playerId: 7,
      playerName: 'Stub Alpha',
      firstSeason: '2023-24',
   };
   const missingId = {
      playerName: complete.playerName,
      firstSeason: complete.firstSeason,
   };
   const rows = [missingId, complete];

   const normalized = PlayerSearchSummary.normalizeAll(rows);

   assert.deepEqual(normalized, [PlayerSearchSummary.normalize(complete)]);
});
