import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerNameBinder } from '../../../scripts/lookup/playerNameBinder.js';


test('Test_Bind_TestPlayer_ExpectValueAndPlayer', () => {
   const player = {
      playerId: 7,
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const inputEl = {
      value: '',
      dataset: {},
   };
   PlayerNameBinder.bind(inputEl, player);
   assert.equal(inputEl.value, player.playerName);
   assert.equal(PlayerNameBinder.playerId(inputEl), String(player.playerId));
   assert.equal(PlayerNameBinder.player(inputEl), player);
});


test('Test_Clear_TestDataset_ExpectRemoved', () => {
   const player = {
      playerId: 7,
      playerName: 'Stub Alpha',
   };
   const inputEl = {
      value: 'Stub Alpha',
      dataset: {
         playerId: '7',
      },
   };
   PlayerNameBinder.bind(inputEl, player);
   PlayerNameBinder.clear(inputEl);
   assert.equal(PlayerNameBinder.playerId(inputEl), undefined);
   assert.equal(PlayerNameBinder.player(inputEl), undefined);
});


test('Test_Player_TestUnbound_ExpectUndefined', () => {
   const inputEl = {
      value: 'Stub Alpha',
      dataset: {},
   };
   assert.equal(PlayerNameBinder.player(inputEl), undefined);
});
