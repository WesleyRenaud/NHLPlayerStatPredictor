import assert from 'node:assert/strict';
import test from 'node:test';

import { ApiClient } from '../../../scripts/api/apiClient.js';
import { PlayerNamesClient } from '../../../scripts/api/playerNamesClient.js';


test('Test_List_TestCachedFetch_ExpectSingleRequest', async () => {
   const stubNames = [ 'Stub Alpha', 'Stub Beta' ];
   let calls = 0;
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.namesPromise = null;
   ApiClient.postJson = async () => {
      calls += 1;
      return { names: stubNames };
   };

   try {
      assert.deepEqual(await PlayerNamesClient.list(), stubNames);
      assert.deepEqual(await PlayerNamesClient.list(), stubNames);
      assert.equal(calls, 1);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.namesPromise = null;
   }
});


test('Test_FetchNames_TestInvalidPayload_ExpectEmpty', async () => {
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.namesPromise = null;
   ApiClient.postJson = async () => ( { players: [] } );

   try {
      assert.deepEqual(await PlayerNamesClient.fetchNames(), []);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.namesPromise = null;
   }
});


test('Test_FetchNames_TestFailedRequest_ExpectEmpty', async () => {
   const originalPostJson = ApiClient.postJson;
   PlayerNamesClient.namesPromise = null;
   ApiClient.postJson = async () => {
      throw new Error('network');
   };

   try {
      assert.deepEqual(await PlayerNamesClient.fetchNames(), []);
   } finally {
      ApiClient.postJson = originalPostJson;
      PlayerNamesClient.namesPromise = null;
   }
});
