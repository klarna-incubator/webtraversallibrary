import {primeNumberGenerator} from '../libraryFunctions/primeNumberGenerator.js';

/**
 * Solution to project euler exercise 7
 * @return {number} the solution!
 */
function exercise7() {
  const gen = primeNumberGenerator(1000000);

  let prime;

  for (let i=0; i<10001; i++) prime = gen.next().value;

  return prime;
}

export {exercise7 as default};
