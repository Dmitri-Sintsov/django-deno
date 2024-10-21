/**
 * Derived from <https://github.com/rollup/rollup/blob/v2.42.3/cli/logging.ts>
 */

import type { RollupError } from "https://unpkg.com/rollup@2.79.2/dist/rollup.d.ts";
import { bold, cyan, dim, red } from "jsr:@std/fmt/colors";
import { relativeId } from "./relativeId.ts";

export const logInfo = console.error.bind(console);
export const logError = console.error.bind(console);
export const logOutput = console.log.bind(console);

/**
 * handleError
 *
 * @param {RollupErr} err
 * @param {boolean} recover
 * @private
 */
export function handleError(err: RollupError, recover = false) {
  let message = err.message || err;

  if (err.name) {
    message = `${err.name}: ${message}`;
  }

  logError(bold(red(`[!] ${bold(message.toString())}`)));

  if (err.url) {
    logError(cyan(err.url));
  }

  if (err.loc) {
    logError(
      `${
        relativeId((err.loc.file || err.id)!)
      } (${err.loc.line}:${err.loc.column})`,
    );
  } else if (err.id) {
    logError(relativeId(err.id));
  }

  if (err.frame) {
    logError(dim(err.frame));
  }

  if (err.stack) {
    logError(dim(err.stack));
  }

  logError("");

  if (!recover) {
    Deno.exit(1);
  }
}
