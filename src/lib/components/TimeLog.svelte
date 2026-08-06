<script lang="ts">
	import { timeEntries } from '$lib/store';
	import TimeEntryItem from './TimeEntryItem.svelte';
</script>

<div class="mt-8">
	<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-3 flex items-center gap-2">
		<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-[#858585]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
		</svg>
		Time Entries
	</h2>
	
	{#if $timeEntries.length === 0}
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-8 text-center text-[#858585]">
			<p>No time entries yet.</p>
		</div>
	{:else}
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-hidden">
			<ul class="flex flex-col">
				{#each [...$timeEntries].sort((a, b) => b.startTime - a.startTime) as entry (entry.id)}
					<TimeEntryItem {entry} />
				{/each}
			</ul>
		</div>
	{/if}
</div>
