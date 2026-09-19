import { PlayerNameBinder } from './playerNameBinder.js';
import { PlayerSearchLabel } from './playerSearchLabel.js';


export class LookupFormController {
   static bind(form, result) {
      form.addEventListener('submit', event => {
         event.preventDefault();
         const player = PlayerNameBinder.player(form.querySelector('#player-name'));

         if (!player) {
            return;
         }

         LookupFormController.render(result, player);
      });
   }


   static render(result, player) {
      result.querySelector('[data-player-name]').textContent = player.playerName;
      result.querySelector('[data-player-meta]').textContent =
         PlayerSearchLabel.meta(player);
      result.hidden = false;
   }
}
