import { PlayerSearchLabel } from './playerSearchLabel.js';


export class PlayerNameBinder {
   static bind(inputEl, player) {
      inputEl.value = player.playerName;
      inputEl.dataset.playerId = String(player.playerId);
      inputEl.dataset.playerLabel = PlayerSearchLabel.format(player);
   }


   static clear(inputEl) {
      delete inputEl.dataset.playerId;
      delete inputEl.dataset.playerLabel;
   }


   static playerId(inputEl) {
      return inputEl.dataset.playerId;
   }


   static label(inputEl) {
      return inputEl.dataset.playerLabel;
   }
}
