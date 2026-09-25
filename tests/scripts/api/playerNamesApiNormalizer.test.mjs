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
   const players = [stubPlayer];

   const normalized = PlayerNamesApiNormalizer.normalizePlayers(players);

   assert.deepEqual(normalized, [PlayerSearchSummary.normalize(stubPlayer)]);
});


test('Test_NormalizePlayers_TestMissing_ExpectEmpty', () => {
   const response = {};

   const normalized = PlayerNamesApiNormalizer.normalizePlayers(response);

   assert.deepEqual(normalized, []);
});


test('Test_NormalizePlayers_TestNull_ExpectEmpty', () => {
   const response = null;

   const normalized = PlayerNamesApiNormalizer.normalizePlayers(response);

   assert.deepEqual(normalized, []);
});
