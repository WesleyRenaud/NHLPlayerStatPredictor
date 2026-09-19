import positionValues from '../../../shared/enums/position.json' with { type: 'json' };

export class Position {
   static {
      Object.assign(Position, positionValues);
   }
}
