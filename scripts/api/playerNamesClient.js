import { ApiClient } from './apiClient.js';
import { ApiRoutes } from './apiRoutes.js';
import { PlayerNamesApiNormalizer } from './playerNamesApiNormalizer.js';


export class PlayerNamesClient {
   static namesPromise = null;


   static list() {
      if (PlayerNamesClient.namesPromise == null) {
         PlayerNamesClient.namesPromise = PlayerNamesClient.fetchNames();
      }

      return PlayerNamesClient.namesPromise;
   }


   static async fetchNames() {
      try {
         const response = await ApiClient.postJson(ApiRoutes.GET_PLAYER_NAMES);
         return PlayerNamesApiNormalizer.normalizeNames(response);
      } catch (error) {
         return [];
      }
   }
}
