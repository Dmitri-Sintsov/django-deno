import { rollup, RollupOutput } from "https://deno.land/x/drollup@2.41.0+0.16.1/mod.ts";
import type { OutputOptions } from "https://deno.land/x/drollup@2.41.0+0.16.1/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup@2.41.0+0.16.1/src/rollup/write.ts";

async function inlineRollup(filename: string, context: any) {
    // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
    // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
    // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api
    const outputOptions: OutputOptions = {
        format: 'es' as const,
        sourcemap: 'inline',
    };
    const options = {
        input: filename,
        output: outputOptions,
    };

    context.response.type = 'application/javascript';

    let rollupOutput: RollupOutput;

    try {
        const bundle = await rollup(options);
        rollupOutput = await bundle.generate(options.output);
    } catch(e) {
        context.response.status = 500;
        context.response.body = e.toString();
        return;
    };

    for (const file of rollupOutput.output) {
        if (file.type === 'asset') {
            // console.log('Asset', file);
        } else {
            // console.log('Chunk', file.modules);
            // https://github.com/cmorten/deno-rollup/blob/bb159fc3a8c3c9fdd0b57142cc7bf84ae93dd2f4/src/cli/build.ts
            // https://deno.land/x/drollup@2.41.0+0.16.1/src/rollup/write.ts
            context.response.body = file.code + `\n//# ${SOURCEMAPPING_URL}=${file.map!.toUrl()}\n`;
            break;
        }
        if (!context.response.body) {
            context.response.status = 500;
            context.response = 'Empty body'
        }
    }

};

export default inlineRollup;
