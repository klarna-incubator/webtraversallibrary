import {loadFile} from './loadFile.js';

/**
 * Given a path to a javascript file, follows the imports and replaces them
 * with the relevant functions from other files, to make one js script
 *
 * @param {string} path
 * @return {string} expanded javascript
 */
function expandJavaScript(path) {
  const js = loadFile(path);

  const lines = js.split('\n');

  const importLines = [];
  const otherLines = [];
  for (const line of lines) {
    if (line.startsWith('import')) importLines.push(line);
    else if (line.startsWith('export')) continue;
    else otherLines.push(line);
  }

  const expanded = [];
  for (const importLine of importLines) {
    const path = importLine.split('"')[1];
    expanded.push(expandJavaScript('/static/js/libraryFunctions/' + path));
  }

  for (const otherLine of otherLines) {
    expanded.push(otherLine);
  }

  return expanded.join('\n');
}

export {expandJavaScript as default};
