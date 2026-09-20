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
   assert.deepEqual(PlayerNameMatcher.filter(PLAYERS, '  '), []);
   assert.deepEqual(PlayerNameMatcher.filter(PLAYERS, ''), []);
});


test('Test_Filter_TestStartsWithBeforeContains_ExpectOrdered', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(PLAYERS, 'a'),
      PLAYERS
   );
});


test('Test_Filter_TestMaxResults_ExpectSliced', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(PLAYERS, 'a', 2),
      [PLAYERS[Position.FIRST], PLAYERS[Position.SECOND]]
   );
});


test('Test_Filter_TestContainsOnly_ExpectMatches', () => {
   assert.deepEqual(
      PlayerNameMatcher.filter(PLAYERS, 'amma'),
      [PLAYERS[Position.FOURTH]]
   );
});


test('Test_Filter_TestSharedName_ExpectBothPlayers', () => {
   const sharedName = 'Shared Skater';
   const first = { playerId: 1, playerName: sharedName };
   const second = { playerId: 2, playerName: sharedName };
   assert.deepEqual(
      PlayerNameMatcher.filter([first, second], sharedName),
      [first, second]
   );
});


test('Test_Filter_TestDiacritics_ExpectAsciiQueryMatches', () => {
   const player = { playerName: 'Viggo Björck' };
   assert.deepEqual(PlayerNameMatcher.filter([player], 'bjork'), [player]);
   assert.deepEqual(PlayerNameMatcher.filter([player], 'viggo'), [player]);
});
