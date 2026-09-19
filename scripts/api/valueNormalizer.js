export class ValueNormalizer {
   static asArray(value) {
      return Array.isArray(value) ? value : [];
   }


   static asObject(value) {
      return value && typeof value === 'object' ? value : {};
   }


   static asTrimmedString(value) {
      if (value == null) {
         return '';
      }

      return String(value).trim();
   }


   static asFiniteNumber(value) {
      if (value === '' || value == null) {
         return undefined;
      }

      const number = Number(value);
      return Number.isFinite(number) ? number : undefined;
   }
}
