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

    public static removeRelDir(path: string) {
        return path.replace(/^\.+/gm, '');
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

    public traverse(relPath: LocalPath): LocalPath {
        var thisParts = this.split();
        var relDirParts = relPath.getDirParts().reverse();
        for (let part of relDirParts) {
            if (part == '..') {
                thisParts.pop();
            } else {
                break;
            }
        }
        thisParts.push(relPath.getBaseName());
        return LocalPath.fromPathParts(thisParts);
    }

    public traverseStr(relPathStr: string): LocalPath {
        return this.traverse(new LocalPath(relPathStr));
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

    public cutAbsolutePath(absPath: string) {
        if (this.path.startsWith(absPath)) {
            this.path = this.path.substr(absPath.length);
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
        while (sourceParts.length > 0) {
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

    public resolve(importerDir: string, source: string, importer?: string ): string {
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
            // Get relative resolved path.
            let resolvedLocalPath = new LocalPath(resolvedPath);
            let relPath = resolvedLocalPath.toRelativePath(importerDir);
            // Return relative path as it's more compactly displayed in deno console output and in browser tools.
            return relPath;
        }
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
