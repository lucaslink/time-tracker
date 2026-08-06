<script lang="ts">
	import Timer from '$lib/components/Timer.svelte';
	import ManualEntry from '$lib/components/ManualEntry.svelte';
	import TimeLog from '$lib/components/TimeLog.svelte';
	import { clients, projects } from '$lib/store';
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-light text-[#cccccc] mb-1">Dashboard</h1>
		<p class="text-sm text-[#858585]">Track your time and see recent activity.</p>
	</div>

	{#if $clients.length === 0 || $projects.length === 0}
		<div class="bg-[#1e1e1e] border border-[#2b2d31] p-6 text-[#cccccc]">
			<h3 class="font-medium mb-2 flex items-center gap-2 text-white">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#007acc]" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
				</svg>
				Welcome to TimeTracker
			</h3>
			<p class="mb-4 text-sm text-[#858585]">To start tracking time, you first need to create a client and a project.</p>
			<a href="/projects" class="inline-block bg-[#007acc] text-white text-sm px-4 py-2 hover:bg-[#005f9e] transition-colors">
				Set up Projects
			</a>
		</div>
	{:else}
		<Timer />
		<ManualEntry />
	{/if}

	<TimeLog />
</div>
