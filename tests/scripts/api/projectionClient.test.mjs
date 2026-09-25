import assert from 'node:assert/strict';
import test from 'node:test';

import { ApiClient } from '../../../scripts/api/apiClient.js';
import { ApiRoutes } from '../../../scripts/api/apiRoutes.js';
import { ProjectionClient } from '../../../scripts/api/projectionClient.js';
import { ProjectionSummary } from '../../../scripts/api/projectionSummary.js';


test('Test_Get_TestPayload_ExpectNormalizedProjection', async () => {
   const playerId = 7;
   const payload = {
      goals: 12,
      assists: 34,
      points: 46,
      gamesPlayed: 70,
   };
   let captured;
   const originalPostJson = ApiClient.postJson;
   ApiClient.postJson = async (url, data) => {
      captured = { url, data };
      return payload;
   };

   try {
      const projection = await ProjectionClient.get(playerId);

      assert.deepEqual(projection, ProjectionSummary.normalize(payload));
      assert.equal(captured.url, ApiRoutes.GET_PROJECTION);
      assert.deepEqual(captured.data, { playerId });
   } finally {
      ApiClient.postJson = originalPostJson;
   }
});
