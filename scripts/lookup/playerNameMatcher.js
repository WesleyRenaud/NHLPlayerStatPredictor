export class PlayerNameMatcher {
   static MAX_RESULTS = 12;


   static filter(names, query, maxResults = PlayerNameMatcher.MAX_RESULTS) {
      const normalizedQuery = String(query).trim().toLowerCase();

      if (!normalizedQuery) {
         return [];
      }

      const startsWithMatches = [];
      const containsMatches = [];

      names.forEach(name => {
         const lower = String(name).toLowerCase();

         if (lower.startsWith(normalizedQuery)) {
            startsWithMatches.push(name);
         } else if (lower.includes(normalizedQuery)) {
            containsMatches.push(name);
         }
      });

      return [...startsWithMatches, ...containsMatches].slice(0, maxResults);
   }
}
