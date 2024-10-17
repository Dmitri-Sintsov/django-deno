import { join, toFileUrl } from "jsr:@std/path";
import { getSystemSeparator } from  "../localpath.ts";

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
