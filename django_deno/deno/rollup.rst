chrome://inspect
https://stackoverflow.com/questions/8494998/web-proxy-in-python-django/12260186
https://github.com/oakserver/oak
https://doc.deno.land/https/deno.land/x/oak/mod.ts#ListenOptionsBase
https://rollupjs.org/guide/en/#javascript-api
https://www.npmjs.com/package/rollup-plugin-sourcemaps
https://www.codota.com/code/javascript/functions/rollup/rollup
https://gist.github.com/Rich-Harris/d472c50732dab03efeb37472b08a3f32

rollupOutput entries:

// For assets, this contains
// {
//   fileName: string,              // the asset file name
//   source: string | Uint8Array    // the asset source
//   type: 'asset'                  // signifies that this is an asset
// }

// For chunks, this contains
// {
//   code: string,                  // the generated JS code
//   dynamicImports: string[],      // external modules imported dynamically by the chunk
//   exports: string[],             // exported variable names
//   facadeModuleId: string | null, // the id of a module that this chunk corresponds to
//   fileName: string,              // the chunk file name
//   implicitlyLoadedBefore: string[]; // entries that should only be loaded after this chunk
//   imports: string[],             // external modules imported statically by the chunk
//   importedBindings: {[imported: string]: string[]} // imported bindings per dependency
//   isDynamicEntry: boolean,       // is this chunk a dynamic entry point
//   isEntry: boolean,              // is this chunk a static entry point
//   isImplicitEntry: boolean,      // should this chunk only be loaded after other chunks
//   map: string | null,            // sourcemaps if present
//   modules: {                     // information about the modules in this chunk
//     [id: string]: {
//       renderedExports: string[]; // exported variable names that were included
//       removedExports: string[];  // exported variable names that were removed
//       renderedLength: number;    // the length of the remaining code in this module
//       originalLength: number;    // the original length of the code in this module
//     };
//   },
//   name: string                   // the name of this chunk as used in naming patterns
//   referencedFiles: string[]      // files referenced via import.meta.ROLLUP_FILE_URL_<id>
//   type: 'chunk',                 // signifies that this is a chunk
// }
