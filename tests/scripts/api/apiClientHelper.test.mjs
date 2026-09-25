import assert from 'node:assert/strict';
import test from 'node:test';

import { ApiClientHelper } from '../../../scripts/api/apiClientHelper.js';


test('Test_BuildJsonRequestOptions_TestPayload_ExpectPostJson', () => {
   const payload = { name: 'Stub Alpha' };
   const method = 'POST';
   const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
   };

   const options = ApiClientHelper.buildJsonRequestOptions(payload);

   assert.deepEqual(options, {
      method,
      headers,
      body: JSON.stringify(payload),
   });
});


test('Test_ParseJsonText_TestEmpty_ExpectEmptyObject', () => {
   const text = '';

   const parsed = ApiClientHelper.parseJsonText(text);

   assert.deepEqual(parsed, {});
});


test('Test_ParseJsonText_TestWhitespace_ExpectEmptyObject', () => {
   const text = '  ';

   const parsed = ApiClientHelper.parseJsonText(text);

   assert.deepEqual(parsed, {});
});


test('Test_ParseJsonText_TestValid_ExpectObject', () => {
   const payload = { ok: true };
   const text = JSON.stringify(payload);

   const parsed = ApiClientHelper.parseJsonText(text);

   assert.deepEqual(parsed, payload);
});


test('Test_BuildHttpError_TestPayloadMessage_ExpectApiClientError', () => {
   const status = 400;
   const statusText = 'Bad Request';
   const message = 'Stub error';
   const url = '/stub';
   const response = { status, statusText };
   const payload = { error: `  ${message}  ` };

   const error = ApiClientHelper.buildHttpError(response, payload, url);

   assert.equal(error.name, 'ApiClientError');
   assert.equal(error.message, `${message} (${url})`);
   assert.equal(error.status, status);
   assert.equal(error.url, url);
});


test('Test_ReadJsonResponse_TestValidBody_ExpectParsed', async () => {
   const payload = { names: [] };
   const url = '/stub';
   const response = {
      text: async () => JSON.stringify(payload),
   };

   const parsed = await ApiClientHelper.readJsonResponse(response, url);

   assert.deepEqual(parsed, payload);
});
