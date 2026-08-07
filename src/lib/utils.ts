export type ExportRow = {
	date: string;
	clientName: string;
	projectName: string;
	projectColor: string;
	timeStr: string;
	durationStr: string;
	description: string;
	rawStartTime: number;
	rawDurationMs: number;
};

export function exportToCSV(rows: ExportRow[], showTime: boolean, showDate: boolean = true, showDescription: boolean = true, dateFilter: string = 'all', reportPeriodString: string = '', totalExportHours: string = '') {
	// Map data for export
	const csvRows = rows.map(row => {
		const cols = [
			`"${row.clientName}"`,
			`"${row.projectName}"`
		];
		
		if (showDescription) {
			cols.push(`"${row.description.replace(/"/g, '""')}"`); // Escape quotes
		}
		
		if (showDate) {
			cols.push(`"${row.date}"`);
		}
		
		if (showTime) {
			let start = '';
			let end = '';
			if (row.timeStr !== 'N/A' && row.timeStr.includes(' - ')) {
				const parts = row.timeStr.split(' - ');
				start = parts[0];
				end = parts[1];
			}
			cols.push(`"${start}"`, `"${end}"`);
		}
		
		// Add decimal hours duration
		const totalSeconds = Math.floor(row.rawDurationMs / 1000);
		const hours = (totalSeconds / 3600).toFixed(2);
		cols.push(hours);
		
		return cols.join(',');
	});

	const headerCols = ['Client', 'Project'];
	if (showDescription) {
		headerCols.push('Description');
	}
	if (showDate) {
		headerCols.push('Date');
	}
	if (showTime) {
		headerCols.push('Start Time', 'End Time');
	}
	headerCols.push('Duration (Hours)');
	
	let csvContent = [headerCols.join(','), ...csvRows].join('\n');
	
	// Add footer row
	if (reportPeriodString && totalExportHours) {
		const emptyColsCount = headerCols.length - 1;
		const footerCols = [`"Total Hours for ${reportPeriodString}:"`];
		for(let i = 1; i < emptyColsCount; i++) {
			footerCols.push('""');
		}
		footerCols.push(`"${totalExportHours}"`);
		csvContent += '\n' + footerCols.join(',');
	}

	// Create and trigger download
	const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.setAttribute('href', url);
	
	const dateStr = new Date().toISOString().split('T')[0];
	link.setAttribute('download', `time-tracker-${dateFilter}-export-${dateStr}.csv`);
	link.style.visibility = 'hidden';
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}
