import { ApiClient } from './apiClient.js';
import { ApiRoutes } from './apiRoutes.js';
import { ProjectionSummary } from './projectionSummary.js';


export class ProjectionClient {
   static async get(playerId) {
      const response = await ApiClient.postJson(ApiRoutes.GET_PROJECTION, { playerId });
      return ProjectionSummary.normalize(response);
   }
}
