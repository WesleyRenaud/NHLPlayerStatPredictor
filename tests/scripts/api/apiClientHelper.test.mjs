import assert from 'node:assert/strict';
import test from 'node:test';

import { ApiClientHelper } from '../../../scripts/api/apiClientHelper.js';


test('Test_BuildJsonRequestOptions_TestPayload_ExpectPostJson', () => {
   const payload = { name: 'Stub Alpha' };
   assert.deepEqual(ApiClientHelper.buildJsonRequestOptions(payload), {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json',
         'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
   });
});


test('Test_ParseJsonText_TestEmptyAndValid_ExpectObject', () => {
   assert.deepEqual(ApiClientHelper.parseJsonText(''), {});
   assert.deepEqual(ApiClientHelper.parseJsonText('  '), {});
   assert.deepEqual(ApiClientHelper.parseJsonText('{"ok":true}'), { ok: true });
});


test('Test_BuildHttpError_TestPayloadMessage_ExpectApiClientError', () => {
   const error = ApiClientHelper.buildHttpError(
      { status: 400, statusText: 'Bad Request' },
      { error: '  Stub error  ' },
      '/stub'
   );

   assert.equal(error.name, 'ApiClientError');
   assert.equal(error.message, 'Stub error (/stub)');
   assert.equal(error.status, 400);
   assert.equal(error.url, '/stub');
});


test('Test_ReadJsonResponse_TestValidBody_ExpectParsed', async () => {
   const payload = await ApiClientHelper.readJsonResponse({
      text: async () => '{"names":[]}',
   }, '/stub');

   assert.deepEqual(payload, { names: [] });
});
