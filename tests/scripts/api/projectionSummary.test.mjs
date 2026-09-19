import assert from 'node:assert/strict';
import test from 'node:test';

import { ProjectionSummary } from '../../../scripts/api/projectionSummary.js';


test('Test_Normalize_TestRow_ExpectFields', () => {
   const projection = ProjectionSummary.normalize({
      goals: 12,
      assists: 34,
      points: 46,
      gamesPlayed: 70,
   });
   assert.equal(projection.goals, 12);
   assert.equal(projection.assists, 34);
   assert.equal(projection.points, 46);
   assert.equal(projection.gamesPlayed, 70);
});
