// Developed with drollup@2.41.0+0.16.1
import { Context } from "https://deno.land/x/oak/mod.ts";

import type { ManualChunksOption, ModuleFormat, OutputBundle, OutputPlugin, PreserveEntrySignaturesOption, RollupCache } from "https://deno.land/x/drollup/deps.ts";
import { rollup, RollupOutput } from "https://deno.land/x/drollup/mod.ts";
import type { NormalizedOutputOptions, OutputOptions } from "https://deno.land/x/drollup/mod.ts";
import { SOURCEMAPPING_URL } from "https://deno.land/x/drollup/src/rollup/write.ts";
import { denoResolver, DenoResolverOptions } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/denoResolver.ts";
import { terser } from "https://deno.land/x/drollup/plugins/terser/mod.ts";
import { parse } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/parse.ts";
import { resolveId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/resolveId.ts";
import { handleUnresolvedId } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/handleUnresolvedId.ts";
import { exists } from "https://deno.land/x/drollup/src/rollup-plugin-deno-resolver/exists.ts";

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

interface EntryPointsBundles {
    [key: string]: string | false;
}

interface RollupBundleItem {
    writeEntryPoint?: string;
    excludes?: string[];
    matches: string[];
    virtualEntryPoints?: boolean;
}

type Bundles = RollupBundleItem[];

interface InlineRollupOptions {
    bundles?: RollupBundleItem;
    cache?: RollupCache;
    chunkFileNames?: string;
    entryPoints?: EntryPointsBundles;
    inlineFileMap?: boolean;
    moduleFormat?: ModuleFormat;
    manualChunks?: ManualChunksOption,
    relativePaths?: boolean;
    staticFilesResolver?: boolean;
    terser?: boolean;
    withCache?: boolean;
}

let allExportsOutputPlugin: OutputPlugin = {
    name: 'allExportsOutputPlugin',
    generateBundle: function(options, bundle, isWrite: boolean) {
        if (typeof bundle['djk.js'] !== 'undefined') {
            let chunk: any = bundle['djk.js'];
            if (typeof chunk.exports !== 'undefined') {
                chunk.exports = ['ActionTemplateDialog', 'Actions', 'Dialog', 'Grid', 'GridActions', 'GridRow', 'globalIoc', 'inherit', 'startApp', 'ui', 'TabPane'];
            }
        }
    },
    writeBundle: function(options: NormalizedOutputOptions, bundle: OutputBundle) {
        if (typeof bundle['djk.js'] !== 'undefined') {
            let chunk: any = bundle['djk.js'];
            if (typeof chunk.exports !== 'undefined') {
                chunk.exports = ['ActionTemplateDialog', 'Actions', 'Dialog', 'Grid', 'GridActions', 'GridRow', 'globalIoc', 'inherit', 'startApp', 'ui', 'TabPane'];
            }
        }
    }
};

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

    async perform(basedir: string | null, filename: string) {
        // https://unpkg.com/rollup@2.41.0/dist/rollup.d.ts
        // https://gist.github.com/vsajip/94fb524746b151b5160924418e6882e5
        // https://deno.land/x/drollup@2.41.0+0.16.1#javascript-api
        let response = new ResponseFields();

        const outputOptions: OutputOptions = {
            // exports: 'named',
            format: this.options.moduleFormat ? this.options.moduleFormat: 'es',
            minifyInternalExports: false,
            plugins: [allExportsOutputPlugin],
            // preserveModules: true,
            sourcemap: this.options.inlineFileMap ? 'inline' : true,
        };

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
/*
        if (!this.options.inlineFileMap) {
            rollupPlugins.push({
				transform(code: string, id: string) {
					if (id.endsWith('document.js')) {
						return {
						    code, syntheticNamedExports: 'ActionTemplateDialog, Actions, Dialog, Grid, GridActions, GridRow, globalIoc, inherit, ui, TabPane'
                        };
					}
				},
            })
        }
*/
/*
        if (this.options.terser) {
            rollupPlugins.push(terser({
                mangle: false,
                output: {
                    comments: false,
                }
            }));
        }
*/

        let inputOptions = filename;

        const options = {
            input: inputOptions,
            output: outputOptions,
            plugins: rollupPlugins,
            // preserveEntrySignatures: 'exports-only' as PreserveEntrySignaturesOption,
            treeshake: false,
            cache: this.options.cache,
        };


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
            rollupOutput = await bundle.generate(options.output);

            response.status = 200;
            let chunks = [];
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
                        chunks.push({
                            code: file.code,
                            filename: file.fileName,
                            map: file.map!.toString(),
                        })
                    }
                }
            }
            response.body = {'rollupFiles': chunks};
            return response;
        } catch(e) {
            let msg = e.toString();
            if (msg === 'Error') {
                if (e.code && e.stack) {
                    msg = `${e.code}\n${e.stack}`;
                }
            }
            response.body = msg;
            return response;
        } finally {
            Deno.chdir(cwd);
        };
    }

}

export type { InlineRollupOptions, RollupBundleItem };
export { InlineRollup };
