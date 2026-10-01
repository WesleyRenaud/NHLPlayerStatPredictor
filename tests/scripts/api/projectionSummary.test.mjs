import assert from 'node:assert/strict';
import test from 'node:test';

import { ProjectionSummary } from '../../../scripts/api/projectionSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const goals = 12;
   const assists = 34;
   const points = 46;
   const penaltyMinutes = 18;
   const gamesPlayed = 70;
   const powerPlayGoals = 5;
   const powerPlayPoints = 12;
   const row = {
      goals,
      assists,
      points,
      penaltyMinutes,
      gamesPlayed,
      powerPlayGoals,
      powerPlayPoints,
   };

   const projection = ProjectionSummary.normalize(row);

   assert.equal(projection.goals, goals);
   assert.equal(projection.assists, assists);
   assert.equal(projection.points, points);
   assert.equal(projection.penaltyMinutes, penaltyMinutes);
   assert.equal(projection.gamesPlayed, gamesPlayed);
   assert.equal(projection.powerPlayGoals, powerPlayGoals);
   assert.equal(projection.powerPlayPoints, powerPlayPoints);
});


test('Test_Normalize_TestMissingPowerPlayStats_ExpectUndefined', () => {
   const projection = ProjectionSummary.normalize({});

   assert.equal(projection.powerPlayGoals, undefined);
   assert.equal(projection.powerPlayPoints, undefined);
   assert.equal(projection.penaltyMinutes, undefined);
});
