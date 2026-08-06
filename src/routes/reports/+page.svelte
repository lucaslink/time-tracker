<script lang="ts">
	import { timeEntries, projects, clients } from '$lib/store';
	import { exportToCSV } from '$lib/utils';
	
	let now = new Date();
	let startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
	let startOfWeek = new Date(now.setDate(now.getDate() - now.getDay())).setHours(0,0,0,0);
	
	now = new Date(); // reset
	let startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).getTime();

	// Computed stats
	let dailyTotal = $derived($timeEntries.filter(e => e.startTime >= startOfDay).reduce((acc, e) => acc + e.duration, 0));
	let weeklyTotal = $derived($timeEntries.filter(e => e.startTime >= startOfWeek).reduce((acc, e) => acc + e.duration, 0));
	let monthlyTotal = $derived($timeEntries.filter(e => e.startTime >= startOfMonth).reduce((acc, e) => acc + e.duration, 0));

	let projectStats = $derived(() => {
		const stats = new Map<string, { duration: number, color: string, name: string }>();
		$projects.forEach(p => stats.set(p.id, { duration: 0, color: p.colorCode, name: p.name }));
		
		$timeEntries.forEach(entry => {
			if (stats.has(entry.projectId)) {
				stats.get(entry.projectId)!.duration += entry.duration;
			}
		});
		
		return Array.from(stats.values()).filter(s => s.duration > 0).sort((a, b) => b.duration - a.duration);
	});

	function formatHours(ms: number) {
		const hours = (ms / (1000 * 60 * 60)).toFixed(1);
		return hours;
	}
	
	function formatDuration(ms: number) {
		const totalSeconds = Math.floor(ms / 1000);
		const hours = Math.floor(totalSeconds / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		if (hours > 0) return `${hours}h ${minutes}m`;
		return `${minutes}m`;
	}

	function formatDate(timestamp: number) {
		return new Date(timestamp).toLocaleDateString(undefined, {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function formatTime(timestamp: number) {
		return new Date(timestamp).toLocaleTimeString(undefined, {
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	function handleExport() {
		exportToCSV($timeEntries, $projects, $clients);
	}
</script>

<div class="space-y-8">
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-light text-[#cccccc] mb-1">Reports</h1>
			<p class="text-sm text-[#858585]">Insights and summaries of your logged time.</p>
		</div>
		<button onclick={handleExport} class="bg-[#007acc] hover:bg-[#005f9e] text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
				<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
			</svg>
			Export CSV
		</button>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-[#858585] mb-2">Today</h3>
			<div class="text-3xl font-light text-[#cccccc] tracking-tight">{formatHours(dailyTotal)}<span class="text-sm text-[#858585] font-normal ml-1">hrs</span></div>
		</div>
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-[#858585] mb-2">This Week</h3>
			<div class="text-3xl font-light text-[#cccccc] tracking-tight">{formatHours(weeklyTotal)}<span class="text-sm text-[#858585] font-normal ml-1">hrs</span></div>
		</div>
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-[#858585] mb-2">This Month</h3>
			<div class="text-3xl font-light text-[#cccccc] tracking-tight">{formatHours(monthlyTotal)}<span class="text-sm text-[#858585] font-normal ml-1">hrs</span></div>
		</div>
	</div>

	<div>
		<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Time by Project</h2>
		
		{#if projectStats().length === 0}
			<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-8 text-center text-[#858585]">
				No time recorded yet.
			</div>
		{:else}
			<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5 space-y-5">
				{#each projectStats() as stat}
					<div>
						<div class="flex justify-between items-end mb-1">
							<div class="flex items-center gap-2">
								<div class="w-2.5 h-2.5 rounded-full" style="background-color: {stat.color};"></div>
								<span class="text-sm text-[#cccccc]">{stat.name}</span>
							</div>
							<span class="text-[#858585] font-mono text-xs">{formatHours(stat.duration)} hrs</span>
						</div>
						<div class="h-1.5 w-full bg-[#252526] overflow-hidden">
							<div class="h-full" style="width: {Math.min((stat.duration / (weeklyTotal || 1)) * 100, 100)}%; background-color: {stat.color};"></div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<div>
		<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Detailed Export Preview</h2>
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-x-auto">
			{#if $timeEntries.length === 0}
				<div class="p-8 text-center text-[#858585]">
					No data available.
				</div>
			{:else}
				<table class="w-full text-left border-collapse min-w-[800px]">
					<thead>
						<tr class="bg-[#252526] border-b border-[#3c3c3c]">
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Date</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Client</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Project</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Time</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Duration</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Description</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-[#2b2d31]">
						{#each [...$timeEntries].sort((a,b) => b.startTime - a.startTime) as entry}
							{@const project = $projects.find(p => p.id === entry.projectId)}
							{@const client = project ? $clients.find(c => c.id === project.clientId) : null}
							<tr class="hover:bg-[#252526] transition-colors text-sm text-[#cccccc]">
								<td class="p-3 whitespace-nowrap">{formatDate(entry.startTime)}</td>
								<td class="p-3 whitespace-nowrap">{client?.name || 'Unknown'}</td>
								<td class="p-3 whitespace-nowrap flex items-center gap-2">
									<div class="w-2 h-2 rounded-full" style="background-color: {project?.colorCode || '#858585'};"></div>
									{project?.name || 'Unknown'}
								</td>
								<td class="p-3 whitespace-nowrap text-xs text-[#858585]">
									{formatTime(entry.startTime)} - {entry.endTime ? formatTime(entry.endTime) : 'Running'}
								</td>
								<td class="p-3 whitespace-nowrap font-mono">{formatDuration(entry.duration)}</td>
								<td class="p-3 text-xs text-[#858585] truncate max-w-[200px]" title={entry.description}>{entry.description || '-'}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	</div>
</div>
