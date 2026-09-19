import { PlayerNamesClient } from '../api/playerNamesClient.js';
import { PlayerNameAutocompleteHelper } from './playerNameAutocompleteHelper.js';
import { PlayerNameBinder } from './playerNameBinder.js';
import { PlayerNameMatcher } from './playerNameMatcher.js';
import { PlayerNameResultsView } from './playerNameResultsView.js';


export class PlayerNameAutocompleteController {
   static bind({ inputEl, resultsEl } = {}) {
      if (!inputEl || !resultsEl) {
         return { clear() {} };
      }

      const resultsView = PlayerNameResultsView.create({ inputEl, resultsEl });
      let searchRequestId = 0;

      async function performSearch() {
         const query = String(inputEl.value).trim();
         const requestId = ++searchRequestId;

         if (!query) {
            resultsView.clear();
            return;
         }

         const players = await PlayerNamesClient.list();

         if (requestId !== searchRequestId) {
            return;
         }

         resultsView.render(PlayerNameMatcher.filter(players, query));
      }

      const runSearch = PlayerNameAutocompleteHelper.debounce(() => {
         performSearch();
      });

      inputEl.addEventListener('input', () => {
         PlayerNameBinder.clear(inputEl);
         runSearch();
      });

      inputEl.addEventListener('focus', () => {
         if (!String(inputEl.value).trim()) {
            return;
         }

         performSearch();
      });

      inputEl.addEventListener('keydown', event => {
         resultsView.handleKeydown(event);
      });

      inputEl.addEventListener('blur', () => {
         setTimeout(() => {
            resultsView.clear();
         }, 150);
      });

      return {
         clear: resultsView.clear,
      };
   }
}
