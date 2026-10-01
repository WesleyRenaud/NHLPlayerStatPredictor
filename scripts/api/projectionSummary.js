import { ValueNormalizer } from './valueNormalizer.js';


export class ProjectionSummary {
   static normalize(value) {
      const row = ValueNormalizer.asObject(value);
      return {
         goals: ValueNormalizer.asFiniteNumber(row.goals),
         assists: ValueNormalizer.asFiniteNumber(row.assists),
         points: ValueNormalizer.asFiniteNumber(row.points),
         gamesPlayed: ValueNormalizer.asFiniteNumber(row.gamesPlayed),
         powerPlayGoals: ValueNormalizer.asFiniteNumber(row.powerPlayGoals),
         powerPlayPoints: ValueNormalizer.asFiniteNumber(row.powerPlayPoints),
         shortHandedGoals: ValueNormalizer.asFiniteNumber(row.shortHandedGoals),
         shortHandedPoints: ValueNormalizer.asFiniteNumber(row.shortHandedPoints),
         projectedToi: ValueNormalizer.asTrimmedString(row.projectedToi),
      };
   }
}
