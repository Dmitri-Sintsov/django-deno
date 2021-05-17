// import { serve } from 'https://deno.land/std/http/server.ts'
import { existsSync } from "https://deno.land/std/fs/mod.ts";

import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";


// @2.42.3%2B0.17.1
import type { RollupCache } from "https://deno.land/x/drollup/deps.ts";

import { LocalPath } from './localpath.ts';
import { ImportMapGenerator } from "./importmap.ts";
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

class EntryCache {
    cache: RollupCache;
    previousInlineString?: string;

    constructor(cache: RollupCache) {
        this.cache = cache;
    }

    public notModified(body: string) {
        return this.previousInlineString === body;
    }

    public updateBody(body: string) {
        let notModified = this.notModified(body);
        this.previousInlineString = body;
        return notModified;
    }
};

type ScriptEntries = Record<string, EntryCache>;

class Site {
    importMapGenerator: ImportMapGenerator;
    entries: ScriptEntries;

    constructor(importMapGenerator: ImportMapGenerator) {
        this.importMapGenerator = importMapGenerator;
        this.entries = {};
    }

    public hasEntry(cachePath: string) {
        return typeof this.entries[cachePath] !== 'undefined';
    }

    public updateEntry(cachePath: string, cache: RollupCache) {
        if (this.hasEntry(cachePath)) {
            this.entries[cachePath].cache = cache;
        } else {
            this.entries[cachePath] = new EntryCache(cache);
        }
        return this.entries[cachePath];
    }

    public hasCache(cachePath: string) {
        return this.hasEntry(cachePath) && this.entries[cachePath].cache;
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
    if (inlineRollupOptions.withCache && site.hasCache(cachePath)) {
        inlineRollupOptions.cache = site.entries[cachePath].cache;
    } else {
        inlineRollupOptions.cache = undefined;
    }
    let entryPoints = [
        // 'document.js',
        'dash.js',
        'dialog.js',
        'modelform.js',
        'tabpane.js',
        'actions.js',
        'grid.js',
        'ioc.js',
        'ui.js',
        'row.js',
        'ioc.js',
    ];
    if (!inlineRollupOptions.inlineFileMap) {
        inlineRollupOptions.chunkFileNames = "[name].js";
        inlineRollupOptions.manualChunks = (id: string, { getModuleInfo }): string | null | undefined => {
            let fullLocalPath = new LocalPath(Deno.cwd());
            fullLocalPath = fullLocalPath.traverseStr(id);
            if (!existsSync(fullLocalPath.path)) {
                throw new Error(`Error in manualChunks, id "${id}" path does not exists: "${fullLocalPath.path}"`);
            }

            if (fullLocalPath.split().indexOf('djk') !== -1) {
                let moduleInfo = getModuleInfo(id);
                if (moduleInfo) {
                    // Add entry point, so exports from nested smaller modules will be preserved in 'djk' chunk.
                    // if (fullLocalPath.getBaseName() !== 'document.js') {
                        moduleInfo.isEntry = filename === 'app.js';
                    // }
                }
                return 'djk';
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
        let entry = site.updateEntry(cachePath, inlineRollupOptions.cache);
        /**
         * let notModified = entry.updateBody(responseFields.body);
         * if (notModified) {
         *    context.response.status = 304;
         *    return;
         * }
         */
    }
    responseFields.toOakContext(context);
});

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ hostname: httpHost, port: httpPort });
Deno.stdout.write(new TextEncoder().encode(`Server listening on ${httpHost}:${httpPort}`));
