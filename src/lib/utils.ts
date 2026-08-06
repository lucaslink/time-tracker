import type { TimeEntry, Project, Client } from '$lib/store';

export function exportToCSV(timeEntries: TimeEntry[], projects: Project[], clients: Client[]) {
	// Map data for export
	const rows = timeEntries.map(entry => {
		const project = projects.find(p => p.id === entry.projectId);
		const client = project ? clients.find(c => c.id === project.clientId) : null;
		
		const projectName = project ? project.name : 'Unknown Project';
		const clientName = client ? client.name : 'Unknown Client';
		
		const startDate = new Date(entry.startTime).toLocaleDateString();
		const startTimeStr = new Date(entry.startTime).toLocaleTimeString();
		const endTimeStr = entry.endTime ? new Date(entry.endTime).toLocaleTimeString() : 'Running';
		
		const totalSeconds = Math.floor(entry.duration / 1000);
		const hours = (totalSeconds / 3600).toFixed(2);
		
		return [
			`"${clientName}"`,
			`"${projectName}"`,
			`"${entry.description || ''}"`,
			`"${startDate}"`,
			`"${startTimeStr}"`,
			`"${endTimeStr}"`,
			hours
		].join(',');
	});

	const header = ['Client', 'Project', 'Description', 'Date', 'Start Time', 'End Time', 'Duration (Hours)'].join(',');
	const csvContent = [header, ...rows].join('\n');

	// Create and trigger download
	const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.setAttribute('href', url);
	link.setAttribute('download', `time-tracker-export-${new Date().toISOString().split('T')[0]}.csv`);
	link.style.visibility = 'hidden';
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}
