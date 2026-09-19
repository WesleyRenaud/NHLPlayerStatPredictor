import { PlayerNamesClient } from '../api/playerNamesClient.js';
import { LookupFormController } from '../lookup/lookupFormController.js';
import { PlayerNameAutocompleteController } from '../lookup/playerNameAutocompleteController.js';


export class LookupBootstrap {
   static start() {
      PlayerNamesClient.list();
      LookupFormController.bind(
         document.querySelector('#lookup-form'),
         document.querySelector('#projection')
      );
      PlayerNameAutocompleteController.bind({
         inputEl: document.querySelector('#player-name'),
         resultsEl: document.querySelector('#player-name-results'),
      });
   }


   static {
      document.addEventListener('DOMContentLoaded', () => {
         LookupBootstrap.start();
      });
   }
}
