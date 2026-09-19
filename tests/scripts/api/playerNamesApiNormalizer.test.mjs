import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNamesApiNormalizer } from '../../../scripts/api/playerNamesApiNormalizer.js';


test('Test_NormalizeNames_TestArray_ExpectNames', () => {
   const stubNames = [ 'Stub Alpha', 'Stub Beta' ];
   assert.deepEqual(
      PlayerNamesApiNormalizer.normalizeNames({ names: stubNames }),
      stubNames
   );
});


test('Test_NormalizeNames_TestMissing_ExpectEmpty', () => {
   assert.deepEqual(PlayerNamesApiNormalizer.normalizeNames({}), []);
   assert.deepEqual(PlayerNamesApiNormalizer.normalizeNames(null), []);
});
