<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { lastDeletedEntry, timeEntries, confirmModal } from '$lib/store';

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

	<!-- Global Undo Toast -->
	{#if $lastDeletedEntry}
		<div class="fixed bottom-6 right-6 bg-[#252526] border border-[#3c3c3c] p-4 rounded-xl shadow-xl flex items-center gap-4 z-50 animate-in fade-in slide-in-from-bottom-4">
			<span class="text-[#cccccc] text-sm">Entry deleted.</span>
			<button 
				onclick={() => {
					if ($lastDeletedEntry) {
						$timeEntries = [...$timeEntries, $lastDeletedEntry];
						$lastDeletedEntry = null;
					}
				}} 
				class="text-[#007acc] hover:text-[#005f9e] font-medium text-sm transition-colors"
			>
				Undo
			</button>
			<button 
				onclick={() => $lastDeletedEntry = null} 
				class="text-[#858585] hover:text-[#cccccc] p-1 rounded-md transition-colors"
				aria-label="Dismiss"
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
				</svg>
			</button>
		</div>
	{/if}

	<!-- Global Confirm Modal -->
	{#if $confirmModal.isOpen}
		<div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[60] animate-in fade-in">
			<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-6 shadow-2xl max-w-sm w-full mx-4">
				<h3 class="text-lg font-medium text-[#cccccc] mb-2">Confirm Action</h3>
				<p class="text-sm text-[#858585] mb-6">{$confirmModal.message}</p>
				<div class="flex justify-end gap-3">
					<button 
						onclick={() => $confirmModal.isOpen = false} 
						class="px-4 py-2 text-sm text-[#cccccc] hover:bg-[#2b2d31] rounded-lg transition-colors"
					>
						Cancel
					</button>
					<button 
						onclick={() => {
							if ($confirmModal.onConfirm) $confirmModal.onConfirm();
							$confirmModal.isOpen = false;
						}} 
						class="px-4 py-2 text-sm bg-[#ac1d1d] hover:bg-[#8c1717] text-white rounded-lg transition-colors"
					>
						Delete
					</button>
				</div>
			</div>
		</div>
	{/if}

	<main class="flex-1 w-full max-w-5xl mx-auto px-4 py-8">
		{@render children()}
	</main>
</div>
