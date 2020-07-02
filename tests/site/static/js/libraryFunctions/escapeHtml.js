/**
 * Removes the various HTML "unsafe" characters from a string and
 * replaces them with their safe equivalents
 *
 * @param {string} unsafe
 * @return {string} the safe html
 */
function escapeHtml(unsafe) {
  return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
}

export {escapeHtml as default};
