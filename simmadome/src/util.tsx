import {useRef} from 'react';


function removeIndex(arr: any[], index: number) {
	return arr.slice(0, index).concat(arr.slice(index+1));
}

function replaceIndex<T>(arr: T[], index: number, val: T) {
	return arr.slice(0, index).concat([val]).concat(arr.slice(index+1));
}

function append<T>(arr: T[], val: T) {
	return arr.concat([val]);
} 

function arrayOf<T>(length: number, func: (i: number) => T): T[] {
	var out: T[] = [];
	for (var i = 0; i < length; i++) {
		out.push(func(i));
	}
	return out;
}

function shallowClone<T>(obj: T): T {
	return Object.assign({}, obj);
}

let getUID = function() { // does NOT generate UUIDs. Meant to create list keys ONLY
	let id = 0;
	return function() { return id++ }
}()

type DistributiveOmit<T, K extends keyof any> = T extends any ? Omit<T, K> : never;
//type DistributivePick<T, K extends keyof T> = T extends any ? Pick<T, K> : never;

export {removeIndex, replaceIndex, append, arrayOf, shallowClone, getUID};
export type {DistributiveOmit};