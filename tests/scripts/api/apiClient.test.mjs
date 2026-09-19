import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';

import { ApiClient } from '../../../scripts/api/apiClient.js';
import { ApiRoutes } from '../../../scripts/api/apiRoutes.js';


function _mockResponse({
   ok = true,
   status = 200,
   statusText = 'OK',
   text = '{}',
} = {}) {
   return {
      ok,
      status,
      statusText,
      text: async () => text,
   };
}


afterEach(() => {
   delete globalThis.fetch;
});


test('Test_PostJson_TestValidPayload_ExpectParsedResponse', async () => {
   const payload = { names: [ 'Stub Alpha' ] };
   globalThis.fetch = async (url, options) => {
      assert.equal(url, ApiRoutes.GET_PLAYER_NAMES);
      assert.equal(options.method, 'POST');
      return _mockResponse({
         text: JSON.stringify(payload),
      });
   };

   assert.deepEqual(await ApiClient.postJson(ApiRoutes.GET_PLAYER_NAMES), payload);
});


test('Test_PostJson_TestHttpError_ExpectApiClientError', async () => {
   globalThis.fetch = async () => _mockResponse({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      text: '{"error":"Stub failure"}',
   });

   await assert.rejects(
      async () => {
         await ApiClient.postJson('/stub');
      },
      error => {
         assert.equal(error.name, 'ApiClientError');
         assert.equal(error.status, 500);
         return true;
      }
   );
});
