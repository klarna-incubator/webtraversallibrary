import {loadFile} from '../libraryFunctions/loadFile.js';

/**
 * Solution to project euler exercise 8
 * @return {number} the solution!
 */
function exercise8() {
  const longNumber = loadFile('/static/data/projectEuler/exercise8Data.txt').split('\n').join('');

  const array = longNumber.split('');
  let biggest = -1;

  for (let i=0; i<array.length-13; i++) {
    let product = 1;
    for (let j=i; j<i+13; j++) {
      product *= array[j];
    }

    if (product > biggest) biggest = product;
  }

  return biggest;
}

export {exercise8 as default};
