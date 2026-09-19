import { ApiClient } from './apiClient.js';
import { ApiRoutes } from './apiRoutes.js';
import { PlayerNamesApiNormalizer } from './playerNamesApiNormalizer.js';


export class PlayerNamesClient {
   static playersPromise = null;


   static list() {
      if (PlayerNamesClient.playersPromise == null) {
         PlayerNamesClient.playersPromise = PlayerNamesClient.fetchPlayers();
      }

      return PlayerNamesClient.playersPromise;
   }


   static async fetchPlayers() {
      try {
         const response = await ApiClient.postJson(ApiRoutes.GET_PLAYER_NAMES);
         return PlayerNamesApiNormalizer.normalizePlayers(response);
      } catch (error) {
         return [];
      }
   }
}
