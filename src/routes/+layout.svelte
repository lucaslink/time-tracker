<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Time Tracker</title>
</svelte:head>

<div class="min-h-screen flex flex-col">
	<header class="sticky top-0 z-10 bg-[#181818] border-b border-[#2b2d31]">
		<div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
			<div class="flex items-center gap-2 text-[#e5e5e5]">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#007acc]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<span class="font-semibold text-[15px] tracking-tight">TimeTracker</span>
			</div>
			<nav class="flex items-center gap-2">
				<a href="/" class="px-3 py-1.5 rounded text-sm transition-colors hover:bg-[#2b2d31] {page.url.pathname === '/' ? 'bg-[#2b2d31] text-[#e5e5e5]' : 'text-[#cccccc]'}">Dashboard</a>
				<a href="/entries" class="px-3 py-1.5 rounded text-sm transition-colors hover:bg-[#2b2d31] {page.url.pathname.startsWith('/entries') ? 'bg-[#2b2d31] text-[#e5e5e5]' : 'text-[#cccccc]'}">Entries</a>
				<a href="/projects" class="px-3 py-1.5 rounded text-sm transition-colors hover:bg-[#2b2d31] {page.url.pathname.startsWith('/projects') ? 'bg-[#2b2d31] text-[#e5e5e5]' : 'text-[#cccccc]'}">Projects</a>
				<a href="/reports" class="px-3 py-1.5 rounded text-sm transition-colors hover:bg-[#2b2d31] {page.url.pathname.startsWith('/reports') ? 'bg-[#2b2d31] text-[#e5e5e5]' : 'text-[#cccccc]'}">Reports</a>
			</nav>
		</div>
	</header>

	<main class="flex-1 w-full max-w-5xl mx-auto px-4 py-8">
		{@render children()}
	</main>
</div>
