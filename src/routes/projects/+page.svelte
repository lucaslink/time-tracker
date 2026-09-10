<script lang="ts">
	import { clients, projects, confirmModal, type Client, type Project } from '$lib/store';

	let newClientName = $state('');
	
	let newProjectName = $state('');
	let newProjectClientId = $state('');
	let newProjectColor = $state('#007acc');

	// Edit Project State
	let editingProjectId = $state<string | null>(null);
	let editProjectName = $state('');
	let editProjectClientId = $state('');
	let editProjectColor = $state('');

	function addClient(e: Event) {
		e.preventDefault();
		if (!newClientName.trim()) return;
		
		const client: Client = {
			id: crypto.randomUUID(),
			name: newClientName.trim(),
			createdAt: Date.now()
		};
		
		$clients = [...$clients, client];
		newClientName = '';
	}

	function addProject(e: Event) {
		e.preventDefault();
		if (!newProjectName.trim() || !newProjectClientId) return;
		
		const project: Project = {
			id: crypto.randomUUID(),
			clientId: newProjectClientId,
			name: newProjectName.trim(),
			colorCode: newProjectColor,
			createdAt: Date.now()
		};
		
		$projects = [...$projects, project];
		newProjectName = '';
	}

	function deleteClient(id: string) {
		$confirmModal = {
			isOpen: true,
			message: 'Are you sure you want to delete this client? All associated projects will also be deleted. This cannot be undone.',
			onConfirm: () => {
				$clients = $clients.filter(c => c.id !== id);
				$projects = $projects.filter(p => p.clientId !== id);
			}
		};
	}

	function deleteProject(id: string) {
		$confirmModal = {
			isOpen: true,
			message: 'Are you sure you want to delete this project? This cannot be undone.',
			onConfirm: () => {
				$projects = $projects.filter(p => p.id !== id);
			}
		};
	}

	function startEditProject(project: Project) {
		editingProjectId = project.id;
		editProjectName = project.name;
		editProjectClientId = project.clientId;
		editProjectColor = project.colorCode;
	}

	function saveEditProject() {
		if (!editingProjectId || !editProjectName.trim() || !editProjectClientId) return;
		
		$projects = $projects.map(p => {
			if (p.id === editingProjectId) {
				return { ...p, name: editProjectName.trim(), colorCode: editProjectColor, clientId: editProjectClientId };
			}
			return p;
		});
		
		editingProjectId = null;
	}

	function cancelEditProject() {
		editingProjectId = null;
	}
	
	function getActiveClientProjects(clientId: string) {
		return $projects.filter(p => p.clientId === clientId && !p.isArchived);
	}

	function getArchivedClientProjects(clientId: string) {
		return $projects.filter(p => p.clientId === clientId && p.isArchived);
	}

	function toggleArchiveProject(id: string) {
		$projects = $projects.map(p => {
			if (p.id === id) {
				return { ...p, isArchived: !p.isArchived };
			}
			return p;
		});
	}
</script>

<div class="space-y-8">
	<div>
		<h1 class="text-2xl font-light text-[#cccccc] mb-1">Projects</h1>
		<p class="text-sm text-[#858585]">Manage your clients and their associated projects.</p>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<!-- Add Client Form -->
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5">
			<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Add Client</h2>
			<form onsubmit={addClient} class="space-y-4">
				<div>
					<label for="clientName" class="block text-xs text-[#858585] mb-1">Client Name</label>
					<input 
						id="clientName" 
						type="text" 
						bind:value={newClientName}
						class="w-full bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc]"
						required
					/>
				</div>
				<button type="submit" class="w-full bg-[#3c3c3c] hover:bg-[#4d4d4d] text-[#cccccc] rounded-lg text-sm py-2 transition-colors">
					Create Client
				</button>
			</form>
		</div>

		<!-- Add Project Form -->
		<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl p-5">
			<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Add Project</h2>
			<form onsubmit={addProject} class="space-y-4">
				<div>
					<label for="projectClient" class="block text-xs text-[#858585] mb-1">Select Client</label>
					<select 
						id="projectClient" 
						bind:value={newProjectClientId}
						class="w-full bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc]"
						required
					>
						<option value="" disabled>Select a client...</option>
						{#each $clients as client}
							<option value={client.id}>{client.name}</option>
						{/each}
					</select>
				</div>
				<div class="flex gap-4">
					<div class="flex-1">
						<label for="projectName" class="block text-xs text-[#858585] mb-1">Project Name</label>
						<input 
							id="projectName" 
							type="text" 
							bind:value={newProjectName}
							class="w-full bg-[#252526] border border-[#3c3c3c] rounded-lg text-[#cccccc] px-3 py-2 text-sm focus:outline-none focus:border-[#007acc]"
							required
						/>
					</div>
					<div class="w-12 shrink-0">
						<label for="projectColor" class="block text-xs text-[#858585] mb-1">Color</label>
						<input 
							id="projectColor" 
							type="color" 
							bind:value={newProjectColor}
							class="w-full h-9 p-0 border-0 bg-transparent cursor-pointer"
						/>
					</div>
				</div>
				<button type="submit" class="w-full bg-[#3c3c3c] hover:bg-[#4d4d4d] text-[#cccccc] rounded-lg text-sm py-2 transition-colors disabled:opacity-50" disabled={$clients.length === 0}>
					Create Project
				</button>
			</form>
		</div>
	</div>

	<!-- List -->
	<div class="mt-8">
		<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Directory</h2>
		{#if $clients.length === 0}
			<div class="text-center py-10 text-[#858585] border border-dashed border-[#2b2d31]">
				No clients yet. Create one above to get started.
			</div>
		{:else}
			<div class="space-y-4">
				{#each $clients as client}
					{#if getActiveClientProjects(client.id).length > 0 || getArchivedClientProjects(client.id).length === 0}
						<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-hidden">
							<div class="px-4 py-3 bg-[#252526] border-b border-[#2b2d31] flex justify-between items-center">
								<h3 class="font-medium text-[#cccccc]">{client.name}</h3>
								<button onclick={() => deleteClient(client.id)} class="text-xs text-[#858585] hover:text-[#f48771] tracking-wide transition-colors">Delete</button>
							</div>
							<ul class="divide-y divide-[#2b2d31]">
								{#each getActiveClientProjects(client.id) as project}
									{#if editingProjectId === project.id}
										<li class="p-3 px-4 bg-[#252526]">
											<div class="flex flex-col md:flex-row gap-3">
												<div class="flex-1">
													<label for="edit-client-{project.id}" class="block text-xs text-[#858585] mb-1">Client</label>
													<select id="edit-client-{project.id}" bind:value={editProjectClientId} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:outline-none focus:border-[#007acc]">
														{#each $clients as c}
															<option value={c.id}>{c.name}</option>
														{/each}
													</select>
												</div>
												<div class="flex-1">
													<label for="edit-name-{project.id}" class="block text-xs text-[#858585] mb-1">Project Name</label>
													<input id="edit-name-{project.id}" type="text" bind:value={editProjectName} class="bg-[#1e1e1e] border border-[#3c3c3c] text-[#cccccc] px-3 py-1.5 text-sm rounded-md w-full focus:outline-none focus:border-[#007acc]" />
												</div>
												<div class="w-16">
													<label for="edit-color-{project.id}" class="block text-xs text-[#858585] mb-1">Color</label>
													<input id="edit-color-{project.id}" type="color" bind:value={editProjectColor} class="w-full h-8 p-0 border-0 bg-transparent cursor-pointer" />
												</div>
											</div>
											<div class="flex justify-end gap-2 mt-3">
												<button onclick={cancelEditProject} class="px-3 py-1.5 text-sm text-[#cccccc] hover:bg-[#3c3c3c] rounded-md transition-colors">Cancel</button>
												<button onclick={saveEditProject} class="px-3 py-1.5 text-sm bg-[#007acc] hover:bg-[#005f9e] text-white rounded-md transition-colors">Save</button>
											</div>
										</li>
									{:else}
										<li class="flex items-center justify-between group p-3 px-4">
											<div class="flex items-center gap-3">
												<div class="w-3 h-3 rounded-full" style="background-color: {project.colorCode};"></div>
												<span class="text-sm text-[#cccccc]">{project.name}</span>
											</div>
											<div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-none">
												<button aria-label="Archive project" onclick={() => toggleArchiveProject(project.id)} class="text-[#858585] hover:text-[#cccccc] p-1" title="Archive">
													<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
														<path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
														<path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd" />
													</svg>
												</button>
												<button aria-label="Edit project" onclick={() => startEditProject(project)} class="text-[#858585] hover:text-[#cccccc] p-1" title="Edit">
													<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
														<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
													</svg>
												</button>
												<button aria-label="Delete project" onclick={() => deleteProject(project.id)} class="text-[#858585] hover:text-[#f48771] p-1" title="Delete">
													<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
														<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9z" clip-rule="evenodd" />
													</svg>
												</button>
											</div>
										</li>
									{/if}
								{:else}
									<li class="text-xs text-[#858585] p-3 px-4 italic">No active projects for this client.</li>
								{/each}
							</ul>
						</div>
					{/if}
				{/each}
			</div>
		{/if}
	</div>

	<!-- Archived Projects -->
	{#if $projects.some(p => p.isArchived)}
		<div class="mt-12">
			<h2 class="text-sm font-semibold uppercase tracking-wider text-[#cccccc] mb-4">Archived Projects</h2>
			<div class="space-y-4">
				{#each $clients as client}
					{#if getArchivedClientProjects(client.id).length > 0}
						<div class="bg-[#1e1e1e] border border-[#2b2d31] rounded-xl overflow-hidden opacity-75">
							<div class="px-4 py-3 bg-[#252526] border-b border-[#2b2d31] flex justify-between items-center">
								<h3 class="font-medium text-[#cccccc]">{client.name}</h3>
							</div>
							<ul class="divide-y divide-[#2b2d31]">
								{#each getArchivedClientProjects(client.id) as project}
									<li class="flex items-center justify-between group p-3 px-4">
										<div class="flex items-center gap-3">
											<div class="w-3 h-3 rounded-full grayscale" style="background-color: {project.colorCode};"></div>
											<span class="text-sm text-[#858585]">{project.name}</span>
										</div>
										<div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-none">
											<button aria-label="Unarchive project" onclick={() => toggleArchiveProject(project.id)} class="text-[#858585] hover:text-[#cccccc] p-1" title="Unarchive">
												<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
													<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
												</svg>
											</button>
											<button aria-label="Delete project" onclick={() => deleteProject(project.id)} class="text-[#858585] hover:text-[#f48771] p-1" title="Delete">
												<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
													<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9z" clip-rule="evenodd" />
												</svg>
											</button>
										</div>
									</li>
								{/each}
							</ul>
						</div>
					{/if}
				{/each}
			</div>
		</div>
	{/if}
</div>