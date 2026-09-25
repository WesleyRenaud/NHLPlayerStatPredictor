import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNameAutocompleteHelper } from '../../../scripts/lookup/playerNameAutocompleteHelper.js';


test('Test_Debounce_TestDelay_ExpectSingleCall', async () => {
   const first = 1;
   const second = 2;
   const delay = 20;
   const wait = delay * 2;
   const calls = [];
   const debounced = PlayerNameAutocompleteHelper.debounce(value => {
      calls.push(value);
   }, delay);

   debounced(first);
   debounced(second);
   await new Promise(resolve => {
      setTimeout(resolve, wait);
   });

   assert.deepEqual(calls, [ second ]);
});
