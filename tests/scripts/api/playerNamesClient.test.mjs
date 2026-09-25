import assert from 'node:assert/strict';
import test from 'node:test';

import { ApiClient } from '../../../scripts/api/apiClient.js';
import { PlayerNamesClient } from '../../../scripts/api/playerNamesClient.js';
import { PlayerSearchSummary } from '../../../scripts/api/playerSearchSummary.js';


test('Test_List_TestCachedFetch_ExpectSingleRequest', async () => {
   const stubPlayer = {
      playerId: 1,
      playerName: 'Stub Alpha',
      firstSeason: '2020-21',
   };
   const stubPlayers = [PlayerSearchSummary.normalize(stubPlayer)];
   let calls = 0;
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.playersPromise = null;
   ApiClient.postJson = async () => {
      calls += 1;
      return [stubPlayer];
   };

   try {
      const first = await PlayerNamesClient.list();
      const second = await PlayerNamesClient.list();

      assert.deepEqual(first, stubPlayers);
      assert.deepEqual(second, stubPlayers);
      assert.equal(calls, 1);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.playersPromise = null;
   }
});


test('Test_FetchPlayers_TestInvalidPayload_ExpectEmpty', async () => {
   const payload = { names: [] };
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.playersPromise = null;
   ApiClient.postJson = async () => payload;

   try {
      const players = await PlayerNamesClient.fetchPlayers();

      assert.deepEqual(players, []);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.playersPromise = null;
   }
});


test('Test_FetchPlayers_TestFailedRequest_ExpectEmpty', async () => {
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.playersPromise = null;
   ApiClient.postJson = async () => {
      throw new Error('network');
   };

   try {
      const players = await PlayerNamesClient.fetchPlayers();

      assert.deepEqual(players, []);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.playersPromise = null;
   }
});
