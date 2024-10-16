import { join, toFileUrl } from "jsr:@std/path";

let sep = (Deno.build.os === "windows") ? '\\' : '/';

/**
 * getUrlBase
 *
 * @returns {URL}
 * @private
 */
function getUrlBase(): URL {
  return toFileUrl(join(Deno.cwd(), sep));
}

export { sep, getUrlBase };
