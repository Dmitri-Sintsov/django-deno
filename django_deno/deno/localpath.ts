/**
 * https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
 * When specifying a path, always use forward slashes, even on Windows.
 */

// import {WINDOWS_SEPS} from "https://deno.land/x/path/mod.ts";

import { isAbsolute } from "jsr:@std/path";
import { existsSync } from "jsr:@std/fs";
import { GlobOptions, globToRegExp } from "jsr:@std/path";


let systemSeparator = (Deno.build.os === 'windows') ? '\\' : '/';

class LocalPath {
    path: string;

    constructor(path: string) {
        this.path = path;
        // Normalize path separators ('\\' for Windows, '/' for Linux),
        // otherwise .startsWith() / .endsWith() may fail.
        let pathParts = this.split();
        this.path = LocalPath.join(pathParts);
    }

    static fromPathParts(parts: string[]): LocalPath {
        let instance = new this(LocalPath.join(parts));
        return instance;
    }

    static getCwd(): LocalPath {
        return new this(Deno.cwd());
    }

    static getFullLocalPath(relPathStr: string): LocalPath {
        let instance = this.getCwd();
        if (isAbsolute(relPathStr)) {
            return new this(relPathStr);
        } else {
            instance = instance.traverseStr(relPathStr);
        }
        if (!instance.exists()) {
            throw new Error(`Error in getFullLocalPath, relPathStr "${relPathStr}" path does not exists: "${instance.path}"`);
        }
        return instance;
    }

    public isAbsolute(): boolean {
        return isAbsolute(this.path);
    }

    public toString() : string {
        return this.path;
    }

    static removeRelDir(path: string) {
        return path.replace(/^\.+/gm, '');
    }

    public exists(): boolean {
        return existsSync(this.path);
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
        let result = parts.join(systemSeparator);
        return result;
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

    public is(anotherLocalPath: LocalPath): boolean {
        return this.path == anotherLocalPath.path;
    }

    public matchesLocal(matchPath: LocalPath): boolean {
        let thisParts = this.split().reverse();
        let matchParts = matchPath.split().reverse();
        if (thisParts.length < matchParts.length) {
            return false;
        }
        for (let [idx, matchPart] of Object.entries(matchParts) as any) {
            let matchRegExp = globToRegExp(matchPart, {
                extended: true,
                globstar: false,
            } as GlobOptions);
            if (!thisParts[idx].match(matchRegExp)) {
                return false;
            }
        }
        return true;
    }

    public matchesGlobStar(matchPath: LocalPath): boolean {
        let matchGlobPath = LocalPath.fromPathParts(['**', ...matchPath.split()])
        let matchRegExp = globToRegExp(matchGlobPath.path, {
            extended: true,
            globstar: true,
        } as GlobOptions);
        return this.path.match(matchRegExp) ? true : false
    }

    public matches(matchPath: LocalPath, useGlobStar: boolean = true): boolean {
        return (useGlobStar) ? this.matchesGlobStar(matchPath) : this.matchesLocal(matchPath);
    }

    public matchesStr(matchPathStr: string, useGlobStar: boolean = true): boolean {
        return this.matches(new LocalPath(matchPathStr), useGlobStar);
    }

    public traverseRelative(relPath: LocalPath): LocalPath {
        var thisParts = this.split();
        var relDirParts = relPath.getDirParts();
        var joinDirParts = relDirParts.slice();
        for (let part of relDirParts) {
            if (part == '.') {
                joinDirParts.shift();
                continue;
            } else if (part == '..') {
                thisParts.pop();
                joinDirParts.shift();
            } else {
                break;
            }
        }
        let relParts = thisParts.concat(joinDirParts);
        relParts.push(relPath.getBaseName());
        return LocalPath.fromPathParts(relParts);
    }

    public traverseAbsolute(absPath: LocalPath): LocalPath {
        var thisParts = this.split();
        var absPathParts = absPath.split();
        if (thisParts.length > absPathParts.length) {
            throw new Error(`Error in traverseAbsolute, ${this.path} is longer than ${absPath.path}`);
        }
        for (var i = 0; i < thisParts.length; i++) {
            if (thisParts[i] !== absPathParts[i]) {
                let parts = [...thisParts, ...absPathParts.slice(i)];
                return LocalPath.fromPathParts(parts);
            }
        }
        throw new Error(`Error in traverseAbsolute, ${absPath.path} equal to ${this.path}`);
    }

    public traverseStr(pathStr: string, params?: { onlyRelative: boolean | null}): LocalPath {
        if (typeof params === 'undefined') {
            params = {onlyRelative: false};
        }
        if (isAbsolute(pathStr) && this.isAbsolute()) {
            let absPath = new LocalPath(pathStr)
            if (params.onlyRelative || pathStr.startsWith(this.path)) {
                return absPath;
            } else {
                // warning: not all absolute pathes are compatible, use with care.
                return this.traverseAbsolute(absPath);
            }
        } else {
            return this.traverseRelative(
                new LocalPath(pathStr)
            );
        }
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

export { systemSeparator, LocalPath };
