import assert from 'node:assert/strict';
import test from 'node:test';

import { ProjectionSummary } from '../../../scripts/api/projectionSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const goals = 12;
   const assists = 34;
   const points = 46;
   const penaltyMinutes = 18;
   const gamesPlayed = 70;
   const shots = 200;
   const shootingPercentage = 100 * goals / shots;
   const powerPlayGoals = 5;
   const powerPlayPoints = 12;
   const shortHandedGoals = 1;
   const shortHandedPoints = 3;
   const evenStrengthGoals = goals - powerPlayGoals - shortHandedGoals;
   const evenStrengthPoints = points - powerPlayPoints - shortHandedPoints;
   const row = {
      goals,
      assists,
      points,
      penaltyMinutes,
      gamesPlayed,
      shots,
      shootingPercentage,
      evenStrengthGoals,
      evenStrengthPoints,
      powerPlayGoals,
      powerPlayPoints,
      shortHandedGoals,
      shortHandedPoints,
   };

   const projection = ProjectionSummary.normalize(row);

   assert.equal(projection.goals, goals);
   assert.equal(projection.assists, assists);
   assert.equal(projection.points, points);
   assert.equal(projection.penaltyMinutes, penaltyMinutes);
   assert.equal(projection.gamesPlayed, gamesPlayed);
   assert.equal(projection.shots, shots);
   assert.equal(projection.shootingPercentage, shootingPercentage);
   assert.equal(projection.evenStrengthGoals, evenStrengthGoals);
   assert.equal(projection.evenStrengthPoints, evenStrengthPoints);
   assert.equal(projection.powerPlayGoals, powerPlayGoals);
   assert.equal(projection.powerPlayPoints, powerPlayPoints);
   assert.equal(projection.shortHandedGoals, shortHandedGoals);
   assert.equal(projection.shortHandedPoints, shortHandedPoints);
});


test('Test_Normalize_TestMissingPowerPlayStats_ExpectUndefined', () => {
   const projection = ProjectionSummary.normalize({});

   assert.equal(projection.powerPlayGoals, undefined);
   assert.equal(projection.powerPlayPoints, undefined);
   assert.equal(projection.shortHandedGoals, undefined);
   assert.equal(projection.shortHandedPoints, undefined);
   assert.equal(projection.penaltyMinutes, undefined);
   assert.equal(projection.evenStrengthGoals, undefined);
   assert.equal(projection.evenStrengthPoints, undefined);
   assert.equal(projection.shots, undefined);
   assert.equal(projection.shootingPercentage, undefined);
});


test('Test_Normalize_TestZeroShotsAndPercentage_ExpectZero', () => {
   const projection = ProjectionSummary.normalize({ shots: 0, shootingPercentage: 0 });

   assert.equal(projection.shots, 0);
   assert.equal(projection.shootingPercentage, 0);
});


test('Test_Normalize_TestZeroEvenStrengthStats_ExpectZero', () => {
   const projection = ProjectionSummary.normalize({ evenStrengthGoals: 0, evenStrengthPoints: 0 });

   assert.equal(projection.evenStrengthGoals, 0);
   assert.equal(projection.evenStrengthPoints, 0);
});
