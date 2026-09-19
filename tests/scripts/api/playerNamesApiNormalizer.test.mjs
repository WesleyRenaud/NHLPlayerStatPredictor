import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNamesApiNormalizer } from '../../../scripts/api/playerNamesApiNormalizer.js';
import { PlayerSearchSummary } from '../../../scripts/api/playerSearchSummary.js';


test('Test_NormalizePlayers_TestArray_ExpectPlayers', () => {
   const stubPlayer = {
      playerId: 1,
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   assert.deepEqual(
      PlayerNamesApiNormalizer.normalizePlayers([stubPlayer]),
      [PlayerSearchSummary.normalize(stubPlayer)]
   );
});


test('Test_NormalizePlayers_TestMissing_ExpectEmpty', () => {
   assert.deepEqual(PlayerNamesApiNormalizer.normalizePlayers({}), []);
   assert.deepEqual(PlayerNamesApiNormalizer.normalizePlayers(null), []);
});
