/**
 * Generates the prime numbers using the sieve of
 * eratosthenes
 *
 * @param {number} arraySize
 * @yields {number} the next prime number
 */
function* primeNumberGenerator(arraySize) {
  const sieve = [];
  sieve.length = arraySize;
  sieve.fill(true);

  for (let i=2; i<arraySize; i++) {
    if (sieve[i]) {
      yield i;

      let j = i;
      while (j<arraySize) {
        j += i;
        sieve[j] = false;
      }
    }
  }
}

export {primeNumberGenerator};
