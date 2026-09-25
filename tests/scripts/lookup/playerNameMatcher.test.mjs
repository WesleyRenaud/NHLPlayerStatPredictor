import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNameMatcher } from '../../../scripts/lookup/playerNameMatcher.js';
import { Position } from '../../../scripts/shared/enums/position.js';


function player(playerName) {
   return { playerName };
}


const PLAYERS = [
   player('Alpha Skater'),
   player('Amur Skater'),
   player('Beta Skater'),
   player('Gamma Skater'),
];


test('Test_Filter_TestBlankQuery_ExpectEmpty', () => {
   const query = '  ';

   const filtered = PlayerNameMatcher.filter(PLAYERS, query);

   assert.deepEqual(filtered, []);
});


test('Test_Filter_TestEmptyQuery_ExpectEmpty', () => {
   const query = '';

   const filtered = PlayerNameMatcher.filter(PLAYERS, query);

   assert.deepEqual(filtered, []);
});


test('Test_Filter_TestStartsWithBeforeContains_ExpectOrdered', () => {
   const query = 'a';

   const filtered = PlayerNameMatcher.filter(PLAYERS, query);

   assert.deepEqual(filtered, PLAYERS);
});


test('Test_Filter_TestMaxResults_ExpectSliced', () => {
   const query = 'a';
   const maxResults = 2;

   const filtered = PlayerNameMatcher.filter(PLAYERS, query, maxResults);

   assert.deepEqual(
      filtered,
      [PLAYERS[Position.FIRST], PLAYERS[Position.SECOND]]
   );
});


test('Test_Filter_TestContainsOnly_ExpectMatches', () => {
   const query = 'amma';

   const filtered = PlayerNameMatcher.filter(PLAYERS, query);

   assert.deepEqual(filtered, [PLAYERS[Position.FOURTH]]);
});


test('Test_Filter_TestSharedName_ExpectBothPlayers', () => {
   const sharedName = 'Shared Skater';
   const first = { playerId: 1, playerName: sharedName };
   const second = { playerId: 2, playerName: sharedName };
   const players = [first, second];

   const filtered = PlayerNameMatcher.filter(players, sharedName);

   assert.deepEqual(filtered, players);
});


test('Test_Filter_TestDiacritics_ExpectAsciiQueryMatches', () => {
   const player = { playerName: 'Viggo Björck' };
   const query = 'bjork';

   const filtered = PlayerNameMatcher.filter([player], query);

   assert.deepEqual(filtered, [player]);
});


test('Test_Filter_TestDiacritics_ExpectFirstNameMatches', () => {
   const player = { playerName: 'Viggo Björck' };
   const query = 'viggo';

   const filtered = PlayerNameMatcher.filter([player], query);

   assert.deepEqual(filtered, [player]);
});


test('Test_Filter_TestMixedCaseCk_ExpectQueryMatches', () => {
   const player = { playerName: 'Stub McKenna' };
   const query = 'mcke';

   const filtered = PlayerNameMatcher.filter([player], query);

   assert.deepEqual(filtered, [player]);
});


test('Test_Filter_TestMixedCaseCk_ExpectCasedQueryMatches', () => {
   const player = { playerName: 'Stub McKenna' };
   const query = 'McKe';

   const filtered = PlayerNameMatcher.filter([player], query);

   assert.deepEqual(filtered, [player]);
});
