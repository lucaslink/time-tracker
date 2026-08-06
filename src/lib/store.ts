import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createLocalStore<T>(key: string, startValue: T) {
	let initialValue = startValue;
	if (browser) {
		const storedValue = window.localStorage.getItem(key);
		if (storedValue) {
			try {
				initialValue = JSON.parse(storedValue);
			} catch (e) {
				console.error("Could not parse stored value for key: ", key);
			}
		}
	}
	const store = writable<T>(initialValue);
	
	if (browser) {
		store.subscribe(value => {
			window.localStorage.setItem(key, JSON.stringify(value));
		});
	}
	
	return store;
}

export type Client = { id: string, name: string, createdAt: number };
export type Project = { id: string, clientId: string, name: string, colorCode: string, createdAt: number };
export type TimeEntry = { id: string, projectId: string, startTime: number, endTime: number | null, duration: number, description: string };

export const clients = createLocalStore<Client[]>('clients', []);
export const projects = createLocalStore<Project[]>('projects', []);
export const timeEntries = createLocalStore<TimeEntry[]>('timeEntries', []);
export const activeTimer = createLocalStore<{projectId: string | null, startTime: number | null, description: string}>('activeTimer', { projectId: null, startTime: null, description: '' });
