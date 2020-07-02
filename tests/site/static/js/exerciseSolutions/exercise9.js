/**
 * Solution to project euler exercise 9
 * @return {number} the solution!
 */
function exercise9() {
  let answer;
  outerloop:
  for (let a=1; a<400; a++) {
    for (let b=1; b<a; b++) {
      const c = 1000 - b - a;

      if (a*a + b*b === c*c) {
        answer = a*b*c;
        break outerloop;
      }
    }
  }

  return answer;
}

export {exercise9 as default};
