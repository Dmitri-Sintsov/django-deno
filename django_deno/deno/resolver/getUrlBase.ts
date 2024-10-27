/**
 * Derived from https://github.com/cmorten/deno-rollup
 */

import { join, toFileUrl } from "jsr:@std/path";
import { systemSeparator } from  "../localpath.ts";

/**
 * getUrlBase
 *
 * @returns {URL}
 * @private
 */
function getUrlBase(): URL {
  return toFileUrl(join(Deno.cwd(), systemSeparator));
}

export { getUrlBase };
