// See autogenerated import_map.json for latest successful run specific modules versions.
import { Context } from "https://deno.land/x/oak/mod.ts";

import type { ManualChunksOption, ModuleFormat, PreserveEntrySignaturesOption, RollupCache } from "https://deno.land/x/drollup/deps.ts";
import type { RollupOptions, OutputOptions } from "https://deno.land/x/drollup/mod.ts";

import { rollup, RollupOutput } from "https://deno.land/x/drollup/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup/src/rollup/write.ts";
import { denoResolver, DenoResolverOptions } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/denoResolver.ts";
import { terser } from "https://deno.land/x/drollup/plugins/terser/mod.ts";
import { parse } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/parse.ts";
import { resolveId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/resolveId.ts";
import { handleUnresolvedId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/handleUnresolvedId.ts";
import { exists } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/exists.ts";

import { LocalPath } from './localpath.ts';
import { ImportMapGenerator } from "./importmap.ts";

class ResponseFields {
    status: any;
    type: any;
    body: any;

    toOakContext(context: Context): void {
        context.response.status = this.status;
        context.response.type = this.type;
        context.response.body = this.body;
    }

    constructor() {
        this.status = 500;
        this.type = 'application/javascript';
        this.body = 'Empty body';
    }
};

class RollupBundleItem {
    /**
     * Warning: make sure bundle name does not match any of bundled module file names,
     * otherwise namespace clash could occur.
     */
    name?: string;
    nameLocalPath?: LocalPath;
    writeEntryPoint?: string;
    writeEntryPointLocalPath?: LocalPath;
    excludes?: string[];
    matches: string[];
    virtualEntryPoints?: 'matches' | string[];
    virtualEntryPointsExcludes?: 'excludes' | string[];
    skipChunks?: LocalPath[];

    constructor(options: Partial<RollupBundleItem> = {}) {
        this.matches = [];
        this.skipChunks = [];
        Object.assign(this, options);
        if (this.writeEntryPoint) {
            this.writeEntryPointLocalPath = new LocalPath(this.writeEntryPoint);
        }
        if (this.name) {
            this.nameLocalPath = new LocalPath(`${this.name}.js`);
        }
        if (!this.matches) {
            this.matches = [];
        }
        if (!this.excludes) {
            this.excludes = [];
        }
        if (!this.virtualEntryPoints) {
            this.virtualEntryPoints = [];
        }
        if (!this.virtualEntryPointsExcludes) {
            this.virtualEntryPointsExcludes = [];
        }
    }

    public isBundleChunk(chunkName: string) : boolean {
        return this.nameLocalPath!.matchesStr(chunkName);
    }

    public addSkipChunk(chunkPath: LocalPath) {
        this.skipChunks!.push(chunkPath);
    }

    public isSkipChunk(facadeModuleLocalPath: LocalPath): boolean {
        for (let skipChunk of this.skipChunks!) {
            if (skipChunk.is(facadeModuleLocalPath)) {
                return true;
            }
        }
        return false;
    }

    public isWriteEntryPoint(entryPointLocalPath: LocalPath): boolean {
        if (this.writeEntryPointLocalPath) {
            return entryPointLocalPath.matches(this.writeEntryPointLocalPath);
        } else {
            return true;
        }
    }

    public setVirtualEntryPoint(moduleInfo: any): boolean {
        let isVirtualEntry: boolean = !moduleInfo.isEntry;
        // Add entry point, so exports from nested smaller modules will be preserved in 'djk' chunk.
        moduleInfo.isEntry = true;
        return isVirtualEntry;
    }

    hasLocalPath(fullLocalPath: LocalPath, matches?: string[]): boolean {
        if (!matches) {
            throw new Error("matches argument is required");
        }
        for (let bundleItemMatch of matches) {
            let bundleItemMatchLocalPath = new LocalPath(bundleItemMatch);
            if (fullLocalPath.matches(bundleItemMatchLocalPath)) {
                return true;
            }
        }
        return false;
    }

    public hasMatchingPath(fullLocalPath: LocalPath, matches?: string[], excludes?: string[]): boolean {
        if (!matches) {
            matches = this.matches;
        }
        if (!excludes) {
            excludes = this.excludes;
        }
        if (this.hasLocalPath(fullLocalPath, excludes)) {
            // console.log(`excluding "${fullLocalPath.path}"`);
            return false;
        }
        if (this.hasLocalPath(fullLocalPath, matches)) {
            // console.log(`matching "${fullLocalPath.path}"`);
            return true;
        }
        return false;
    }

    public isVirtualEntry(fullLocalPath: LocalPath): boolean {
        let matches = (this.virtualEntryPoints === 'matches') ? this.matches : this.virtualEntryPoints;
        let excludes = (this.virtualEntryPointsExcludes === 'excludes') ? this.excludes : this.virtualEntryPointsExcludes;
        return this.hasMatchingPath(fullLocalPath, matches, excludes);
    }

}


class RollupBundleSet {
    bundles: { [key: string]: RollupBundleItem };

    constructor() {
        this.bundles = {};
    }

    /**
     * Do not override existing singleton with new instance created by InlineRollupOptions.getBundleChunk,
     * otherwise RollupBUndleItem.skipChunks value will be reset.
     */
    public add(bundle: RollupBundleItem): RollupBundleItem {
        if (bundle.name) {
            if (typeof this.bundles[bundle.name] === 'undefined') {
                this.bundles[bundle.name] = bundle;
            }
            return this.bundles[bundle.name];
        } else {
            throw new Error('Bundle name has to be initialized')
        }
    }

    public getWriteBundle(entryPointLocalPath: LocalPath): RollupBundleItem | false {
        let bundleName: string;
        let bundle: RollupBundleItem;
        for ([bundleName, bundle] of Object.entries(this.bundles)) {
            if (bundle.isWriteEntryPoint(entryPointLocalPath)) {
                return bundle;
            }
        }
        return false;
    }

    public getBundleChunk(chunkPathStr: string): RollupBundleItem | false {
        let bundleName: string;
        let bundle: RollupBundleItem;
        let result: RollupBundleItem | false = false;
        for ([bundleName, bundle] of Object.entries(this.bundles)) {
            if (bundle.isBundleChunk(chunkPathStr)) {
                if (result) {
                    throw new Error(
                        `One chunk "${chunkPathStr}" cannot belong to multiple bundles "${result.name}" "${bundleName}"`
                    )
                }
                result = bundle;
            }
        }
        return result;
    }

    public isSkipChunk(facadeModuleLocalPath: LocalPath): boolean {
        let bundleName: string;
        let bundle: RollupBundleItem;
        for ([bundleName, bundle] of Object.entries(this.bundles)) {
            if (bundle.isSkipChunk(facadeModuleLocalPath)) {
                return true;
            }
        }
        return false;
    }

    public isWritableChunk(baseDirLocalPath: LocalPath, writeBundle: RollupBundleItem | false, chunkObj: any): boolean {
        let facadeModuleLocalPath = (chunkObj.facadeModuleId) ?
                baseDirLocalPath.traverseStr(chunkObj.facadeModuleId) : false;
        if (facadeModuleLocalPath) {
            return !this.isSkipChunk(facadeModuleLocalPath);
        } else {
            if (this.getBundleChunk(chunkObj.fileName)) {
                return writeBundle? true : false;
            } else {
                return true;
            }
        }
    }

}


class InlineRollupOptions {
    bundles?: RollupBundleItem[];
    cache?: RollupCache;
    chunkFileNames?: string;
    inlineFileMap?: boolean;
    moduleFormat?: ModuleFormat;
    manualChunks?: ManualChunksOption;
    relativePaths?: boolean;
    staticFilesResolver?: boolean;
    terser?: boolean;
    withCache?: boolean;

    constructor(options: Partial<InlineRollupOptions> = {}) {
        Object.assign(this, options);
    }

    public getBundleChunk(fullLocalPath: LocalPath): RollupBundleItem | false {
        if (this.bundles) {
            let bundleName: string = '';
            let rollupBundleItemOptions: RollupBundleItem;
            for ([bundleName, rollupBundleItemOptions] of Object.entries(this.bundles)) {
                rollupBundleItemOptions.name = bundleName;
                let rollupBundleItem = new RollupBundleItem(rollupBundleItemOptions);
                if (rollupBundleItem.hasMatchingPath(fullLocalPath)) {
                    // console.log(`Matched bundle name: "${rollupBundleItem.name}" script "${fullLocalPath.path}"`);
                    return rollupBundleItem;
                }
            }
        }
        return false;
    }

}

class InlineRollup {

    importMapGenerator: ImportMapGenerator;
    options: InlineRollupOptions;

    constructor (importMapGenerator: ImportMapGenerator, options: InlineRollupOptions) {
        this.importMapGenerator = importMapGenerator;
        this.options = options;
    }

    getStaticFilesResolver() {
        let resolverOptions: DenoResolverOptions = {};
        return async (source: string, importer?: string) => {
            let id = resolveId(source, importer);
            let url = parse(id);

            if (!url) {
                return handleUnresolvedId(id, importer);
            }

            if (!(await exists(url, resolverOptions.fetchOpts))) {
                // We assume extensionless imports are from bundling commonjs
                // as in Deno extensions are compulsory. We assume that the
                // extensionless commonjs file is JavaScript and not TypeScript.
                id += ".js";
                url = new URL(`${url.href}.js`);
            }

            if (!(await exists(url, resolverOptions.fetchOpts))) {
                // id = id.substr(0, id.length - 3);
                // return handleUnresolvedId(id, importer);
                return this.importMapGenerator.resolve(
                    Deno.cwd(), source, importer, this.options.relativePaths
                );
            }
            return id;
        };
    }

    async generate(basedir: string | null, filename: string): Promise<Error | RollupOutput> {
        // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
        // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
        // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api

        const outputOptions: OutputOptions = {
            format: this.options.moduleFormat ? this.options.moduleFormat: 'es',
            minifyInternalExports: false,
            plugins: [],
            // preserveModules: true,
            // preserveModulesRoot: 'src',
            sourcemap: this.options.inlineFileMap ? 'inline' : true,
        };

        if (outputOptions.format !== 'es') {
            // https://rollupjs.org/guide/en/#outputexports
            outputOptions.exports = 'named';
            if (outputOptions.format === 'amd') {
                // https://rollupjs.org/guide/en/#outputamd
                outputOptions.amd = {autoId: true};
            }
        }

        if (this.options.chunkFileNames) {
            outputOptions.chunkFileNames = this.options.chunkFileNames;
        }

        if (this.options.manualChunks) {
            outputOptions.manualChunks = this.options.manualChunks;
        }

        let rollupPlugins : any[] = [];

        if (this.options.staticFilesResolver) {
            let resolver = denoResolver();
            resolver.resolveId = this.getStaticFilesResolver();
            rollupPlugins.push(resolver);
        }

        if (this.options.terser) {
            rollupPlugins.push(terser({
                mangle: true,
                toplevel: false,
                output: {
                    comments: false,
                }
            }));
        }

        let inputOptions = filename;

        const options: RollupOptions = {
            input: inputOptions,
            output: outputOptions,
            plugins: rollupPlugins,
            // preserveEntrySignatures: 'exports-only' as PreserveEntrySignaturesOption,
            treeshake: false,
        };

        if (this.options.cache) {
            options.cache = this.options.cache;
        }

        let rollupOutput: RollupOutput;

        let cwd = Deno.cwd();
        if (basedir) {
            Deno.chdir(basedir);
        }

        try {
            const bundle = await rollup(options);
            if (!this.options.inlineFileMap && bundle.cache) {
                // Add synthetic exports, when needed
                for (let mdl of bundle.cache.modules) {
                    if (mdl.id.endsWith('document.js')) {
                        // mdl.syntheticNamedExports = 'ActionTemplateDialog, Actions, Dialog, Grid, GridActions, GridRow, globalIoc, inherit, ui, TabPane';
                    }
                }
            }
            if (this.options.withCache) {
                // Update cache.
                this.options.cache = bundle.cache;
            }
            rollupOutput = await bundle.generate(options.output as OutputOptions);
            return rollupOutput;

        } catch(e) {
            return e;
        } finally {
            Deno.chdir(cwd);
        };
    }

    getErrorResponse(ex: Error): ResponseFields {
        let response = new ResponseFields();
        let msg = ex.toString();
        if (msg === 'Error') {
            let er = ex as any;
            if (er.code && er.stack) {
                msg = `${er.code}\n${er.stack}`;
            }
        }
        response.body = msg;
        return response;
    }

    getRollupResponse(
            baseDirLocalPath: LocalPath, entryPointLocalPath: LocalPath,
            rollupOutput: RollupOutput, bundles: RollupBundleSet
    ): ResponseFields {
        let response = new ResponseFields();
        response.status = 200;
        let chunks = [];
        let writeBundle: RollupBundleItem | false = bundles.getWriteBundle(entryPointLocalPath);
        for (const file of rollupOutput.output) {
            if (file.type === 'asset') {
                console.log('Todo: support assets', file);
            } else {
                // console.log('Chunk', file.modules);
                // https://github.com/cmorten/deno-rollup/blob/bb159fc3a8c3c9fdd0b57142cc7bf84ae93dd2f4/src/cli/build.ts
                // https://deno.land/x/drollup@2.41.0+0.16.1/src/rollup/write.ts
                if (this.options.inlineFileMap) {
                    response.body = file.code + `\n//# ${SOURCEMAPPING_URL}=${file.map!.toUrl()}\n`;
                    return response;
                } else {
                    // console.log(`chunk ${file.fileName}`);
                    // console.log(`isEntry=${file.isEntry} isDynamicEntry=${file.isDynamicEntry} isImplicitEntry=${file.isImplicitEntry}`);
                    if (bundles.isWritableChunk(baseDirLocalPath, writeBundle, file)) {
                        chunks.push({
                            code: file.code,
                            filename: file.fileName,
                            map: file.map!.toString(),
                        })
                    }
                }
            }
        }
        response.body = {'rollupFiles': chunks};
        return response;
    }

}

export { RollupBundleSet, InlineRollupOptions, InlineRollup };
