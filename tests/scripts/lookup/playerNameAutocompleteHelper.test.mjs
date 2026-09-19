import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNameAutocompleteHelper } from '../../../scripts/lookup/playerNameAutocompleteHelper.js';


test('Test_Debounce_TestDelay_ExpectSingleCall', async () => {
   const calls = [];
   const debounced = PlayerNameAutocompleteHelper.debounce(value => {
      calls.push(value);
   }, 20);

   debounced(1);
   debounced(2);
   await new Promise(resolve => {
      setTimeout(resolve, 40);
   });
   assert.deepEqual(calls, [ 2 ]);
});
