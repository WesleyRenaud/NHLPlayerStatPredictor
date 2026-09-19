import { ValueNormalizer } from './valueNormalizer.js';


export class PlayerNamesApiNormalizer {
   static normalizeNames(response) {
      return ValueNormalizer.asArray(ValueNormalizer.asObject(response).names);
   }
}
