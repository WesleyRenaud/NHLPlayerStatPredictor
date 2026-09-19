import { PlayerNameBinder } from './playerNameBinder.js';


export class LookupFormController {
   static bind(form, result) {
      form.addEventListener('submit', event => {
         event.preventDefault();
         const input = form.querySelector('#player-name');

         if (!PlayerNameBinder.playerId(input)) {
            return;
         }

         LookupFormController.render(result, PlayerNameBinder.label(input));
      });
   }


   static render(result, playerName) {
      result.querySelector('[data-player-name]').textContent = playerName;
      result.hidden = false;
   }
}
