export class ApiClientHelper {
   static buildJsonRequestOptions(data = {}) {
      return {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
         },
         body: JSON.stringify(data),
      };
   }


   static parseJsonText(text = '') {
      const trimmedText = String(text).trim();

      if (!trimmedText) {
         return {};
      }

      return JSON.parse(trimmedText);
   }


   static buildHttpError(response, payload, url) {
      const message =
         typeof payload?.error === 'string' && payload.error.trim()
            ? payload.error.trim()
            : `Request failed: ${response.status} ${response.statusText}`.trim();
      const error = new Error(`${message} (${url})`);
      error.name = 'ApiClientError';
      error.status = response.status;
      error.statusText = response.statusText;
      error.url = url;
      error.payload = payload;
      return error;
   }


   static async readJsonResponse(response, url) {
      const text = await response.text();

      try {
         return ApiClientHelper.parseJsonText(text);
      } catch {
         throw new Error(`Invalid JSON response from ${url}`);
      }
   }
}
