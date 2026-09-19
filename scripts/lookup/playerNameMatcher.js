export class PlayerNameMatcher {
   static MAX_RESULTS = 12;


   static filter(players, query, maxResults = PlayerNameMatcher.MAX_RESULTS) {
      const normalizedQuery = String(query).trim().toLowerCase();

      if (!normalizedQuery) {
         return [];
      }

      const startsWithMatches = [];
      const containsMatches = [];

      players.forEach(player => {
         const lower = String(player.playerName).toLowerCase();

         if (lower.startsWith(normalizedQuery)) {
            startsWithMatches.push(player);
         } else if (lower.includes(normalizedQuery)) {
            containsMatches.push(player);
         }
      });

      return [...startsWithMatches, ...containsMatches].slice(0, maxResults);
   }
}
