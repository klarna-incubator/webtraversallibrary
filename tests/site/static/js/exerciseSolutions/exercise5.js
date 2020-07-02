/**
 * Solution to project euler exercise 5
 * @return {number} the solution!
 */
function exercise5() {
  let i=0;
  const done=false;

  outerWhile:
  while (!done) {
    i+=20;
    for (let j=2; j<=20; j++) {
      if (i % j != 0) continue outerWhile;
    }

    break;
  }

  return i;
}

export {exercise5 as default};
