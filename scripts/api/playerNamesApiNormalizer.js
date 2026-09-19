import { PlayerSearchSummary } from './playerSearchSummary.js';


export class PlayerNamesApiNormalizer {
   static normalizePlayers(response) {
      return PlayerSearchSummary.normalizeAll(response);
   }
}
