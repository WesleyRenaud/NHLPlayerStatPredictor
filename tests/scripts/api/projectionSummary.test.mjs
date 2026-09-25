import assert from 'node:assert/strict';
import test from 'node:test';

import { ProjectionSummary } from '../../../scripts/api/projectionSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const goals = 12;
   const assists = 34;
   const points = 46;
   const gamesPlayed = 70;
   const row = { goals, assists, points, gamesPlayed };

   const projection = ProjectionSummary.normalize(row);

   assert.equal(projection.goals, goals);
   assert.equal(projection.assists, assists);
   assert.equal(projection.points, points);
   assert.equal(projection.gamesPlayed, gamesPlayed);
});
