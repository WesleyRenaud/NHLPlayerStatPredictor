import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNameMatcher } from '../../../scripts/lookup/playerNameMatcher.js';


const NAMES = [ 'Alpha Skater', 'Amur Skater', 'Beta Skater', 'Gamma Skater' ];


test('Test_Filter_TestBlankQuery_ExpectEmpty', () => {
   assert.deepEqual(PlayerNameMatcher.filter(NAMES, '  '), []);
   assert.deepEqual(PlayerNameMatcher.filter(NAMES, ''), []);
});


test('Test_Filter_TestStartsWithBeforeContains_ExpectOrdered', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(NAMES, 'a'),
      [ 'Alpha Skater', 'Amur Skater', 'Beta Skater', 'Gamma Skater' ]
   );
});


test('Test_Filter_TestMaxResults_ExpectSliced', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(NAMES, 'a', 2),
      [ 'Alpha Skater', 'Amur Skater' ]
   );
});


test('Test_Filter_TestContainsOnly_ExpectMatches', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(NAMES, 'amma'),
      [ 'Gamma Skater' ]
   );
});
