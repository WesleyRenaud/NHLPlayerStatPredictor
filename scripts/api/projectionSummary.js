import { ValueNormalizer } from './valueNormalizer.js';


export class ProjectionSummary {
   static normalize(value) {
      const row = ValueNormalizer.asObject(value);
      const season = row.seasonStats;
      return {
         ...ProjectionSummary.normalizeStats(row),
         projectedToi: ValueNormalizer.asTrimmedString(row.projectedToi),
         seasonStats: season == null ? null : {
            ...ProjectionSummary.normalizeStats(season),
            seasonLabel: ValueNormalizer.asTrimmedString(season.seasonLabel),
            timeOnIcePerGame: ValueNormalizer.asTrimmedString(season.timeOnIcePerGame),
         },
      };
   }


   static normalizeStats(value) {
      const row = ValueNormalizer.asObject(value);
      return {
         goals: ValueNormalizer.asFiniteNumber(row.goals),
         assists: ValueNormalizer.asFiniteNumber(row.assists),
         points: ValueNormalizer.asFiniteNumber(row.points),
         penaltyMinutes: ValueNormalizer.asFiniteNumber(row.penaltyMinutes),
         gamesPlayed: ValueNormalizer.asFiniteNumber(row.gamesPlayed),
         shots: ValueNormalizer.asFiniteNumber(row.shots),
         shootingPercentage: ValueNormalizer.asFiniteNumber(row.shootingPercentage),
         evenStrengthGoals: ValueNormalizer.asFiniteNumber(row.evenStrengthGoals),
         evenStrengthPoints: ValueNormalizer.asFiniteNumber(row.evenStrengthPoints),
         powerPlayGoals: ValueNormalizer.asFiniteNumber(row.powerPlayGoals),
         powerPlayPoints: ValueNormalizer.asFiniteNumber(row.powerPlayPoints),
         shortHandedGoals: ValueNormalizer.asFiniteNumber(row.shortHandedGoals),
         shortHandedPoints: ValueNormalizer.asFiniteNumber(row.shortHandedPoints),
      };
   }
}
