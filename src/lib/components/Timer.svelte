<script lang="ts">
	import { activeTimer, projects, timeEntries } from '$lib/store';
	import { onMount, onDestroy } from 'svelte';

	let elapsedSeconds = $state(0);
	let interval: ReturnType<typeof setInterval>;

	function updateElapsed() {
		if ($activeTimer.startTime) {
			elapsedSeconds = Math.floor((Date.now() - $activeTimer.startTime) / 1000);
		} else {
			elapsedSeconds = 0;
		}
	}

	onMount(() => {
		updateElapsed();
		interval = setInterval(updateElapsed, 1000);
	});

	onDestroy(() => {
		if (interval) clearInterval(interval);
	});

	function toggleTimer() {
		if ($activeTimer.startTime) {
			// Stop timer
			const endTime = Date.now();
			const duration = endTime - $activeTimer.startTime;
			
			$timeEntries = [
				{
					id: crypto.randomUUID(),
					projectId: $activeTimer.projectId || '',
					startTime: $activeTimer.startTime,
					endTime: endTime,
					duration: duration,
					description: $activeTimer.description
				},
				...$timeEntries
			];

			$activeTimer = { projectId: null, startTime: null, description: '' };
			elapsedSeconds = 0;
		} else {
			// Start timer
			$activeTimer = { ...$activeTimer, startTime: Date.now() };
		}
	}

	function formatTime(totalSeconds: number) {
		const hours = Math.floor(totalSeconds / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		const seconds = totalSeconds % 60;
		return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
	}
</script>

<div class="bg-[#1e1e1e] border border-[#2b2d31] p-5 rounded-xl flex flex-col md:flex-row gap-4 items-center justify-between">
	<div class="flex-1 w-full flex flex-col md:flex-row gap-4">
		<select 
			bind:value={$activeTimer.projectId} 
			disabled={$activeTimer.startTime !== null}
			class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] w-full md:w-64 disabled:opacity-50"
		>
			<option value={null} disabled>Select Project...</option>
			{#each $projects as project}
				<option value={project.id}>{project.name}</option>
			{/each}
		</select>
		
		<input 
			type="text" 
			bind:value={$activeTimer.description} 
			placeholder="What are you working on?" 
			disabled={$activeTimer.startTime !== null}
			class="bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc] flex-1 min-w-0 disabled:opacity-50"
		/>
	</div>
	
	<div class="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
		<div class="text-3xl font-mono tracking-wider font-light text-[#cccccc]">
			{formatTime(elapsedSeconds)}
		</div>
		
		<button 
			onclick={toggleTimer}
			disabled={!$activeTimer.projectId && !$activeTimer.startTime}
			class="w-32 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed
				{$activeTimer.startTime 
					? 'bg-[#ac1d1d] text-white hover:bg-[#8c1717]' 
					: 'bg-[#007acc] text-white hover:bg-[#005f9e]'}"
		>
			{$activeTimer.startTime ? 'Stop' : 'Start'}
		</button>
	</div>
</div>
