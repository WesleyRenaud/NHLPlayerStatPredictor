import assert from 'node:assert/strict';
import test from 'node:test';

import { PlayerHistoryController } from '../../../scripts/lookup/playerHistoryController.js';


function element(document) {
   return {
      ownerDocument: document, children: [], listeners: {}, textContent: '',
      classList: { toggle(name, unavailable) { this[name] = unavailable; } },
      attributes: {},
      setAttribute(name, value) { this.attributes[name] = value; },
      append(child) { child.parent = this; this.children.push(child); },
      replaceChildren() { this.children = []; },
      remove() { this.parent.children.pop(); },
      get lastElementChild() { return this.children.at(-1); },
      addEventListener(name, handler) { this.listeners[name] = handler; },
   };
}


function dialogElement() {
   const document = { createElement() { return element(document); } };
   const dialog = element(document);
   dialog.nodes = {
      '#history-player-name': element(document),
      '[data-history-seasons]': element(document),
      '[data-history-career]': element(document),
   };
   dialog.nodes['[data-history-career]'].append(element(document));
   dialog.querySelector = selector => dialog.nodes[selector];
   dialog.sortButtons = PlayerHistoryController.statColumns.map(key => ({
      ...element(document), dataset: { historySort: key }, parentElement: element(document),
   }));
   dialog.querySelectorAll = () => dialog.sortButtons;
   dialog.showModal = () => { dialog.open = true; };
   dialog.close = () => { dialog.open = false; };
   dialog.getBoundingClientRect = () => ({ left: 10, right: 100, top: 10, bottom: 100 });
   return dialog;
}


test('Test_Render_TestSeasonAndCareer_ExpectSafeCellsAndNoDuplicatedTotals', () => {
   const dialog = dialogElement();
   const season = { seasonLabel: '2025-26', league: 'NHL', team: '<Team>', goals: 0, shootingPercentage: 12.34 };
   const history = { playerName: '<Player>', seasons: [season], career: { goals: 10 } };
   for (let render = 0; render < 2; render++) PlayerHistoryController.render(dialog, history);

   assert.equal(dialog.nodes['#history-player-name'].textContent, history.playerName);
   const rows = dialog.nodes['[data-history-seasons]'].children;
   assert.equal(rows.length, history.seasons.length);
   assert.equal(rows[0].children[2].textContent, season.team);
   const columns = PlayerHistoryController.statColumns;
   assert.equal(rows[0].children[3 + columns.indexOf('goals')].textContent, season.goals);
   assert.equal(rows[0].children[3 + columns.indexOf('shootingPercentage')].textContent, season.shootingPercentage.toFixed(1));
   assert.equal(rows[0].children[3 + columns.indexOf('shots')].textContent, '—');
   assert.equal(dialog.nodes['[data-history-career]'].children.length, 1 + columns.length);
});


test('Test_Bind_TestTriggerAndBackdrop_ExpectModalOpenAndOutsideDismissal', () => {
   const dialog = dialogElement();
   const trigger = element(dialog.ownerDocument);
   const history = { playerName: 'Player', seasons: [], career: {} };
   PlayerHistoryController.bind(trigger, dialog, () => history);
   trigger.listeners.click();
   assert.equal(dialog.open, true);
   dialog.listeners.click({ target: trigger, clientX: 0, clientY: 0 });
   assert.equal(dialog.open, true);
   dialog.listeners.click({ target: dialog, clientX: 50, clientY: 50 });
   assert.equal(dialog.open, true);
   dialog.listeners.click({ target: dialog, clientX: 0, clientY: 0 });
   assert.equal(dialog.open, false);
});


test('Test_Render_TestNoNhlCareer_ExpectHiddenCareerRowAndResetForVeteran', () => {
   const dialog = dialogElement();
   const history = { playerName: 'Player', seasons: [], career: { gamesPlayed: 20 } };
   PlayerHistoryController.render(dialog, history);
   const row = dialog.nodes['[data-history-career]'];

   PlayerHistoryController.render(dialog, { ...history, career: null });
   assert.equal(row.hidden, true);
   assert.equal(row.children.length, 1);

   PlayerHistoryController.render(dialog, history);
   assert.equal(row.hidden, false);
   assert.equal(row.children.length, 1 + PlayerHistoryController.statColumns.length);
});


for (const key of PlayerHistoryController.statColumns) {
   test(`Test_Sort_Test${key}_ExpectDescendingThenAscendingWithoutCareerChange`, () => {
      const dialog = dialogElement();
      const first = { seasonLabel: '2024-25', [key]: key === 'timeOnIcePerGame' ? '9:59' : 5 };
      const second = { seasonLabel: '2025-26', [key]: key === 'timeOnIcePerGame' ? '10:00' : 10 };
      const history = { playerName: 'Player', seasons: [first, second], career: { goals: 20 } };
      const trigger = element(dialog.ownerDocument);
      PlayerHistoryController.bind(trigger, dialog, () => history);
      trigger.listeners.click();
      const career = dialog.nodes['[data-history-career]'];
      const careerCells = [...career.children];
      const button = dialog.sortButtons.find(item => item.dataset.historySort === key);
      const displayedSeasons = () => dialog.nodes['[data-history-seasons]'].children.map(row => row.children[0].textContent);

      button.listeners.click();
      assert.deepEqual(displayedSeasons(), [second.seasonLabel, first.seasonLabel]);
      assert.equal(button.parentElement.attributes['aria-sort'], 'descending');
      button.listeners.click();
      assert.deepEqual(displayedSeasons(), [first.seasonLabel, second.seasonLabel]);
      assert.equal(button.parentElement.attributes['aria-sort'], 'ascending');
      assert.deepEqual(career.children, careerCells);
      assert.deepEqual(history.seasons, [first, second]);
   });
}


test('Test_Sort_TestMissingAndTiedValues_ExpectStableTiesMissingLastAndReset', () => {
   const dialog = dialogElement();
   const seasons = [
      { seasonLabel: 'missing', goals: null, assists: 0 },
      { seasonLabel: 'first tie', goals: 5, assists: 10 },
      { seasonLabel: 'second tie', goals: 5, assists: 20 },
      { seasonLabel: 'zero', goals: 0, assists: 30 },
   ];
   const history = { playerName: 'Player', seasons, career: {} };
   PlayerHistoryController.render(dialog, history);
   const displayedSeasons = () => dialog.nodes['[data-history-seasons]'].children.map(row => row.children[0].textContent);

   PlayerHistoryController.sort(dialog, 'goals');
   assert.deepEqual(displayedSeasons(), ['first tie', 'second tie', 'zero', 'missing']);
   PlayerHistoryController.sort(dialog, 'goals');
   assert.deepEqual(displayedSeasons(), ['zero', 'first tie', 'second tie', 'missing']);
   PlayerHistoryController.sort(dialog, 'assists');
   assert.deepEqual(displayedSeasons(), ['zero', 'second tie', 'first tie', 'missing']);
   const goalsButton = dialog.sortButtons.find(item => item.dataset.historySort === 'goals');
   assert.equal(goalsButton.parentElement.attributes['aria-sort'], 'none');

   PlayerHistoryController.render(dialog, history);
   assert.deepEqual(displayedSeasons(), seasons.map(season => season.seasonLabel));
   assert.ok(dialog.sortButtons.every(button => button.parentElement.attributes['aria-sort'] === 'none'));
});
