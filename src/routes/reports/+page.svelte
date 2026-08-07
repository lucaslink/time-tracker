<script lang="ts">
	import { timeEntries, projects, clients } from '$lib/store';
	import { exportToCSV, type ExportRow } from '$lib/utils';
	
	let now = new Date();
	let startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
	let startOfWeek = new Date(now.setDate(now.getDate() - now.getDay())).setHours(0,0,0,0);
	
	now = new Date(); // reset
	let startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).getTime();
	let startOfYear = new Date(now.getFullYear(), 0, 1).getTime();

	// Filters
	let dateFilter = $state<'all' | 'week' | 'month' | 'year'>('all');
	let groupBy = $state<'none' | 'day-project' | 'project'>('none');
	let showDescription = $state(true);

	// Computed stats (all time vs recent)
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

	let reportPeriodString = $derived(() => {
		if (dateFilter === 'week') {
			const endOfWeek = new Date(startOfWeek + 6 * 24 * 60 * 60 * 1000);
			const startStr = new Date(startOfWeek).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
			const endStr = endOfWeek.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
			return `Week of ${startStr} - ${endStr}`;
		} else if (dateFilter === 'month') {
			return `Month of ${new Date(startOfMonth).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}`;
		} else if (dateFilter === 'year') {
			return `Year of ${new Date(startOfYear).toLocaleDateString(undefined, { year: 'numeric' })}`;
		}
		return 'All Time';
	});

	let exportRows = $derived(() => {
		// 1. Filter
		let filtered = $timeEntries;
		if (dateFilter === 'week') filtered = filtered.filter(e => e.startTime >= startOfWeek);
		if (dateFilter === 'month') filtered = filtered.filter(e => e.startTime >= startOfMonth);
		if (dateFilter === 'year') filtered = filtered.filter(e => e.startTime >= startOfYear);

		// Sort filtered first (oldest to newest) to maintain stable description order
		filtered = [...filtered].sort((a, b) => a.startTime - b.startTime);

		// 2. Group & Map
		let finalRows: ExportRow[] = [];

		if (groupBy === 'none') {
			finalRows = filtered.map(entry => {
				const project = $projects.find(p => p.id === entry.projectId);
				const client = project ? $clients.find(c => c.id === project.clientId) : null;
				
				return {
					date: formatDate(entry.startTime),
					clientName: client?.name || 'Unknown',
					projectName: project?.name || 'Unknown',
					projectColor: project?.colorCode || '#858585',
					timeStr: `${formatTime(entry.startTime)} - ${entry.endTime ? formatTime(entry.endTime) : 'Running'}`,
					durationStr: formatDuration(entry.duration),
					description: entry.description || '',
					rawStartTime: entry.startTime,
					rawDurationMs: entry.duration
				};
			});
		} else if (groupBy === 'day-project') {
			// Group by Date + ProjectId
			const map = new Map<string, ExportRow>();

			filtered.forEach(entry => {
				const dateStr = formatDate(entry.startTime);
				const project = $projects.find(p => p.id === entry.projectId);
				const client = project ? $clients.find(c => c.id === project.clientId) : null;
				
				const key = `${dateStr}-${entry.projectId}`;
				
				if (map.has(key)) {
					const existing = map.get(key)!;
					existing.rawDurationMs += entry.duration;
					existing.durationStr = formatDuration(existing.rawDurationMs);
					if (entry.description) {
						existing.description = existing.description 
							? `${existing.description}; ${entry.description}`
							: entry.description;
					}
				} else {
					map.set(key, {
						date: dateStr,
						clientName: client?.name || 'Unknown',
						projectName: project?.name || 'Unknown',
						projectColor: project?.colorCode || '#858585',
						timeStr: 'N/A',
						durationStr: formatDuration(entry.duration),
						description: entry.description || '',
						rawStartTime: entry.startTime,
						rawDurationMs: entry.duration
					});
				}
			});

			finalRows = Array.from(map.values());
		} else if (groupBy === 'project') {
			// Group by ProjectId only
			const map = new Map<string, ExportRow>();

			filtered.forEach(entry => {
				const project = $projects.find(p => p.id === entry.projectId);
				const client = project ? $clients.find(c => c.id === project.clientId) : null;
				
				const key = entry.projectId;
				
				if (map.has(key)) {
					const existing = map.get(key)!;
					existing.rawDurationMs += entry.duration;
					existing.durationStr = formatDuration(existing.rawDurationMs);
					if (entry.description) {
						existing.description = existing.description 
							? `${existing.description}; ${entry.description}`
							: entry.description;
					}
				} else {
					map.set(key, {
						date: 'N/A',
						clientName: client?.name || 'Unknown',
						projectName: project?.name || 'Unknown',
						projectColor: project?.colorCode || '#858585',
						timeStr: 'N/A',
						durationStr: formatDuration(entry.duration),
						description: entry.description || '',
						rawStartTime: entry.startTime,
						rawDurationMs: entry.duration
					});
				}
			});

			finalRows = Array.from(map.values());
		}

		// Always sort newest to oldest for the final table display
		return finalRows.sort((a, b) => b.rawStartTime - a.rawStartTime);
	});

	let totalExportHours = $derived(() => {
		const totalMs = exportRows().reduce((acc, row) => acc + row.rawDurationMs, 0);
		return (Math.floor(totalMs / 1000) / 3600).toFixed(2);
	});

	function handleExportCSV() {
		exportToCSV(
			exportRows(), 
			groupBy === 'none', 
			groupBy !== 'project', 
			showDescription, 
			dateFilter,
			reportPeriodString(),
			totalExportHours()
		);
	}

	function handleBackupJSON() {
		const data = {
			clients: $clients,
			projects: $projects,
			timeEntries: $timeEntries
		};
		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `timetracker-backup-${new Date().toISOString().split('T')[0]}.json`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}

	let fileInput: HTMLInputElement;

	function triggerRestore() {
		fileInput.click();
	}

	function handleRestore(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const content = e.target?.result as string;
				const data = JSON.parse(content);
				
				if (data.clients && data.projects && data.timeEntries) {
					if (confirm('This will replace all your current data. Are you sure you want to proceed?')) {
						$clients = data.clients;
						$projects = data.projects;
						$timeEntries = data.timeEntries;
						alert('Data successfully restored!');
					}
				} else {
					alert('Invalid backup file format.');
				}
			} catch (err) {
				alert('Error reading backup file.');
				console.error(err);
			}
			target.value = '';
		};
		reader.readAsText(file);
	}
</script>

<div class="space-y-8">
	<div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
		<div>
			<h1 class="text-2xl font-light text-[#cccccc] mb-1">Reports & Data</h1>
			<p class="text-sm text-[#858585]">Insights, summaries, and data management.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<button onclick={handleExportCSV} class="bg-[#252526] border border-[#3c3c3c] text-[#cccccc] hover:bg-[#007acc] hover:text-white hover:border-[#007acc] px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
				</svg>
				CSV Export
			</button>
			<button onclick={handleBackupJSON} class="bg-[#252526] border border-[#3c3c3c] text-[#cccccc] hover:bg-[#007acc] hover:text-white hover:border-[#007acc] px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
				</svg>
				Backup (JSON)
			</button>
			<button onclick={triggerRestore} class="bg-[#252526] border border-[#3c3c3c] text-[#cccccc] hover:bg-[#007acc] hover:text-white hover:border-[#007acc] px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM9 7.414V15a1 1 0 102 0V7.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 101.414 1.414L9 7.414z" clip-rule="evenodd" />
				</svg>
				Restore
			</button>
			<input type="file" accept=".json" bind:this={fileInput} onchange={handleRestore} class="hidden" />
		</div>
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
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-4">
			<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc]">Detailed Export Preview</h2>
			
			<div class="flex flex-wrap gap-3">
				<div>
					<label for="dateFilter" class="block text-xs text-[#858585] mb-1">Date Range</label>
					<select id="dateFilter" bind:value={dateFilter} class="bg-[#252526] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md focus:outline-none focus:border-[#007acc] w-full md:w-auto">
						<option value="all">All Time</option>
						<option value="week">This Week</option>
						<option value="month">This Month</option>
						<option value="year">This Year</option>
					</select>
				</div>
				<div>
					<label for="groupBy" class="block text-xs text-[#858585] mb-1">Grouping</label>
					<select id="groupBy" bind:value={groupBy} class="bg-[#252526] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md focus:outline-none focus:border-[#007acc] w-full md:w-auto">
						<option value="none">Individual Entries</option>
						<option value="day-project">Group by Day & Project</option>
						<option value="project">Group by Project</option>
					</select>
				</div>
				<div class="flex items-center gap-2 self-end mb-1">
					<input type="checkbox" id="showDescription" bind:checked={showDescription} class="w-4 h-4 bg-[#252526] border border-[#3c3c3c] rounded text-[#007acc] focus:ring-[#007acc] focus:ring-offset-0 focus:ring-1 cursor-pointer appearance-none checked:bg-[#007acc] checked:border-[#007acc]" />
					<label for="showDescription" class="text-xs text-[#cccccc] cursor-pointer select-none">Show Description</label>
				</div>
			</div>
		</div>
		
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-x-auto">
			{#if exportRows().length === 0}
				<div class="p-8 text-center text-[#858585]">
					No data available for the selected filters.
				</div>
			{:else}
				<table class="w-full text-left border-collapse min-w-[800px]">
					<thead>
						<tr class="bg-[#252526] border-b border-[#3c3c3c]">
							{#if groupBy !== 'project'}
								<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Date</th>
							{/if}
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Client</th>
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Project</th>
							{#if groupBy === 'none'}
								<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Time</th>
							{/if}
							<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Duration</th>
							{#if showDescription}
								<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Description</th>
							{/if}
						</tr>
					</thead>
					<tbody class="divide-y divide-[#2b2d31]">
						{#each exportRows() as row}
							<tr class="hover:bg-[#252526] transition-colors text-sm text-[#cccccc]">
								{#if groupBy !== 'project'}
									<td class="p-3 whitespace-nowrap">{row.date}</td>
								{/if}
								<td class="p-3 whitespace-nowrap">{row.clientName}</td>
								<td class="p-3 whitespace-nowrap flex items-center gap-2">
									<div class="w-2 h-2 rounded-full" style="background-color: {row.projectColor};"></div>
									{row.projectName}
								</td>
								{#if groupBy === 'none'}
									<td class="p-3 whitespace-nowrap text-xs text-[#858585]">{row.timeStr}</td>
								{/if}
								<td class="p-3 whitespace-nowrap font-mono">{row.durationStr}</td>
								{#if showDescription}
									<td class="p-3 text-xs text-[#858585] truncate max-w-[250px]" title={row.description}>{row.description || '-'}</td>
								{/if}
							</tr>
						{/each}
					</tbody>
					<tfoot class="bg-[#252526] border-t border-[#3c3c3c]">
						<tr class="text-sm">
							<td colspan={groupBy === 'none' ? 4 : (groupBy === 'project' ? 2 : 3)} class="p-3 text-right font-medium text-[#cccccc]">
								Total Hours for {reportPeriodString()}:
							</td>
							<td class="p-3 font-mono font-medium text-[#cccccc]">{totalExportHours()}h</td>
							{#if showDescription}
								<td></td>
							{/if}
						</tr>
					</tfoot>
				</table>
			{/if}
		</div>
	</div>
</div>
