import { LocalPath } from './localpath.ts';

class CommonBasePath {
    commonBaseStr: string;

    constructor(cacheEntry: string) {
        // deserialize
        this.commonBaseStr = cacheEntry;
    }

    public unpack(pathStr: string): string {
        if (pathStr.startsWith(this.commonBaseStr)) {
            return pathStr;
        } else {
            return `${this.commonBaseStr}${pathStr}`;
        }
    }
}

interface MapItems {
    [index: string]: string;
};

interface PathItem {
    key: string;
    val: string;
}

interface PathMapCache {
    map: MapItems;
    base_key: string;
    base_val: string;
};


class PathMap {
    map: MapItems;
    baseKey: CommonBasePath;
    baseVal: CommonBasePath;

    constructor(cacheEntry: PathMapCache) {
        // The order is important, .baseKey / .baseVal should be initialized before .map:
        this.baseKey = new CommonBasePath(cacheEntry.base_key);
        this.baseVal = new CommonBasePath(cacheEntry.base_val);
        this.map = this.unpack(cacheEntry.map);
    }

    public unpackRelation(relPathItem: PathItem): PathItem {
        let packedPathItem: PathItem = {key: relPathItem.key, val: ''};
        if (relPathItem.val === '') {
            packedPathItem.val = relPathItem.key;
        } else if (relPathItem.val.endsWith('.')) {
            let packedKeyNoRelDir = LocalPath.removeRelDir(relPathItem.key);
            packedPathItem.val = relPathItem.val.slice(0, -1) + packedKeyNoRelDir;
        } else {
            packedPathItem.val = relPathItem.val;
        }
        return packedPathItem;
    }

    public entries(): [string, string][] {
        return Object.entries(this.map);
    }

    public unpack(packedMap: MapItems): MapItems {
        let map: MapItems = {};
        let relKey: string;
        let relVal: string;
        for ([relKey, relVal] of Object.entries(packedMap)) {
            let relPathItem: PathItem = {key: relKey, val: relVal};
            let packedPathItem = this.unpackRelation(relPathItem);
            map[this.baseKey.unpack(packedPathItem.key)] = this.baseVal.unpack(packedPathItem.val);
        }
        return map;
    };

    findSource(source: string): string | null {
        let targetPath: string;
        let sourcePath: string;
        for ([targetPath, sourcePath] of this.entries()) {
            if (targetPath.endsWith(source)) {
                // return absoulte resolved path.
                return sourcePath;
            }
        }
        return null;
    }

    public resolveSource(source: LocalPath): string | null {
        source.cutAbsolutePath(this.baseVal.commonBaseStr);
        let sourceParts = source.split();
        while (sourceParts.length > 1) {
            sourceParts.shift();
            let sourceStr = LocalPath.join(sourceParts);
            let resolvedSource = this.findSource(sourceStr);
            if (resolvedSource !== null) {
                return resolvedSource;
            }
        }
        return null;
    }
}

interface ImportMapCache {
    baseMap: PathMapCache,
    importMap: PathMapCache,
};


class ImportMapGenerator {
    moduleBaseDir: string;
    baseMap: PathMap;
    importMap: PathMap;

    constructor(cacheEntry: ImportMapCache) {
        this.moduleBaseDir = '';
        this.baseMap = new PathMap(cacheEntry.baseMap);
        this.importMap = new PathMap(cacheEntry.importMap);
    }

    public resolve(importerDir: string, source: string, importer?: string, relativePaths?: boolean ): string {
        let resolvedPath: string | null;
        let importerDirLocalPath = new LocalPath(importerDir);
        let expectedSourceLocalPath = importerDirLocalPath.traverseStr(source);
        resolvedPath = this.importMap.resolveSource(expectedSourceLocalPath);
        if (resolvedPath === null) {
            resolvedPath = this.baseMap.resolveSource(expectedSourceLocalPath);
        }
        if (resolvedPath === null) {
            return source;
        } else {
            if (relativePaths) {
                // Get relative resolved path.
                let resolvedLocalPath = new LocalPath(resolvedPath);
                let relPath = resolvedLocalPath.toRelativePath(importerDir);
                // Return relative path as it's more compactly displayed in deno console output and in browser tools.
                return relPath;
            } else {
                return resolvedPath;
            }
        }
    }
};

export {ImportMapGenerator};
