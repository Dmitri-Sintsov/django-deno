// Developed with drollup@2.41.0+0.16.1
import { Context } from "https://deno.land/x/oak/mod.ts";
import { rollup, RollupOutput } from "https://deno.land/x/drollup/mod.ts";
import type { OutputOptions } from "https://deno.land/x/drollup/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup/src/rollup/write.ts";
import { denoResolver, DenoResolverOptions } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/denoResolver.ts";
import { parse } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/parse.ts";
import { resolveId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/resolveId.ts";
import { handleUnresolvedId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/handleUnresolvedId.ts";
import { exists } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/exists.ts";

import { ImportMapGenerator } from "./importmap.ts";

class ResponseFields {
    status: any;
    type: any;
    body: any;

    toOakContext(context: Context): void {
        context.response.status = this.status;
        context.response.type = this.type;
        context.response.body = this.body;
    };

    constructor() {
        this.status = 500;
        this.type = 'application/javascript';
        this.body = 'Empty body';
    }
};

async function inlineRollup(basedir: string | null, filename: string, importMapGenerator: ImportMapGenerator) {
    // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
    // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
    // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api
    let response = new ResponseFields();

    const outputOptions: OutputOptions = {
        format: 'es' as const,
        sourcemap: 'inline',
    };

    let resolverOptions: DenoResolverOptions = {};
    let resolver = denoResolver();

    resolver.resolveId = async (source: string, importer?: string) => {
        let id = resolveId(source, importer);
        let url = parse(id);

        if (!url) {
            return handleUnresolvedId(id, importer);
        }

        if (!(await exists(url, resolverOptions.fetchOpts))) {
            // We assume extensionless imports are from bundling commonjs
            // as in Deno extensions are compulsory. We assume that the
            // extensionless commonjs file is JavaScript and not TypeScript.
            id += ".js";
            url = new URL(`${url.href}.js`);
        }

        if (!(await exists(url, resolverOptions.fetchOpts))) {
            // id = id.substr(0, id.length - 3);
            // return handleUnresolvedId(id, importer);
            return importMapGenerator.resolve(Deno.cwd(), source, importer);
        }
        return id;
    };

    const options = {
        input: filename,
        output: outputOptions,
        plugins: [resolver],
    };

    let rollupOutput: RollupOutput;

    let cwd = Deno.cwd();
    if (basedir) {
        Deno.chdir(basedir);
    }

    try {
        const bundle = await rollup(options);
        rollupOutput = await bundle.generate(options.output);
    } catch(e) {
        response.body = e.toString();
        return response;
    } finally {
        Deno.chdir(cwd);
    };

    for (const file of rollupOutput.output) {
        if (file.type === 'asset') {
            // console.log('Asset', file);
        } else {
            // console.log('Chunk', file.modules);
            // https://github.com/cmorten/deno-rollup/blob/bb159fc3a8c3c9fdd0b57142cc7bf84ae93dd2f4/src/cli/build.ts
            // https://deno.land/x/drollup@2.41.0+0.16.1/src/rollup/write.ts
            response.body = file.code + `\n//# ${SOURCEMAPPING_URL}=${file.map!.toUrl()}\n`;
            response.status = 200;
            break;
        }
    }
    return response;
};

export default inlineRollup;
