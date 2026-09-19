import { PlayerNameBinder } from './playerNameBinder.js';
import { PlayerSearchLabel } from './playerSearchLabel.js';
import { ProjectionClient } from '../api/projectionClient.js';


export class LookupFormController {
   static bind(form, result) {
      form.addEventListener('submit', async event => {
         event.preventDefault();
         const player = PlayerNameBinder.player(form.querySelector('#player-name'));

         if (!player) {
            return;
         }

         const projection = await ProjectionClient.get(player.playerId);
         LookupFormController.render(result, player, projection);
      });
   }


   static render(result, player, projection) {
      result.querySelector('[data-player-name]').textContent = player.playerName;
      result.querySelector('[data-player-meta]').textContent =
         PlayerSearchLabel.meta(player);
      result.querySelector('[data-goals]').textContent = projection.goals;
      result.querySelector('[data-assists]').textContent = projection.assists;
      result.querySelector('[data-points]').textContent = projection.points;
      result.hidden = false;
   }
}
