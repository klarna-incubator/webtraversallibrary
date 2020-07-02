/**
 * Solution to project euler exercise 4
 * @return {number} the solution!
 */
function exercise4() {
  let biggest = -1;

  for (let i=100; i<1000; i++) {
    for (let j=100; j<i; j++) {
      const product = i*j;

      const productString = product.toString(10);
      const reversedString = productString.split('').reverse().join('');

      if (productString === reversedString && product > biggest) {
        biggest = product;
      }
    }
  }

  return biggest;
}

export {exercise4 as default};
