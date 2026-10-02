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
      '[data-penalty-minutes]': { textContent: '' },
      '[data-games-played]': { textContent: '' },
      '[data-shots]': { textContent: '' },
      '[data-shooting-percentage]': { textContent: '' },
      '[data-even-strength-goals]': { textContent: '' },
      '[data-even-strength-points]': { textContent: '' },
      '[data-power-play-goals]': { textContent: '' },
      '[data-power-play-points]': { textContent: '' },
      '[data-short-handed-goals]': { textContent: '' },
      '[data-short-handed-points]': { textContent: '' },
      '[data-toi]': { textContent: '' },
   };
   for (const node of Object.values(nodes)) node.classList = classList();
   const seasonNodes = Object.fromEntries(Object.keys(nodes).map(selector =>
      [selector, { textContent: '', classList: classList() }]));
   nodes['[data-projection-stats]'] = { querySelector: selector => nodes[selector] };
   nodes['[data-season-stats]'] = {
      querySelector: selector => seasonNodes[selector],
      attributes: {},
      setAttribute(name, value) { this.attributes[name] = value; },
   };
   for (const mode of ['current', 'pace']) {
      nodes[`[data-season-tab="${mode}"]`] = {
         disabled: false,
         attributes: {},
         listeners: {},
         setAttribute(name, value) { this.attributes[name] = value; },
         addEventListener(name, handler) { this.listeners[name] = handler; },
         focus() { this.focused = true; },
      };
   }
   nodes['[data-season-stats-container]'] = { hidden: true };
   return {
      hidden: true,
      classList: classList(),
      offsetWidth: 0,
      querySelector(selector) {
         return nodes[selector];
      },
      nodes,
      seasonNodes,
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
      shots: 200,
      shootingPercentage: 100 * 12 / 200,
      assists: 34,
      points: 46,
      penaltyMinutes: 18,
      gamesPlayed: 70,
      evenStrengthGoals: 6,
      evenStrengthPoints: 31,
      powerPlayGoals: 5,
      powerPlayPoints: 12,
      shortHandedGoals: 1,
      shortHandedPoints: 3,
      projectedToi: '18:30',
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
   assert.equal(
      result.nodes['[data-penalty-minutes]'].textContent,
      projection.penaltyMinutes
   );
   assert.equal(result.nodes['[data-games-played]'].textContent, projection.gamesPlayed);
   assert.equal(result.nodes['[data-shots]'].textContent, projection.shots);
   assert.equal(result.nodes['[data-shooting-percentage]'].textContent, projection.shootingPercentage.toFixed(1));
   assert.equal(result.nodes['[data-even-strength-goals]'].textContent, projection.evenStrengthGoals);
   assert.equal(result.nodes['[data-even-strength-points]'].textContent, projection.evenStrengthPoints);
   assert.equal(
      result.nodes['[data-power-play-goals]'].textContent,
      projection.powerPlayGoals
   );
   assert.equal(
      result.nodes['[data-power-play-points]'].textContent,
      projection.powerPlayPoints
   );
   assert.equal(
      result.nodes['[data-short-handed-goals]'].textContent,
      projection.shortHandedGoals
   );
   assert.equal(
      result.nodes['[data-short-handed-points]'].textContent,
      projection.shortHandedPoints
   );
   assert.equal(result.nodes['[data-toi]'].textContent, '18:30');
   assert.equal(result.hidden, false);
});


test('Test_Render_TestObservedSeason_ExpectSeparateActualAndProjectedRows', () => {
   const result = resultElement();
   const seasonStats = {
      seasonLabel: '2025-26', gamesPlayed: 80, goals: 40, assists: 60, points: 100,
      penaltyMinutes: 20, evenStrengthGoals: 30, evenStrengthPoints: 70,
      powerPlayGoals: 10, powerPlayPoints: 30, shortHandedGoals: 0, shortHandedPoints: 0,
      shots: 300, shootingPercentage: 100 * 40 / 300, timeOnIcePerGame: '22:15',
   };
   const projection = { goals: 35, seasonStats, projectedToi: '23:00' };

   LookupFormController.render(result, {}, projection);

   assert.equal(result.nodes['[data-season-stats-container]'].hidden, false);
   assert.equal(result.seasonNodes['[data-games-played]'].textContent, seasonStats.gamesPlayed);
   assert.equal(result.seasonNodes['[data-goals]'].textContent, seasonStats.goals);
   assert.equal(result.seasonNodes['[data-even-strength-points]'].textContent, seasonStats.evenStrengthPoints);
   assert.equal(result.seasonNodes['[data-shots]'].textContent, seasonStats.shots);
   assert.equal(result.seasonNodes['[data-shooting-percentage]'].textContent, seasonStats.shootingPercentage.toFixed(1));
   assert.equal(result.seasonNodes['[data-toi]'].textContent, seasonStats.timeOnIcePerGame);
   assert.equal(result.nodes['[data-goals]'].textContent, projection.goals);
   assert.equal(result.nodes['[data-toi]'].textContent, projection.projectedToi);

   LookupFormController.render(result, {}, { goals: 10, seasonStats: null });

   assert.equal(result.nodes['[data-season-stats-container]'].hidden, true);
   assert.equal(result.nodes['[data-goals]'].textContent, 10);
});


test('Test_Render_TestZeroEvenStrengthStats_ExpectZero', () => {
   const result = resultElement();

   LookupFormController.render(result, {}, { evenStrengthGoals: 0, evenStrengthPoints: 0 });

   assert.equal(result.nodes['[data-even-strength-goals]'].textContent, 0);
   assert.equal(result.nodes['[data-even-strength-points]'].textContent, 0);
});


test('Test_BindSeasonTabs_TestClickAndKeyboard_ExpectPaceSwitchAndReset', () => {
   const result = resultElement();
   const seasonStats = {
      gamesPlayed: 10, goals: 5, shots: 30, shootingPercentage: 100 * 5 / 30,
      timeOnIcePerGame: '20:00',
   };
   const gamesRemaining = 60;
   seasonStats.fullSeasonPace = {
      ...seasonStats,
      gamesPlayed: seasonStats.gamesPlayed + gamesRemaining,
      goals: seasonStats.goals / seasonStats.gamesPlayed * (seasonStats.gamesPlayed + gamesRemaining),
   };
   const projection = { goals: 20, seasonStats };
   LookupFormController.bindSeasonTabs(result);
   LookupFormController.render(result, {}, projection);
   const current = result.nodes['[data-season-tab="current"]'];
   const pace = result.nodes['[data-season-tab="pace"]'];
   pace.listeners.click();

   assert.equal(result.seasonNodes['[data-goals]'].textContent, seasonStats.fullSeasonPace.goals);
   assert.equal(result.seasonNodes['[data-games-played]'].textContent, seasonStats.fullSeasonPace.gamesPlayed);
   assert.equal(result.nodes['[data-goals]'].textContent, projection.goals);
   assert.equal(result.seasonNodes['[data-toi]'].textContent, seasonStats.timeOnIcePerGame);
   assert.equal(pace.attributes['aria-selected'], 'true');
   assert.equal(current.tabIndex, -1);
   assert.equal(result.nodes['[data-season-stats]'].attributes['aria-labelledby'], 'full-season-pace-tab');

   for (const key of ['ArrowLeft', 'Home', 'ArrowRight', 'End']) {
      let prevented = false;
      pace.listeners.keydown({ key, preventDefault() { prevented = true; } });
      assert.equal(prevented, true);
   }
   assert.equal(current.focused, true);
   assert.equal(pace.focused, true);
   LookupFormController.render(result, {}, projection);
   assert.equal(current.attributes['aria-selected'], 'true');
   assert.equal(result.seasonNodes['[data-goals]'].textContent, seasonStats.goals);
});


test('Test_BindSeasonTabs_TestUnavailablePace_ExpectDisabledTab', () => {
   const result = resultElement();
   LookupFormController.bindSeasonTabs(result);
   const seasonStats = { goals: 0, gamesPlayed: 0, fullSeasonPace: null };
   LookupFormController.render(result, {}, { seasonStats });
   const pace = result.nodes['[data-season-tab="pace"]'];
   const current = result.nodes['[data-season-tab="current"]'];

   current.listeners.keydown({ key: 'ArrowRight', preventDefault() {} });
   current.listeners.keydown({ key: 'Enter', preventDefault() { assert.fail('Unexpected key interception'); } });
   assert.equal(pace.disabled, true);
   assert.equal(current.attributes['aria-selected'], 'true');
   assert.equal(result.seasonNodes['[data-games-played]'].textContent, seasonStats.gamesPlayed);
});


test('Test_Render_TestUnavailableShotHistory_ExpectPlaceholders', () => {
   const result = resultElement();

   LookupFormController.render(result, {}, { shots: undefined, shootingPercentage: undefined });

   assert.equal(result.nodes['[data-shots]'].textContent, '—');
   assert.equal(result.nodes['[data-shooting-percentage]'].textContent, '—');
   for (const selector of ['[data-penalty-minutes]', '[data-shots]', '[data-shooting-percentage]', '[data-toi]']) {
      assert.equal(result.nodes[selector].classList.contains('is-unavailable'), true);
   }
});


test('Test_Render_TestZeroShotsAndPercentage_ExpectZero', () => {
   const result = resultElement();

   LookupFormController.render(result, {}, {});
   LookupFormController.render(result, {}, { shots: 0, shootingPercentage: 0, penaltyMinutes: 0, projectedToi: '0:00' });

   assert.equal(result.nodes['[data-shots]'].textContent, 0);
   assert.equal(result.nodes['[data-shooting-percentage]'].textContent, '0.0');
   for (const selector of ['[data-penalty-minutes]', '[data-shots]', '[data-shooting-percentage]', '[data-toi]']) {
      assert.equal(result.nodes[selector].classList.contains('is-unavailable'), false);
   }
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
      projectedToi: '18:30',
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
      projectedToi: '18:30',
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
