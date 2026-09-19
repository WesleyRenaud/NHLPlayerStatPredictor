const PLAYERS = new WeakMap();


export class PlayerNameBinder {
   static bind(inputEl, player) {
      inputEl.value = player.playerName;
      inputEl.dataset.playerId = String(player.playerId);
      PLAYERS.set(inputEl, player);
   }


   static clear(inputEl) {
      delete inputEl.dataset.playerId;
      PLAYERS.delete(inputEl);
   }


   static playerId(inputEl) {
      return inputEl.dataset.playerId;
   }


   static player(inputEl) {
      return PLAYERS.get(inputEl);
   }
}
