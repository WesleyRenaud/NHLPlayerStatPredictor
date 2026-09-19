import assert from 'node:assert/strict';
import test from 'node:test';

import { LookupFormController } from '../../../scripts/lookup/lookupFormController.js';
import { PlayerSearchLabel } from '../../../scripts/lookup/playerSearchLabel.js';


function resultElement() {
   const nodes = {
      '[data-player-name]': { textContent: '' },
      '[data-player-meta]': { textContent: '' },
   };
   return {
      hidden: true,
      querySelector(selector) {
         return nodes[selector];
      },
      nodes,
   };
}


test('Test_Render_TestPlayer_ExpectNameThenMeta', () => {
   const player = {
      playerName: 'Stub Alpha',
      position: 'POS',
      team: 'TM',
      firstSeason: '2018-19',
   };
   const result = resultElement();
   LookupFormController.render(result, player);
   assert.equal(result.nodes['[data-player-name]'].textContent, player.playerName);
   assert.equal(
      result.nodes['[data-player-meta]'].textContent,
      PlayerSearchLabel.meta(player)
   );
   assert.equal(result.hidden, false);
});
