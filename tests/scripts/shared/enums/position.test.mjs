import assert from 'node:assert/strict';
import test from 'node:test';

import { Position } from '../../../../scripts/shared/enums/position.js';


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
