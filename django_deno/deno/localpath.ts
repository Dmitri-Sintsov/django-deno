/**
 * https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
 * When specifying a path, always use forward slashes, even on Windows.
 */

// import {WINDOWS_SEPS} from "https://deno.land/x/path/mod.ts";

import { existsSync } from "https://deno.land/std/fs/mod.ts";


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

    static getFullLocalPath(relPathStr: string): LocalPath {
        let instance = new this(Deno.cwd());
        instance = instance.traverseStr(relPathStr);
        if (!instance.exists()) {
            throw new Error(`Error in getFullLocalPath, relPathStr "${relPathStr}" path does not exists: "${instance.path}"`);
        }
        return instance;
    }

    public toString() : string {
        return this.path;
    }

    static getSystemSeparator(): string {
        return (Deno.build.os == 'windows') ? '\\': '/';
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
        return parts.join(LocalPath.getSystemSeparator());
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

    public matches(matchPath: LocalPath): boolean {
        var thisParts = this.split().reverse();
        var matchParts = matchPath.split().reverse();
        if (thisParts.length < matchParts.length) {
            return false;
        }
        for (let [idx, matchPart] of Object.entries(matchParts) as any) {
            if (matchPart !== '*' && matchPart !== thisParts[idx]) {
                return false;
            }
        }
        return true;
    }

    public matchesStr(matchPathStr: string): boolean {
        return this.matches(new LocalPath(matchPathStr));
    }

    public traverse(relPath: LocalPath): LocalPath {
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

export { LocalPath };
