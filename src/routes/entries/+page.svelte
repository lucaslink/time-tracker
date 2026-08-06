<script lang="ts">
	import { timeEntries } from '$lib/store';
	import TimeEntryItem from '$lib/components/TimeEntryItem.svelte';

	function getWeekStart(timestamp: number) {
		const d = new Date(timestamp);
		const day = d.getDay();
		const diff = d.getDate() - day;
		const start = new Date(d.setDate(diff));
		start.setHours(0, 0, 0, 0);
		return start.getTime();
	}

	function formatWeekRange(startTimestamp: number) {
		const start = new Date(startTimestamp);
		const end = new Date(start);
		end.setDate(end.getDate() + 6);

		const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
		return `${start.toLocaleDateString(undefined, options)} - ${end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
	}
	
	function formatDuration(ms: number) {
		const totalSeconds = Math.floor(ms / 1000);
		const hours = Math.floor(totalSeconds / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		if (hours > 0) return `${hours}h ${minutes}m`;
		return `${minutes}m`;
	}

	// Group entries by week
	let groupedEntries = $derived(() => {
		const groups = new Map<number, typeof $timeEntries>();
		
		for (const entry of $timeEntries) {
			const weekStart = getWeekStart(entry.startTime);
			if (!groups.has(weekStart)) {
				groups.set(weekStart, []);
			}
			groups.get(weekStart)!.push(entry);
		}
		
		// Sort weeks descending
		const sortedWeeks = Array.from(groups.keys()).sort((a, b) => b - a);
		
		return sortedWeeks.map(weekStart => {
			const entries = groups.get(weekStart)!.sort((a, b) => b.startTime - a.startTime);
			const totalDuration = entries.reduce((acc, e) => acc + e.duration, 0);
			return {
				weekStart,
				entries,
				totalDuration
			};
		});
	});
</script>

<div class="space-y-8">
	<div>
		<h1 class="text-2xl font-light text-[#cccccc] mb-1">Time Entries</h1>
		<p class="text-sm text-[#858585]">View all your time entries grouped by week.</p>
	</div>

	{#if $timeEntries.length === 0}
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-8 text-center text-[#858585]">
			No time entries yet.
		</div>
	{:else}
		<div class="space-y-6">
			{#each groupedEntries() as group (group.weekStart)}
				<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-hidden">
					<div class="px-4 py-3 bg-[#252526] border-b border-[#2b2d31] flex justify-between items-center">
						<h3 class="font-medium text-[#cccccc]">Week of {formatWeekRange(group.weekStart)}</h3>
						<span class="text-sm font-mono text-[#858585]">Total: {formatDuration(group.totalDuration)}</span>
					</div>
					<ul class="flex flex-col">
						{#each group.entries as entry (entry.id)}
							<TimeEntryItem {entry} />
						{/each}
					</ul>
				</div>
			{/each}
		</div>
	{/if}
</div>
