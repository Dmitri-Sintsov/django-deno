// import { serve } from 'https://deno.land/std/http/server.ts'

import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";


// @2.42.3%2B0.17.1
import type { RollupCache } from "https://deno.land/x/drollup/deps.ts";

import { LocalPath } from './localpath.ts';
import { ImportMapGenerator } from "./importmap.ts";
import type { RollupBundleItem, BundleChunkInfo } from './rollup.ts';
import { InlineRollupOptions, InlineRollup } from "./rollup.ts";

let args = parse(Deno.args);
const httpHost = args['host'];
const httpPort = args['port'];

const apiStatus = {
    "server": "Django deno server",
    "version": "0.0.1",
    "pid": Deno.pid,
};

type CacheEntries = Record<string, RollupCache>;

class Site {
    importMapGenerator: ImportMapGenerator;
    entries: CacheEntries;

    constructor(importMapGenerator: ImportMapGenerator) {
        this.importMapGenerator = importMapGenerator;
        this.entries = {};
    }

    public hasCache(cachePath: string) {
        return typeof this.entries[cachePath] !== 'undefined';
    }

    public getCache(cachePath: string) {
        return this.entries[cachePath];
    }

    public setCache(cachePath: string, cache: RollupCache) {
        this.entries[cachePath] = cache;
    }

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
    sites[siteId] = new Site(
        new ImportMapGenerator({
            baseMap: value['base_map'],
            importMap: value['import_map'],
        })
    );
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
    for (let valArg of ['filename', 'basedir', 'options']) {
        if (typeof value[valArg] === 'undefined') {
            context.response.body = `No {valArg} arg specified`;
            context.response.status = 500;
            return;
        }
    }
    basedir = value['basedir'];
    filename = value['filename'];

    let fullPathParts = new LocalPath(basedir).split();
    fullPathParts.push(filename);
    let entryPointLocalPath = LocalPath.fromPathParts(fullPathParts);
    let cachePath: string = entryPointLocalPath.path;

    let inlineRollupOptions = new InlineRollupOptions(value['options']);

    // https://github.com/lucacasonato/dext.ts/issues/65
    if (inlineRollupOptions.withCache && site.hasCache(cachePath)) {
        inlineRollupOptions.cache = site.getCache(cachePath);
    } else {
        inlineRollupOptions.cache = undefined;
    }

    if (!inlineRollupOptions.inlineFileMap) {
        inlineRollupOptions.chunkFileNames = "[name].js";
        inlineRollupOptions.manualChunks = (id: string, { getModuleInfo }): string | null | undefined => {
            let fullLocalPath = inlineRollupOptions.getFullLocalPath(id);
            // https://flaviocopes.com/typescript-object-destructuring/
            // const { name, age }: { name: string; age: number } = body.value
            let {bundleName, matchingBundle}: BundleChunkInfo = inlineRollupOptions.getBundleChunk(fullLocalPath);
            let moduleInfo = getModuleInfo(id);
            if (moduleInfo && matchingBundle) {
                inlineRollupOptions.setVirtualEntryPoints(moduleInfo, entryPointLocalPath, matchingBundle);
                console.log(`Found bundle ${bundleName}`);
                return bundleName;
            }
        }
    }

    let inlineRollup = new InlineRollup(site.importMapGenerator, inlineRollupOptions);
    let responseFields = await inlineRollup.perform(basedir, filename);
    /**
     * Warning: never use rollup cache for different source settings, eg. inline and bundled chunks at the same time.
     * Otherwise, it would cause cache incoherency and hard to track bugs.
     */
    if (inlineRollupOptions.withCache && inlineRollupOptions.cache) {
        site.setCache(cachePath, inlineRollupOptions.cache);
    }
    responseFields.toOakContext(context);
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
