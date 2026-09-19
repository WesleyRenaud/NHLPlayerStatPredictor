import { ValueNormalizer } from './valueNormalizer.js';


export class PlayerSearchSummary {
   static normalize(value) {
      const row = ValueNormalizer.asObject(value);
      return {
         playerId: Number(row.playerId),
         playerName: ValueNormalizer.asTrimmedString(row.playerName),
         position: ValueNormalizer.asTrimmedString(row.position),
         team: ValueNormalizer.asTrimmedString(row.team),
         firstSeason: ValueNormalizer.asTrimmedString(row.firstSeason),
      };
   }


   static isComplete(player) {
      return (
         player.playerName &&
         Number.isFinite(player.playerId) &&
         player.firstSeason
      );
   }


   static normalizeAll(values) {
      return ValueNormalizer.asArray(values)
         .map(PlayerSearchSummary.normalize)
         .filter(PlayerSearchSummary.isComplete);
   }
}
