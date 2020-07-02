import {loadFile} from '../libraryFunctions/loadFile.js';

/**
 * Solution to project euler exercise 13
 * @return {number} the solution!
 */
function exercise13() {
  const bigIntegers = loadFile('/static/data/projectEuler/exercise13Data.txt').split('\n');

  let total = BigInt(0);
  for (const integer of bigIntegers) {
    total = total + BigInt(integer);
  }

  return total.toString().slice(0, 10);
}

export {exercise13 as default};
