/**
 * Derived from https://github.com/cmorten/deno-rollup
 */

import { notImplemented } from "./notImplemented.ts";
// import { cache } from "jsr:@std/cache";

const decoder = new TextDecoder("utf-8");

/**
 * loadUrl
 *
 * @param {URL} url
 * @param {RequestInit} [fetchOpts]
 * @returns {Promise<string>}
 * @private
 */
export async function loadUrl(
  url: URL,
  fetchOpts?: RequestInit,
): Promise<string> | never {
  switch (url.protocol) {
    case "file:": {
      const out = await Deno.readFile(url);

      return decoder.decode(out);
    }
    case "http:":
    case "https:": {
        const res = await fetch(url.href, fetchOpts);
        return await res.text();
    }
    default: {
      return notImplemented(`support for protocol '${url.protocol}'`);
    }
  }
}
