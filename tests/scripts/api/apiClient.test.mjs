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
   const url = ApiRoutes.GET_PLAYER_NAMES;
   const method = 'POST';
   let captured;
   globalThis.fetch = async (requestedUrl, options) => {
      captured = { url: requestedUrl, options };
      return _mockResponse({
         text: JSON.stringify(payload),
      });
   };

   const parsed = await ApiClient.postJson(url);

   assert.equal(captured.url, url);
   assert.equal(captured.options.method, method);
   assert.deepEqual(parsed, payload);
});


test('Test_PostJson_TestHttpError_ExpectApiClientError', async () => {
   const status = 500;
   const statusText = 'Internal Server Error';
   const url = '/stub';
   const errorName = 'ApiClientError';
   globalThis.fetch = async () => _mockResponse({
      ok: false,
      status,
      statusText,
      text: '{"error":"Stub failure"}',
   });

   const rejected = ApiClient.postJson(url);

   await assert.rejects(rejected, error => {
      assert.equal(error.name, errorName);
      assert.equal(error.status, status);
      return true;
   });
});
