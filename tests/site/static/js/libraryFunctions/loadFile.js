/**
 * loads a local static file's contents into a string
 *
 * @param {string} path
 * @return {string} the contents of the file
 */
function loadFile(path) {
  let fileContents;

  /**
   * listen for the file contents response
   */
  function listener() {
    fileContents = this.responseText; // eslint-disable-line no-invalid-this
  }

  const req = new XMLHttpRequest();
  req.addEventListener('load', listener);
  req.open('GET', path, false);
  req.send();

  return fileContents;
}

export {loadFile};
export {loadFile as default};
