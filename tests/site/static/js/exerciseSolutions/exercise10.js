import {primeNumberGenerator} from '../libraryFunctions/primeNumberGenerator.js';

/**
 * Solution to project euler exercise 10
 * @return {number} the solution!
 */
function exercise10() {
  const gen = primeNumberGenerator(2000000);

  let sum = 0;
  while (true) {
    const prime = gen.next();
    if (prime.done) break;
    sum += prime.value;
  }

  return sum;
}

export {exercise10 as default};
