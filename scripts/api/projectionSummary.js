import { ValueNormalizer } from './valueNormalizer.js';


export class ProjectionSummary {
   static normalize(value) {
      const row = ValueNormalizer.asObject(value);
      return {
         goals: ValueNormalizer.asFiniteNumber(row.goals),
         assists: ValueNormalizer.asFiniteNumber(row.assists),
         points: ValueNormalizer.asFiniteNumber(row.points),
         gamesPlayed: ValueNormalizer.asFiniteNumber(row.gamesPlayed),
      };
   }
}
