// import { serve } from 'https://deno.land/std/http/server.ts'
import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";
import type { ImportMapObject } from "https://deno.land/x/drollup/plugins/importmap/mod.ts";

import inlineRollup from "./rollup.ts";

let args = parse(Deno.args);
const httpHost = args['host'];
const httpPort = args['port'];

const router = new Router();
router
.get("/", (context) => {
    context.response.body = {
        "server": "Django deno server",
        "version": "0.0.1",
    };
})
.post("/rollup/", async (context) => {
    let filenameParam: string | null | undefined;
    let basedirParam: string | null | undefined;

    // HTTP POST
    const body = context.request.body({ type: 'form' });
    const value = await body.value;
    filenameParam = value.get('filename');
    basedirParam = value.get('basedir');

    let filename: string;
    if (filenameParam === undefined || filenameParam === null) {
        context.response.body = 'No filename arg specified';
        context.response.status = 500;
    } else {
        filename = filenameParam;
        // https://github.com/lucacasonato/dext.ts/issues/65
        let importmap = {
            imports: {
                "../django-deno/settings.js": "/home/user/work/drf-gallery/lib/python3.8/site-packages/django_deno/static/django-deno/settings.js"
            }
        };
        let responseFields = await inlineRollup(basedirParam, filename, importmap);
        responseFields.toOakContext(context);
    }
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
