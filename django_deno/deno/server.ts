// import { serve } from 'https://deno.land/std/http/server.ts'
import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";

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

    let cwd = Deno.cwd();
    if (basedirParam) {
        Deno.chdir(basedirParam);
    }

    let filename: string;
    if (filenameParam === undefined || filenameParam === null) {
        context.response.body = 'No filename arg specified';
        context.response.status = 500;
    } else {
        filename = filenameParam;
        let responseFields = await inlineRollup(filename);
        responseFields.toOakContext(context);
    }
    Deno.chdir(cwd);
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
