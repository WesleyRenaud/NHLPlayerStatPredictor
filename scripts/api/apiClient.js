import { ApiClientHelper } from './apiClientHelper.js';


export class ApiClient {
   static async postJson(url, data = {}) {
      const response = await fetch(url, ApiClientHelper.buildJsonRequestOptions(data));
      const payload = await ApiClientHelper.readJsonResponse(response, url);

      if (!response.ok) {
         throw ApiClientHelper.buildHttpError(response, payload, url);
      }

      return payload;
   }
}
