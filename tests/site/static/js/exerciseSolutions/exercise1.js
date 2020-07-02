/**
 * Solution to project euler exercise 1
 * @return {number} the solution!
 */
function exercise1() {
  let total = 0;
  for (let i=0; i<1000; i++) {
    if ((i % 3) * (i % 5) === 0) total += i;
  }

  return total;
}

export {exercise1 as default};
