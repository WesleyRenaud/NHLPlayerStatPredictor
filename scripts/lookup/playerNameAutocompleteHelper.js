export class PlayerNameAutocompleteHelper {
   static DEFAULT_DELAY_MS = 180;


   static debounce(fn, delay = PlayerNameAutocompleteHelper.DEFAULT_DELAY_MS) {
      let timer = null;

      return (...args) => {
         clearTimeout(timer);
         timer = setTimeout(() => fn(...args), delay);
      };
   }
}
