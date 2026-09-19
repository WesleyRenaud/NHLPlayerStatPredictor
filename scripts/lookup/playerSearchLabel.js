import { ValueNormalizer } from '../api/valueNormalizer.js';


export class PlayerSearchLabel {
   static SEPARATOR = ' · ';
   static RANGE_SEPARATOR = ' - ';
   static PRESENT = 'Present';


   static career(player) {
      return [
         player.firstSeason,
         PlayerSearchLabel.PRESENT,
      ]
         .map(part => ValueNormalizer.asTrimmedString(part))
         .filter(part => part)
         .join(PlayerSearchLabel.RANGE_SEPARATOR);
   }


   static meta(player) {
      return [
         player.position,
         player.team,
         PlayerSearchLabel.career(player),
      ]
         .map(part => ValueNormalizer.asTrimmedString(part))
         .filter(part => part)
         .join(PlayerSearchLabel.SEPARATOR);
   }


   static format(player) {
      return [player.playerName, PlayerSearchLabel.meta(player)]
         .map(part => ValueNormalizer.asTrimmedString(part))
         .filter(part => part)
         .join(PlayerSearchLabel.SEPARATOR);
   }
}
