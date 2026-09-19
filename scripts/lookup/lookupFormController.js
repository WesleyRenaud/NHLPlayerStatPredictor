import { PlayerNameBinder } from './playerNameBinder.js';
import { PlayerSearchLabel } from './playerSearchLabel.js';
import { ProjectionClient } from '../api/projectionClient.js';


export class LookupFormController {
   static bind(form, result) {
      const input = form.querySelector('#player-name');

      form.addEventListener('submit', async event => {
         event.preventDefault();
         const player = PlayerNameBinder.player(input);

         if (!player) {
            LookupFormController.showError(form);
            return;
         }

         LookupFormController.clearError(form);
         LookupFormController.setBusy(form, true);

         try {
            const projection = await ProjectionClient.get(player.playerId);
            LookupFormController.render(result, player, projection);
         } finally {
            LookupFormController.setBusy(form, false);
         }
      });

      input.addEventListener('input', () => {
         LookupFormController.clearError(form);
      });
   }


   static showError(form) {
      const input = form.querySelector('#player-name');
      const button = form.querySelector('button[type="submit"]');
      form.querySelector('#lookup-error').hidden = false;
      input.classList.add('is-invalid');
      input.setAttribute('aria-invalid', 'true');
      button.classList.remove('is-invalid');
      button.offsetWidth;
      button.classList.add('is-invalid');
   }


   static clearError(form) {
      const input = form.querySelector('#player-name');
      form.querySelector('#lookup-error').hidden = true;
      input.classList.remove('is-invalid');
      input.removeAttribute('aria-invalid');
      form.querySelector('button[type="submit"]').classList.remove('is-invalid');
   }


   static setBusy(form, busy) {
      const button = form.querySelector('button[type="submit"]');
      button.disabled = busy;
      button.classList.toggle('is-busy', busy);
      button.setAttribute('aria-busy', String(busy));
   }


   static render(result, player, projection) {
      result.querySelector('[data-player-name]').textContent = player.playerName;
      result.querySelector('[data-player-meta]').textContent =
         PlayerSearchLabel.meta(player);
      result.querySelector('[data-goals]').textContent = projection.goals;
      result.querySelector('[data-assists]').textContent = projection.assists;
      result.querySelector('[data-points]').textContent = projection.points;
      result.querySelector('[data-games-played]').textContent = projection.gamesPlayed;
      result.hidden = false;
      result.classList.remove('is-updated');
      result.offsetWidth;
      result.classList.add('is-updated');
   }
}
