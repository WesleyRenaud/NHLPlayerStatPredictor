import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { Position } from '../../../../scripts/shared/enums/position.js';
import positionValues from '../../../../shared/enums/position.json' with { type: 'json' };

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');


test('Test_Position_TestSharedJson_ExpectSingleSourceOfTruth', () => {
   const diskValues = JSON.parse(
      readFileSync(path.join(root, 'shared/enums/position.json'), 'utf8')
   );

   for (const [key, value] of Object.entries(positionValues)) {
      assert.equal(Position[key], value);
   }
   assert.deepEqual(positionValues, diskValues);
});


test('Test_Position_TestListIndexing_ExpectElements', () => {
   const first = 'a';
   const second = 'b';
   const third = 'c';
   const fourth = 'd';
   const items = [ first, second, third, fourth ];

   assert.equal(items[Position.FIRST], first);
   assert.equal(items[Position.SECOND], second);
   assert.equal(items[Position.THIRD], third);
   assert.equal(items[Position.FOURTH], fourth);
   assert.equal(items.at(Position.LAST), fourth);
   assert.equal(items.at(Position.SECOND_LAST), third);
});
