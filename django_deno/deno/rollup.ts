// Developed with drollup@2.41.0+0.16.1
import { Context } from "https://deno.land/x/oak/mod.ts";
import { rollup, RollupOutput } from "https://deno.land/x/drollup/mod.ts";
import type { OutputOptions } from "https://deno.land/x/drollup/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup/src/rollup/write.ts";

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

async function inlineRollup(filename: string) {
    // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
    // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
    // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api
    let response = new ResponseFields();

    const outputOptions: OutputOptions = {
        format: 'es' as const,
        sourcemap: 'inline',
    };
    const options = {
        input: filename,
        output: outputOptions,
    };

    let rollupOutput: RollupOutput;

    try {
        const bundle = await rollup(options);
        rollupOutput = await bundle.generate(options.output);
    } catch(e) {
        response.body = e.toString();
        return response;
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
