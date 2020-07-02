/**
 * Solution to project euler exercise 14
 * @return {number} the solution!
 */
function exercise14() {
  const smallerThan = 1000000;

  // solution is much faster if we cache the sequences we've already looked at
  const sequenceLengths = [];
  for (let i=0; i<smallerThan; i++) sequenceLengths.push(-1);
  sequenceLengths[1] = 1;

  for (let i=2; i<=smallerThan; i++) {
    // if we've already had a sequence go through this number, don't recalculate
    if (sequenceLengths[i] !== -1) continue;

    const collatzSequence = [i];
    let length = 0;
    while (true) {
      const term = collatzSequence[collatzSequence.length - 1];

      // if we've already calculated this one, backfill the other terms and finish
      // due to memory constraints, calculate terms over 1000000 on the fly
      if (term < sequenceLengths.length && sequenceLengths[term] !== -1) {
        length += sequenceLengths[term];

        for (let j=0; j<collatzSequence.length; j++) {
          if (collatzSequence[j]< sequenceLengths.length) {
            sequenceLengths[collatzSequence[j]] = length - j;
          }
        }

        break;
      }

      // otherwise compute the next term in the sequence
      if (term % 2 == 0) collatzSequence.push(term/2);
      else collatzSequence.push(1 + (3*term));
      length += 1;
    }
  }

  // find the longest sequence
  let maxInd = 0;
  let max = 0;
  for (let i=0; i<=smallerThan; i++) {
    if (sequenceLengths[i] > max) {
      max = sequenceLengths[i];
      maxInd = i;
    }
  }

  return maxInd;
}

export {exercise14 as default};
