export class LookupFormController {
   static bind(form, result) {
      form.addEventListener('submit', event => {
         event.preventDefault();
         const input = form.querySelector('#player-name');
         const playerName = input.value.trim();

         if (!playerName) {
            return;
         }

         LookupFormController.render(result, playerName);
      });
   }


   static render(result, playerName) {
      result.querySelector('[data-player-name]').textContent = playerName;
      result.hidden = false;
   }
}
