import assert from 'node:assert/strict';
import test from 'node:test';

import { LookupFormController } from '../../../scripts/lookup/lookupFormController.js';
import { PlayerSearchLabel } from '../../../scripts/lookup/playerSearchLabel.js';


function resultElement() {
   const nodes = {
      '[data-player-name]': { textContent: '' },
      '[data-player-meta]': { textContent: '' },
      '[data-goals]': { textContent: '' },
      '[data-assists]': { textContent: '' },
      '[data-points]': { textContent: '' },
   };
   return {
      hidden: true,
      querySelector(selector) {
         return nodes[selector];
      },
      nodes,
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
   assert.equal(result.hidden, false);
});
