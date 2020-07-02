/**
 * Solution to project euler exercise 6
 * @return {number} the solution!
 */
function exercise6() {
  let sumOfSquares = 0;
  let sum = 0;
  for (let i=0; i<=100; i++) {
    sumOfSquares += i**2;
    sum += i;
  }

  const squareOfSum = sum**2;

  return squareOfSum - sumOfSquares;
}

export {exercise6 as default};
