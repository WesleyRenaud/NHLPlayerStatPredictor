export class PlayerNameMatcher {
   static MAX_RESULTS = 12;


   static filter(players, query, maxResults = PlayerNameMatcher.MAX_RESULTS) {
      const normalizedQuery = PlayerNameMatcher.fold(query).trim();

      if (!normalizedQuery) {
         return [];
      }

      const startsWithMatches = [];
      const containsMatches = [];

      players.forEach(player => {
         const foldedName = PlayerNameMatcher.fold(player.playerName);

         if (foldedName.startsWith(normalizedQuery)) {
            startsWithMatches.push(player);
         } else if (foldedName.includes(normalizedQuery)) {
            containsMatches.push(player);
         }
      });

      return [...startsWithMatches, ...containsMatches].slice(0, maxResults);
   }


   static fold(value) {
      return String(value)
         .normalize('NFD')
         .replace(/\p{M}/gu, '')
         .toLowerCase()
         .replaceAll('ck', 'k');
   }
}
