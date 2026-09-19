import assert from 'node:assert/strict';
import test from 'node:test';

import { LookupFormController } from '../../../scripts/lookup/lookupFormController.js';
import { PlayerNameBinder } from '../../../scripts/lookup/playerNameBinder.js';
import { PlayerSearchLabel } from '../../../scripts/lookup/playerSearchLabel.js';
import { ProjectionClient } from '../../../scripts/api/projectionClient.js';


function classList() {
   const names = new Set();
   return {
      add(name) {
         names.add(name);
      },
      remove(name) {
         names.delete(name);
      },
      contains(name) {
         return names.has(name);
      },
      toggle(name, on) {
         if (on) {
            names.add(name);
         } else {
            names.delete(name);
         }
      },
   };
}


function resultElement() {
   const nodes = {
      '[data-player-name]': { textContent: '' },
      '[data-player-meta]': { textContent: '' },
      '[data-goals]': { textContent: '' },
      '[data-assists]': { textContent: '' },
      '[data-points]': { textContent: '' },
      '[data-games-played]': { textContent: '' },
   };
   return {
      hidden: true,
      classList: classList(),
      offsetWidth: 0,
      querySelector(selector) {
         return nodes[selector];
      },
      nodes,
   };
}


function lookupForm() {
   const inputAttributes = {};
   const buttonAttributes = {};
   const input = {
      value: '',
      dataset: {},
      classList: classList(),
      offsetWidth: 0,
      listeners: {},
      addEventListener(name, handler) {
         this.listeners[name] = handler;
      },
      setAttribute(name, value) {
         inputAttributes[name] = value;
      },
      removeAttribute(name) {
         delete inputAttributes[name];
      },
      getAttribute(name) {
         return inputAttributes[name];
      },
   };
   const error = { hidden: true };
   const button = {
      classList: classList(),
      offsetWidth: 0,
      disabled: false,
      setAttribute(name, value) {
         buttonAttributes[name] = value;
      },
      getAttribute(name) {
         return buttonAttributes[name];
      },
   };
   const nodes = {
      '#player-name': input,
      '#lookup-error': error,
      'button[type="submit"]': button,
   };
   const listeners = {};
   return {
      input,
      error,
      button,
      querySelector(selector) {
         return nodes[selector];
      },
      addEventListener(name, handler) {
         listeners[name] = handler;
      },
      submit() {
         return listeners.submit({ preventDefault() {} });
      },
   };
}


test('Test_Render_TestPlayerAndProjection_ExpectNameMetaAndStats', () => {
   const player = {
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const projection = {
      goals: 12,
      assists: 34,
      points: 46,
      gamesPlayed: 70,
   };
   const result = resultElement();
   LookupFormController.render(result, player, projection);
   assert.equal(result.nodes['[data-player-name]'].textContent, player.playerName);
   assert.equal(
      result.nodes['[data-player-meta]'].textContent,
      PlayerSearchLabel.meta(player)
   );
   assert.equal(result.nodes['[data-goals]'].textContent, projection.goals);
   assert.equal(result.nodes['[data-assists]'].textContent, projection.assists);
   assert.equal(result.nodes['[data-points]'].textContent, projection.points);
   assert.equal(result.nodes['[data-games-played]'].textContent, projection.gamesPlayed);
   assert.equal(result.hidden, false);
});


test('Test_Bind_TestUnboundPlayer_ExpectError', async () => {
   const form = lookupForm();
   LookupFormController.bind(form, resultElement());
   await form.submit();
   assert.equal(form.error.hidden, false);
   assert.equal(form.input.classList.contains('is-invalid'), true);
   assert.equal(form.input.getAttribute('aria-invalid'), 'true');
   assert.equal(form.button.classList.contains('is-invalid'), true);
});


test('Test_Bind_TestPlayer_ExpectErrorClearedAndRendered', async t => {
   const player = {
      playerId: 7,
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const projection = {
      goals: 12,
      assists: 34,
      points: 46,
      gamesPlayed: 70,
   };
   const original = ProjectionClient.get;
   ProjectionClient.get = async () => projection;
   t.after(() => {
      ProjectionClient.get = original;
   });
   const form = lookupForm();
   const result = resultElement();
   PlayerNameBinder.bind(form.input, player);
   LookupFormController.bind(form, result);
   LookupFormController.showError(form);
   await form.submit();
   assert.equal(form.error.hidden, true);
   assert.equal(form.input.classList.contains('is-invalid'), false);
   assert.equal(form.button.classList.contains('is-invalid'), false);
   assert.equal(form.button.classList.contains('is-busy'), false);
   assert.equal(form.button.disabled, false);
   assert.equal(form.button.getAttribute('aria-busy'), 'false');
   assert.equal(result.nodes['[data-player-name]'].textContent, player.playerName);
   assert.equal(result.hidden, false);
   assert.equal(result.classList.contains('is-updated'), true);
});


test('Test_Bind_TestInput_ExpectErrorCleared', () => {
   const form = lookupForm();
   LookupFormController.bind(form, resultElement());
   LookupFormController.showError(form);
   form.input.listeners.input();
   assert.equal(form.error.hidden, true);
   assert.equal(form.input.classList.contains('is-invalid'), false);
   assert.equal(form.button.classList.contains('is-invalid'), false);
});


test('Test_Bind_TestPendingProjection_ExpectBusyButton', async t => {
   const player = {
      playerId: 7,
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const projection = {
      goals: 12,
      assists: 34,
      points: 46,
      gamesPlayed: 70,
   };
   let resolveGet;
   const original = ProjectionClient.get;
   ProjectionClient.get = () => new Promise(resolve => {
      resolveGet = resolve;
   });
   t.after(() => {
      ProjectionClient.get = original;
   });
   const form = lookupForm();
   const result = resultElement();
   PlayerNameBinder.bind(form.input, player);
   LookupFormController.bind(form, result);
   const pending = form.submit();
   assert.equal(form.button.disabled, true);
   assert.equal(form.button.classList.contains('is-busy'), true);
   assert.equal(form.button.getAttribute('aria-busy'), 'true');
   resolveGet(projection);
   await pending;
   assert.equal(form.button.disabled, false);
   assert.equal(form.button.classList.contains('is-busy'), false);
   assert.equal(result.classList.contains('is-updated'), true);
});
