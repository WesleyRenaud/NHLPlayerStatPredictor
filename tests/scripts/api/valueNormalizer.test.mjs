import assert from 'node:assert/strict';
import test from 'node:test';

import { ValueNormalizer } from '../../../scripts/api/valueNormalizer.js';


test('Test_AsArray_TestValidCollection_ExpectSameReference', () => {
   const names = [ 'Stub Alpha' ];
   assert.equal(ValueNormalizer.asArray(names), names);
});


test('Test_AsArray_TestMissingValues_ExpectEmptyArray', () => {
   assert.deepEqual(ValueNormalizer.asArray(null), []);
   assert.deepEqual(ValueNormalizer.asArray({ name: 'Stub Alpha' }), []);
});


test('Test_AsObject_TestValidObject_ExpectSameReference', () => {
   const payload = { names: [] };
   assert.equal(ValueNormalizer.asObject(payload), payload);
});


test('Test_AsObject_TestMissingValues_ExpectEmptyObject', () => {
   assert.deepEqual(ValueNormalizer.asObject(null), {});
   assert.deepEqual(ValueNormalizer.asObject('Stub Alpha'), {});
});


test('Test_AsTrimmedString_TestWhitespace_ExpectTrimmed', () => {
   assert.equal(ValueNormalizer.asTrimmedString('  Stub Alpha  '), 'Stub Alpha');
});


test('Test_AsTrimmedString_TestNullish_ExpectEmpty', () => {
   assert.equal(ValueNormalizer.asTrimmedString(null), '');
   assert.equal(ValueNormalizer.asTrimmedString(undefined), '');
});
