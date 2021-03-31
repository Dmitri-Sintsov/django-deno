// import {Path, WINDOWS_SEPS} from "https://deno.land/x/path/mod.ts";

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
            return `{this.commonBaseStr}{pathStr}`;
        }
    }
}

interface MapItems {
    [index: string]: string;
};

interface PathMapCache {
    map: MapItems;
    base_key: string;
    base_val: string;
};

interface PathItem {
    key: string;
    val: string;
}


class PathMap {
    map: MapItems;
    baseKey: CommonBasePath;
    baseVal: CommonBasePath;

    constructor(cacheEntry: PathMapCache) {
        this.map = this.unpack(cacheEntry.map);
        this.baseKey = new CommonBasePath(cacheEntry.base_key);
        this.baseVal = new CommonBasePath(cacheEntry.base_val);

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

export {PathMap};
