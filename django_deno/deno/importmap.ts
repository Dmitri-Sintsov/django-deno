// import {Path, WINDOWS_SEPS} from "https://deno.land/x/path/mod.ts";

class LocalPath {
    path: string;

    constructor(path: string) {
        this.path = path;
    }

    static fromPathParts(parts: string[]) {
        let instance = new this(LocalPath.join(parts));
        return instance;
    }

    public getSeparator(): string {
        return this.path.search('/')  === -1 ? '\\' : '/';
    }

    public split(): string[] {
        return this.path.split(
            this.getSeparator()
        );
    }

    static join(parts: string[]) {
        return parts.join('/');
    }

    public getDirParts(): string[] {
        return this.split().slice(0, -1);
    }

    public getBaseName(): string {
        // Use object deconstructing to get last element from array
        const {length, [length-1]: baseName} = this.split();
        return baseName;
    };

    public getDirName(): string {
        return LocalPath.join(this.getDirParts());
    }

    /**
    >>> import os
    >>> path = "/home/User/Desktop/file.txt"
    >>> start = "/home/User"
    >>> os.path.relpath(path, start)
    'Desktop/file.txt'
    >>> start = "/home/User/Download"
    >>> os.path.relpath(path, start)
    '../Desktop/file.txt'
    */
    // Assumes that both this.path and startDir are absolute pathes.
    public toRelativePath(startDir: string): string {
        let startDirParts = new LocalPath(startDir).split();
        let thisDirParts = this.getDirParts();
        let idx: string = '0';
        let i: number = Number(idx);
        // Find common base path.
        for (idx in startDirParts) {
            i = Number(idx);
            if (i >= thisDirParts.length || startDirParts[i] !== thisDirParts[i]) {
                break;
            }
        }
        // Walk down to common base path with '..'.
        let parents = Array(startDirParts.length - i).fill('..');
        let relParts = parents.concat(thisDirParts.slice(i));
        if (relParts.length !== 0) {
            relParts.push(this.getBaseName());
            return LocalPath.fromPathParts(relParts).path;
        } else {
            return this.path;
        }
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
        } else if (relPathItem.val.endsWith('.')) {
            let packedKeyNoRel = relPathItem.key.replace(/^\.+/gm, '');
            packedPathItem.val = relPathItem.val.slice(0, -1) + packedKeyNoRel;
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

    public getImportMap(esModulePath: string, esModuleName: string): MapItems {
        let esModuleLocalPath = LocalPath.fromPathParts(
            new LocalPath(esModulePath)
            .split()
            .concat([esModuleName])
        );
        this.moduleBaseDir = new LocalPath(
            this.baseMap.map[esModuleLocalPath.path]
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
