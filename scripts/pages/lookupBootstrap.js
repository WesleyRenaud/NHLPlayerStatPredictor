import { PlayerNamesClient } from '../api/playerNamesClient.js';
import { LookupFormController } from '../lookup/lookupFormController.js';
import { PlayerNameAutocompleteController } from '../lookup/playerNameAutocompleteController.js';
import { PlayerHistoryController } from '../lookup/playerHistoryController.js';


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
      const result = document.querySelector('#projection');
      PlayerHistoryController.bind(
         result.querySelector('[data-player-name]'),
         document.querySelector('#player-history'),
         () => LookupFormController.playerHistories.get(result)
      );
   }


   static {
      document.addEventListener('DOMContentLoaded', () => {
         LookupBootstrap.start();
      });
   }
}
