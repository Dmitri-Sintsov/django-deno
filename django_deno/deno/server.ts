import { parse } from "https://deno.land/std/flags/mod.ts";
import { rollup, RollupOutput } from "https://deno.land/x/drollup@2.41.0+0.16.1/mod.ts";
import type { OutputOptions } from "https://deno.land/x/drollup@2.41.0+0.16.1/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup@2.41.0+0.16.1/src/rollup/write.ts";
// import { serve } from 'https://deno.land/std/http/server.ts'
import { Application, Router } from "https://deno.land/x/oak/mod.ts";

let args = parse(Deno.args);
const httpHost = args['host'];
const httpPort = args['port'];

async function inlineRollup(context: any) {
    // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
    // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
    // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api
    const outputOptions: OutputOptions = {
        format: 'es' as const,
        sourcemap: 'inline',
    };
    let filename;

    if ('filename' in context.params) {
        // HTTP GET
        filename = context.params.filename;
    } else {
        // HTTP POST
        const body = context.request.body({ type: 'form' });
        const value = await body.value;
        filename = value.get('filename', '');
    }
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

const router = new Router();
router
.get("/", (context) => {
    context.response.body = "Hello, deno!";
})
.get("/rollup/:filename", inlineRollup)
.post("/rollup/", inlineRollup);

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
