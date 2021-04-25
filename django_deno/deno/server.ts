// import { serve } from 'https://deno.land/std/http/server.ts'
import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";
// @2.42.3%2B0.17.1
import type { RollupCache } from "https://deno.land/x/drollup/deps.ts";

import { LocalPath, ImportMapGenerator } from "./importmap.ts";
import type { InlineRollupOptions } from './rollup.ts';
import { InlineRollup } from "./rollup.ts";

let args = parse(Deno.args);
const httpHost = args['host'];
const httpPort = args['port'];

const apiStatus = {
    "server": "Django deno server",
    "version": "0.0.1",
    "pid": Deno.pid,
};

type SiteCache = Record<string, RollupCache>;

interface Site {
    importMapGenerator: ImportMapGenerator,
    siteCache: SiteCache,
};

interface Sites {
    [index: string]: Site;
};

let sites: Sites = {};

const router = new Router();

router
.get("/status/", (context) => {
    context.response.body = apiStatus;
})
.post("/maps/", async (context) => {
    const body = context.request.body({ type: 'json' });
    const value = await body.value;
    const siteId = value['site_id'];
    sites[siteId] = {
        importMapGenerator: new ImportMapGenerator({
            baseMap: value['base_map'],
            importMap: value['import_map'],
        }),
        siteCache: {},
    };
    context.response.body = apiStatus;
    context.response.status = 200;
})
.post("/rollup/", async (context) => {
    // HTTP POST
    const body = context.request.body({ type: 'json' });
    const value = await body.value;
    const site = sites[value['site_id']];

    let basedir: string;
    let filename: string;
    let inlineRollupOptions: InlineRollupOptions;
    for (let valArg of ['filename', 'basedir', 'options']) {
        if (typeof value[valArg] === 'undefined') {
            context.response.body = `No {valArg} arg specified`;
            context.response.status = 500;
            return;
        }
    }
    basedir = value['basedir'];
    filename = value['filename'];

    let cacheParts = new LocalPath(basedir).split();
    cacheParts.push(filename);
    let cachePath: string = LocalPath.fromPathParts(cacheParts).path;

    inlineRollupOptions = value['options'];
    // https://github.com/lucacasonato/dext.ts/issues/65
    if (inlineRollupOptions.withCache && typeof site.siteCache[cachePath] !== 'undefined') {
        inlineRollupOptions.cache = site.siteCache[cachePath];
    } else {
        inlineRollupOptions.cache = undefined;
    }
    let inlineRollup = new InlineRollup(site.importMapGenerator, inlineRollupOptions);
    let responseFields = await inlineRollup.perform(basedir, filename);
    if (inlineRollupOptions.withCache && inlineRollupOptions.cache) {
        site.siteCache[cachePath] = inlineRollupOptions.cache;
    }
    responseFields.toOakContext(context);
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
