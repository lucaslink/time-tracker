<script lang="ts">
	import { projects, timeEntries } from '$lib/store';

	let projectId = $state('');
	let date = $state(new Date().toISOString().split('T')[0]);
	let startTimeStr = $state('09:00');
	let endTimeStr = $state('17:00');
	let description = $state('');

	function addManualEntry(e: Event) {
		e.preventDefault();
		if (!projectId) return;

		// Parse dates
		const start = new Date(`${date}T${startTimeStr}`);
		let end = new Date(`${date}T${endTimeStr}`);
		
		// Handle crossing midnight
		if (end < start) {
			end = new Date(end.getTime() + 24 * 60 * 60 * 1000);
		}
		
		const startTimeMs = start.getTime();
		const endTimeMs = end.getTime();
		const totalMs = endTimeMs - startTimeMs;

		if (totalMs <= 0) return;

		$timeEntries = [
			{
				id: crypto.randomUUID(),
				projectId,
				startTime: startTimeMs,
				endTime: endTimeMs,
				duration: totalMs,
				description: description.trim()
			},
			...$timeEntries
		];

		// Reset form partially
		description = '';
	}
</script>

<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5 mt-6">
	<h3 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Add Manual Entry</h3>
	<form onsubmit={addManualEntry} class="flex flex-col gap-4">
		<div class="flex flex-col md:flex-row gap-4">
			<div class="flex-1">
				<label for="manualProject" class="block text-xs text-[#858585] mb-1">Project</label>
				<select 
					id="manualProject" 
					bind:value={projectId} 
					class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full"
					required
				>
					<option value="" disabled>Select Project...</option>
					{#each $projects as project}
						<option value={project.id}>{project.name}</option>
					{/each}
				</select>
			</div>
			<div class="w-full md:w-44">
				<label for="manualDate" class="block text-xs text-[#858585] mb-1">Date</label>
				<input 
					id="manualDate" 
					type="date" 
					bind:value={date} 
					class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full"
					required
				/>
			</div>
			<div class="w-full md:w-36">
				<label for="manualStart" class="block text-xs text-[#858585] mb-1">Start Time</label>
				<input 
					id="manualStart" 
					type="time" 
					bind:value={startTimeStr} 
					class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full"
					required
				/>
			</div>
			<div class="w-full md:w-36">
				<label for="manualEnd" class="block text-xs text-[#858585] mb-1">End Time</label>
				<input 
					id="manualEnd" 
					type="time" 
					bind:value={endTimeStr} 
					class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full"
					required
				/>
			</div>
		</div>
		
		<div class="flex flex-col md:flex-row gap-4 items-end">
			<div class="flex-1 w-full">
				<label for="manualDesc" class="block text-xs text-[#858585] mb-1">Description (Optional)</label>
				<input 
					id="manualDesc" 
					type="text" 
					bind:value={description} 
					placeholder="What did you work on?" 
					class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full"
				/>
			</div>
			<button 
				type="submit"
				disabled={!projectId}
				class="w-full md:w-32 py-2 rounded-lg text-sm font-medium bg-[#3c3c3c] hover:bg-[#4d4d4d] text-[#cccccc] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
			>
				Add Time
			</button>
		</div>
	</form>
</div>
