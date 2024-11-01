// deno-lint-ignore-file prefer-const
// import { serve } from 'jsr:@std/http'

import { parseArgs } from "jsr:@std/cli";
import { Application, Router } from "jsr:@oak/oak";

import type { RollupCache } from "rollup";

import { LocalPath } from './localpath.ts';
import { ImportMapGenerator } from "./importmap.ts";
import { RollupBundleSet, InlineRollupOptions, InlineRollup } from "./rollup.ts";

let args = parseArgs(Deno.args, {
    boolean: ['help'],
    string: ['host', 'port'],
    default: {
        'host': '127.0.0.1',
        'port': false,
    },
});

if (args.help) {
    console.log(`django-deno rollup server. Usage: ${import.meta.filename} --host=hostname --port=port`)
    Deno.exit(1);
}

const httpHost = args.host;

if (!args.port) {
    console.log("Missing 'port' arg");
    Deno.exit(1);
}
const httpPort = Number(args.port);

const apiStatus = {
    "server": "Django deno server",
    "version": "0.2.0",
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

}

interface Sites {
    [index: string]: Site;
};

let sites: Sites = {};

const router = new Router();

router
.get("/status/", (context, next) => {
    context.response.body = apiStatus;
})
.post("/maps/", async (context, next) => {
    const value = await context.request.body.json();
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
.post("/rollup/", async (context, next) => {
    // HTTP POST
    let responseFields;
    const value = await context.request.body.json();
    if (typeof sites[value.site_id] === 'undefined' ) {
        responseFields = InlineRollup.getErrorResponse(
            new Error(`sites for site_id=${value.site_id} is undefined`)
        );
        responseFields.toOakContext(context);
        return;
    }
    const site = sites[value.site_id];

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

    let baseDirLocalPath = new LocalPath(basedir);
    let fullPathParts = baseDirLocalPath.split();
    fullPathParts.push(filename);
    let entryPointLocalPath = LocalPath.fromPathParts(fullPathParts);
    let cachePath: string = entryPointLocalPath.path;

    console.log(`=== Entry point "${entryPointLocalPath.path}" ===`);

    let inlineRollupOptions = new InlineRollupOptions(value['options']);

    // https://github.com/lucacasonato/dext.ts/issues/65
    if (inlineRollupOptions.withCache && site.hasCache(cachePath)) {
        inlineRollupOptions.cache = site.getCache(cachePath);
    } else {
        inlineRollupOptions.cache = undefined;
    }

    let foundBundles = new RollupBundleSet();

    if (!inlineRollupOptions.inlineFileMap) {
        inlineRollupOptions.chunkFileNames = "[name].js";
        inlineRollupOptions.manualChunks = (id: string, { getModuleInfo }): string | null | undefined => {
            let fullLocalPath = LocalPath.getFullLocalPath(id);
            // https://flaviocopes.com/typescript-object-destructuring/
            // const { name, age }: { name: string; age: number } = body.value
            let matchingBundle = inlineRollupOptions.getBundleChunk(fullLocalPath);
            let moduleInfo = getModuleInfo(id);
            if (moduleInfo && matchingBundle && matchingBundle.name) {
                // Keep singleton matchingBundle.
                matchingBundle = foundBundles.add(matchingBundle);
                let isVirtualEntry: boolean = false;
                if (matchingBundle.isWriteEntryPoint(entryPointLocalPath)) {
                    if (matchingBundle.isVirtualEntry(fullLocalPath)) {
                        isVirtualEntry = matchingBundle.setVirtualEntryPoint(moduleInfo);
                    }
                    if (isVirtualEntry) {
                        console.log(`Bundle "${matchingBundle.name}", virtual entry point "${fullLocalPath.path}"`);
                        matchingBundle.addSkipChunk(fullLocalPath);
                    } else {
                        console.log(`Bundle "${matchingBundle.name}", module "${fullLocalPath.path}"`);
                    }
                } else {
                    matchingBundle.addSkipChunk(fullLocalPath);
                }
                return matchingBundle.name;
            }
        }
    }

    let inlineRollup = new InlineRollup(site.importMapGenerator, inlineRollupOptions);
    let rollupOutput = await inlineRollup.generate(basedir, filename);
    if (rollupOutput instanceof Error) {
        responseFields = InlineRollup.getErrorResponse(rollupOutput);
    } else {
        responseFields = inlineRollup.getRollupResponse(baseDirLocalPath, entryPointLocalPath, rollupOutput, foundBundles);
    }
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
