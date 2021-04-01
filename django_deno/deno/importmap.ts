// import {Path, WINDOWS_SEPS} from "https://deno.land/x/path/mod.ts";

class LocalPath {
    path: string;

    constructor(path: string) {
        this.path = path;
    }

    public getSeparator(): string {
        return this.path.search('/') ? '/' : '\\';
    }

    public split(): string[] {
        return this.path.split(
            this.getSeparator()
        );
    }

    public join(parts: string[]) {
        return '/'.join(parts);
    }

    public getDirParts() string[]: {
        return this.split().slice(0, -1);
    }

    public getDirName(): string {
        return this.join(this.getDirParts());
    }

    public toRelativePath(startDir: string) {
        if (!this.path.startsWith(startDir)) {
            throw new Error(`${this.path} does not start with ${start}`);
        }
        let startDirParts = new LocalPath(startDir).split();
        let thisDirParts = this.getDirParts();
        let reverseStartDirParts = startDirParts.slice().reverse();
        let reverseThisDirParts = thisDirParts.slice().reverse();
        let relPath: string[] = [];
        // https://www.geeksforgeeks.org/python-os-path-relpath-method/
    }
}


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
        if (relPathItem.val == '') {
            packedPathItem.val = relPathItem.key;
        } else if (packedPathItem.val.endsWith('.')) {
            let packedKeyNoRel = relPathItem.key.replace(/^\.+/gm, '');
            packedPathItem.val = relPathItem.val.slice(0, -1) + packedKeyNoRel;
        } else {
            packedPathItem.val = relPathItem.val;
        }
        return packedPathItem;
    }

    public entries(): [string, string] {
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
        this.baseMap = new PathMap(ImportMapCache.baseMap);
        this.importMap = new PathMap(ImportMapCache.importMap);
    }

    public getImportMap(esModulePath): MapItems {
        this.moduleBaseDir = new LocalPath(
            this.baseMap.map[esModulePath]
        ).getDirName();
        let relativeImportMap: MapItems = {};
        let targetPath: string;
        let sourcePath: string;
        for ([targetPath, sourcePath] of this.importMap.entries()) {
            let relativeTargetPath = new LocalPath(targetPath);
            relativeImportMap[relativeTargetPath.toRelativePath(this.moduleBaseDir)] = sourcePath;
        }
        return relativeImportMap;
    }
};

export {ImportMapGenerator};
