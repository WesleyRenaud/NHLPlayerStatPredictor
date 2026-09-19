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
      assert.deepEqual(await PlayerNamesClient.list(), stubPlayers);
      assert.deepEqual(await PlayerNamesClient.list(), stubPlayers);
      assert.equal(calls, 1);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.playersPromise = null;
   }
});


test('Test_FetchPlayers_TestInvalidPayload_ExpectEmpty', async () => {
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.playersPromise = null;
   ApiClient.postJson = async () => ( { names: [] } );

   try {
      assert.deepEqual(await PlayerNamesClient.fetchPlayers(), []);
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
      assert.deepEqual(await PlayerNamesClient.fetchPlayers(), []);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.playersPromise = null;
   }
});
