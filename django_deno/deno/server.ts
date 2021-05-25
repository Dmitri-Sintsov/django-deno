// import { serve } from 'https://deno.land/std/http/server.ts'
import { existsSync } from "https://deno.land/std/fs/mod.ts";

import { parse } from "https://deno.land/std/flags/mod.ts";
import { Application, Router } from "https://deno.land/x/oak/mod.ts";


// @2.42.3%2B0.17.1
import type { RollupCache } from "https://deno.land/x/drollup/deps.ts";

import { LocalPath } from './localpath.ts';
import { ImportMapGenerator } from "./importmap.ts";
import type { InlineRollupOptions, RollupBundleItem } from './rollup.ts';
import { InlineRollup } from "./rollup.ts";

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

    let fullPathParts = new LocalPath(basedir).split();
    fullPathParts.push(filename);
    let entryPointLocalPath = LocalPath.fromPathParts(fullPathParts);
    let cachePath: string = entryPointLocalPath.path;

    inlineRollupOptions = value['options'];
    // https://github.com/lucacasonato/dext.ts/issues/65
    if (inlineRollupOptions.withCache && site.hasCache(cachePath)) {
        inlineRollupOptions.cache = site.getCache(cachePath);
    } else {
        inlineRollupOptions.cache = undefined;
    }

    if (!inlineRollupOptions.inlineFileMap) {
        inlineRollupOptions.chunkFileNames = "[name].js";
        inlineRollupOptions.manualChunks = (id: string, { getModuleInfo }): string | null | undefined => {
            let fullLocalPath = new LocalPath(Deno.cwd());
            fullLocalPath = fullLocalPath.traverseStr(id);
            if (!existsSync(fullLocalPath.path)) {
                throw new Error(`Error in manualChunks, id "${id}" path does not exists: "${fullLocalPath.path}"`);
            }
            let matchingBundle: RollupBundleItem | false = false;
            let bundleName: string = '';
            if (inlineRollupOptions.bundles) {
                let rollupBundleItem: RollupBundleItem;
                for ([bundleName, rollupBundleItem] of Object.entries(inlineRollupOptions.bundles)) {
                    for (let bundleItemMatch of rollupBundleItem.matches) {
                        let bundleItemMatchLocalPath = new LocalPath(bundleItemMatch);
                        if (fullLocalPath.matches(bundleItemMatchLocalPath)) {
                            console.log(`Matched bundle name: ${bundleName} script ${fullLocalPath.path}`);
                            matchingBundle = rollupBundleItem;
                            break;
                        }
                    }
                }
            }
            if (matchingBundle) {
                if (matchingBundle.writeEntryPoint && matchingBundle.virtualEntryPoints) {
                    let moduleInfo = getModuleInfo(id);
                    if (moduleInfo) {
                        let writeEntryPointLocalPath = new LocalPath(matchingBundle.writeEntryPoint);
                        let useVirtualEntryPoints = entryPointLocalPath.matches(writeEntryPointLocalPath);
                        if (useVirtualEntryPoints) {
                            console.log(`Using virtualEntryPoints, bundle ${bundleName}, entry point ${entryPointLocalPath.path}` )
                        } else {
                            console.log(`Bundle ${bundleName}, entry point ${entryPointLocalPath.path}` )
                        }
                        // Add entry point, so exports from nested smaller modules will be preserved in 'djk' chunk.
                        moduleInfo.isEntry = useVirtualEntryPoints;
                    }
                }
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
