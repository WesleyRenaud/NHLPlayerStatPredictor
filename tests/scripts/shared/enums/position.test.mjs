import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { Position } from '../../../../scripts/shared/enums/position.js';
import positionValues from '../../../../shared/enums/position.json' with { type: 'json' };

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');


test('Test_Position_TestSharedJson_ExpectSingleSourceOfTruth', () => {
   for (const [key, value] of Object.entries(positionValues)) {
      assert.equal(Position[key], value);
   }

   const diskValues = JSON.parse(
      readFileSync(path.join(root, 'shared/enums/position.json'), 'utf8')
   );
   assert.deepEqual(positionValues, diskValues);
});


test('Test_Position_TestListIndexing_ExpectElements', () => {
   const items = [ 'a', 'b', 'c', 'd' ];

   assert.equal(items[Position.FIRST], 'a');
   assert.equal(items[Position.SECOND], 'b');
   assert.equal(items[Position.THIRD], 'c');
   assert.equal(items[Position.FOURTH], 'd');
   assert.equal(items.at(Position.LAST), 'd');
   assert.equal(items.at(Position.SECOND_LAST), 'c');
});
