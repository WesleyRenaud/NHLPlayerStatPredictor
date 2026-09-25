import assert from 'node:assert/strict';
import test from 'node:test';

import { ValueNormalizer } from '../../../scripts/api/valueNormalizer.js';


test('Test_AsArray_TestValidCollection_ExpectSameReference', () => {
   const names = [ 'Stub Alpha' ];

   const values = ValueNormalizer.asArray(names);

   assert.equal(values, names);
});


test('Test_AsArray_TestNull_ExpectEmptyArray', () => {
   const value = null;

   const values = ValueNormalizer.asArray(value);

   assert.deepEqual(values, []);
});


test('Test_AsArray_TestObject_ExpectEmptyArray', () => {
   const value = { name: 'Stub Alpha' };

   const values = ValueNormalizer.asArray(value);

   assert.deepEqual(values, []);
});


test('Test_AsObject_TestValidObject_ExpectSameReference', () => {
   const payload = { names: [] };

   const object = ValueNormalizer.asObject(payload);

   assert.equal(object, payload);
});


test('Test_AsObject_TestNull_ExpectEmptyObject', () => {
   const value = null;

   const object = ValueNormalizer.asObject(value);

   assert.deepEqual(object, {});
});


test('Test_AsObject_TestString_ExpectEmptyObject', () => {
   const value = 'Stub Alpha';

   const object = ValueNormalizer.asObject(value);

   assert.deepEqual(object, {});
});


test('Test_AsTrimmedString_TestWhitespace_ExpectTrimmed', () => {
   const name = 'Stub Alpha';
   const value = `  ${name}  `;

   const trimmed = ValueNormalizer.asTrimmedString(value);

   assert.equal(trimmed, name);
});


test('Test_AsTrimmedString_TestNull_ExpectEmpty', () => {
   const value = null;

   const trimmed = ValueNormalizer.asTrimmedString(value);

   assert.equal(trimmed, '');
});


test('Test_AsTrimmedString_TestUndefined_ExpectEmpty', () => {
   const value = undefined;

   const trimmed = ValueNormalizer.asTrimmedString(value);

   assert.equal(trimmed, '');
});


test('Test_AsFiniteNumber_TestNumber_ExpectNumber', () => {
   const value = 12;

   const number = ValueNormalizer.asFiniteNumber(value);

   assert.equal(number, value);
});


test('Test_AsFiniteNumber_TestNumericString_ExpectNumber', () => {
   const value = '34';

   const number = ValueNormalizer.asFiniteNumber(value);

   assert.equal(number, Number(value));
});


test('Test_AsFiniteNumber_TestUndefined_ExpectUndefined', () => {
   const value = undefined;

   const number = ValueNormalizer.asFiniteNumber(value);

   assert.equal(number, undefined);
});


test('Test_AsFiniteNumber_TestEmptyString_ExpectUndefined', () => {
   const value = '';

   const number = ValueNormalizer.asFiniteNumber(value);

   assert.equal(number, undefined);
});
