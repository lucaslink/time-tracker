<script lang="ts">
	import { timeEntries, projects, clients } from '$lib/store';
	
	let { entry } = $props<{ entry: any }>();
	
	let isEditing = $state(false);
	
	// Edit state
	let editDate = $state('');
	let editStartTimeStr = $state('');
	let editEndTimeStr = $state('');
	let editDescription = $state('');
	let editProjectId = $state('');

	function pad(n: number) {
		return n.toString().padStart(2, '0');
	}

	function startEdit() {
		const startDate = new Date(entry.startTime);
		editDate = startDate.toISOString().split('T')[0];
		
		editStartTimeStr = `${pad(startDate.getHours())}:${pad(startDate.getMinutes())}`;
		
		if (entry.endTime) {
			const endDate = new Date(entry.endTime);
			editEndTimeStr = `${pad(endDate.getHours())}:${pad(endDate.getMinutes())}`;
		} else {
			editEndTimeStr = '';
		}
		
		editDescription = entry.description || '';
		editProjectId = entry.projectId;
		isEditing = true;
	}

	function saveEdit() {
		const start = new Date(`${editDate}T${editStartTimeStr}`);
		let end = editEndTimeStr ? new Date(`${editDate}T${editEndTimeStr}`) : null;
		
		// Handle crossing midnight
		if (end && end < start) {
			end = new Date(end.getTime() + 24 * 60 * 60 * 1000);
		}
		
		const newStartTime = start.getTime();
		const newEndTime = end ? end.getTime() : null;
		const totalMs = newEndTime ? (newEndTime - newStartTime) : entry.duration; // keep original duration if running? Actually if it's running, endTime is null, duration is calculated live.
		
		$timeEntries = $timeEntries.map(e => {
			if (e.id === entry.id) {
				return {
					...e,
					projectId: editProjectId,
					startTime: newStartTime,
					endTime: newEndTime,
					duration: newEndTime ? totalMs : (Date.now() - newStartTime),
					description: editDescription
				};
			}
			return e;
		});
		
		isEditing = false;
	}

	function cancelEdit() {
		isEditing = false;
	}

	function deleteEntry() {
		$timeEntries = $timeEntries.filter(e => e.id !== entry.id);
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
			weekday: 'short',
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

	let project = $derived($projects.find(p => p.id === entry.projectId));
	let client = $derived(project ? $clients.find(c => c.id === project.clientId) : null);
</script>

{#if isEditing}
	<li class="p-4 bg-[#252526] border-y border-[#3c3c3c]">
		<div class="flex flex-col gap-3">
			<div class="flex flex-col md:flex-row gap-3">
				<div class="flex-1">
					<label for="project-{entry.id}" class="block text-xs text-[#858585] mb-1">Project</label>
					<select id="project-{entry.id}" bind:value={editProjectId} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:border-[#007acc] focus:outline-none">
						{#each $projects as p}
							<option value={p.id}>{p.name}</option>
						{/each}
					</select>
				</div>
				<div class="w-full md:w-44">
					<label for="date-{entry.id}" class="block text-xs text-[#858585] mb-1">Date</label>
					<input id="date-{entry.id}" type="date" bind:value={editDate} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:border-[#007acc] focus:outline-none" />
				</div>
				<div class="w-full md:w-28">
					<label for="start-{entry.id}" class="block text-xs text-[#858585] mb-1">Start Time</label>
					<input id="start-{entry.id}" type="time" bind:value={editStartTimeStr} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:border-[#007acc] focus:outline-none" required />
				</div>
				<div class="w-full md:w-28">
					<label for="end-{entry.id}" class="block text-xs text-[#858585] mb-1">End Time</label>
					<input id="end-{entry.id}" type="time" bind:value={editEndTimeStr} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:border-[#007acc] focus:outline-none" disabled={!entry.endTime} />
				</div>
			</div>
			<div>
				<label for="desc-{entry.id}" class="block text-xs text-[#858585] mb-1">Description</label>
				<input id="desc-{entry.id}" type="text" bind:value={editDescription} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:border-[#007acc] focus:outline-none" placeholder="Optional description" />
			</div>
			<div class="flex justify-end gap-2 mt-2">
				<button onclick={cancelEdit} class="px-3 py-1.5 text-sm text-[#cccccc] hover:bg-[#3c3c3c] rounded-md transition-colors">Cancel</button>
				<button onclick={saveEdit} disabled={!editStartTimeStr || (entry.endTime && !editEndTimeStr)} class="px-3 py-1.5 text-sm bg-[#007acc] hover:bg-[#005f9e] text-white rounded-md transition-colors disabled:opacity-50">Save</button>
			</div>
		</div>
	</li>
{:else}
	<li class="p-4 hover:bg-[#2b2d31] transition-none flex flex-col md:flex-row md:items-center justify-between gap-4 group text-sm border-b border-[#2b2d31] last:border-0">
		<div class="flex items-start gap-3 flex-1 min-w-0">
			<div class="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0" style="background-color: {project?.colorCode || '#007acc'};"></div>
			<div class="flex-1 min-w-0">
				<div class="flex items-center gap-2 mb-1">
					<span class="font-medium text-white">{project?.name || 'Unknown Project'}</span>
					<span class="text-[#858585] text-xs px-1.5 py-0.5 rounded border border-[#3c3c3c]">{client?.name || 'Unknown Client'}</span>
				</div>
				<div class="flex items-center gap-2 text-xs text-[#cccccc] mb-1">
					<span>{formatDate(entry.startTime)}</span>
					<span class="text-[#858585]">&bull;</span>
					<span>{formatTime(entry.startTime)} - {entry.endTime ? formatTime(entry.endTime) : 'Running'}</span>
				</div>
				{#if entry.description}
					<p class="text-xs text-[#858585] truncate mt-1 italic">"{entry.description}"</p>
				{/if}
			</div>
		</div>
		
		<div class="flex items-center justify-between md:justify-end gap-4 md:w-56 shrink-0">
			<span class="font-mono text-[#cccccc] text-base">{formatDuration(entry.duration)}</span>
			<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-none">
				<button 
					onclick={startEdit}
					class="text-[#858585] hover:text-[#cccccc] p-1.5 rounded-md hover:bg-[#3c3c3c]"
					title="Edit entry"
					aria-label="Edit entry"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
					</svg>
				</button>
				<button 
					onclick={deleteEntry}
					class="text-[#858585] hover:text-[#f48771] p-1.5 rounded-md hover:bg-[#3c3c3c]"
					title="Delete entry"
					aria-label="Delete entry"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
					</svg>
				</button>
			</div>
		</div>
	</li>
{/if}
