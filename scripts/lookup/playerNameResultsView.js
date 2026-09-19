export class PlayerNameResultsView {
   static create({ inputEl, resultsEl } = {}) {
      let currentMatches = [];
      let highlightedIndex = -1;


      function renderResults(children = []) {
         resultsEl.replaceChildren(...children);
      }


      function clear() {
         renderResults();
         resultsEl.classList.remove('active');
         currentMatches = [];
         highlightedIndex = -1;
      }


      function updateHighlight() {
         const items = resultsEl.querySelectorAll('.player-name-autocomplete-item');

         items.forEach((item, index) => {
            item.classList.toggle('is-highlighted', index === highlightedIndex);

            if (index === highlightedIndex) {
               item.scrollIntoView({ block: 'nearest' });
            }
         });
      }


      function selectName(name) {
         inputEl.value = name;
         clear();
         inputEl.dispatchEvent(new Event('change', { bubbles: true }));
      }


      function render(matches) {
         currentMatches = matches;
         highlightedIndex = -1;

         if (!matches.length) {
            const empty = document.createElement('div');
            empty.className = 'player-name-autocomplete-empty';
            empty.textContent = resultsEl.dataset.empty ?? '';
            renderResults([empty]);
            resultsEl.classList.add('active');
            return;
         }

         const fragment = document.createDocumentFragment();

         matches.forEach(name => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'player-name-autocomplete-item';
            item.textContent = name;

            item.addEventListener('mousedown', event => {
               event.preventDefault();
            });

            item.addEventListener('click', () => {
               selectName(name);
            });

            fragment.appendChild(item);
         });

         renderResults([fragment]);
         resultsEl.classList.add('active');
      }


      function handleKeydown(event) {
         const hasResults =
            resultsEl.classList.contains('active') &&
            currentMatches.length > 0;

         if (event.key === 'Escape') {
            clear();
            return;
         }

         if (!hasResults) {
            return;
         }

         if (event.key === 'ArrowDown') {
            event.preventDefault();
            highlightedIndex = Math.min(highlightedIndex + 1, currentMatches.length - 1);
            updateHighlight();
            return;
         }

         if (event.key === 'ArrowUp') {
            event.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, 0);
            updateHighlight();
            return;
         }

         if (event.key === 'Enter') {
            if (highlightedIndex >= 0 && highlightedIndex < currentMatches.length) {
               event.preventDefault();
               selectName(currentMatches[highlightedIndex]);
            }
         }
      }


      return {
         clear,
         render,
         handleKeydown,
      };
   }
}
