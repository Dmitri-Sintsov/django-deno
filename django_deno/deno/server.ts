// import { serve } from 'https://deno.land/std/http/server.ts'
import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";
import type { ImportMapObject } from "https://deno.land/x/drollup/plugins/importmap/mod.ts";

import { PathMap } from "./importmap.ts";
import inlineRollup from "./rollup.ts";

let args = parse(Deno.args);
const httpHost = args['host'];
const httpPort = args['port'];

const apiStatus = {
    "server": "Django deno server",
    "version": "0.0.1",
    "pid": Deno.pid,
};

let baseMap: PathMap;
let importMap: PathMap;

const router = new Router();
router
.get("/status/", (context) => {
    context.response.body = apiStatus;
})
.post("/maps/", async (context) => {
    const body = context.request.body({ type: 'json' });
    const value = await body.value;
    baseMap = new PathMap(value['base_map']);
    importMap = new PathMap(value['import_map']);
    context.response.body = apiStatus;
    context.response.status = 200;
})
.post("/rollup/", async (context) => {
    // HTTP POST
    const body = context.request.body({ type: 'json' });
    const value = await body.value;

    let filename: string;
    if (typeof value['filename'] === 'undefined') {
        context.response.body = 'No filename arg specified';
        context.response.status = 500;
    } else {
        filename = value['filename'];
        // https://github.com/lucacasonato/dext.ts/issues/65
        let importmap = {
            imports: {
                "../django-deno/settings.js": "/home/user/work/drf-gallery/lib/python3.8/site-packages/django_deno/static/django-deno/settings.js"
            }
        };
        let responseFields = await inlineRollup(value['basedir'], filename, importmap);
        responseFields.toOakContext(context);
    }
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
