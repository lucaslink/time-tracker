import re

with open('src/routes/reports/+page.svelte', 'r') as f:
    content = f.read()

# 1. Update dateFilter type
old_dateFilter = "let dateFilter = $state<'all' | 'week' | 'month' | 'year' | 'custom'>('all');"
new_dateFilter = "let dateFilter = $state<'all' | 'week' | 'last_week' | 'month' | 'last_month' | 'year' | 'custom'>('all');"
content = content.replace(old_dateFilter, new_dateFilter)

# 2. Update $effect for dates
old_effect = """	$effect(() => {
		if (dateFilter === 'week') {
			customStartDate = new Date(startOfWeek).toISOString().split('T')[0];
			customEndDate = new Date(startOfWeek + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
		} else if (dateFilter === 'month') {
			customStartDate = new Date(startOfMonth).toISOString().split('T')[0];
			const endOfMonth = new Date(new Date(startOfMonth).getFullYear(), new Date(startOfMonth).getMonth() + 1, 0);
			customEndDate = endOfMonth.toISOString().split('T')[0];
		} else if (dateFilter === 'year') {
			customStartDate = new Date(startOfYear).toISOString().split('T')[0];
			const endOfYear = new Date(new Date(startOfYear).getFullYear(), 11, 31);
			customEndDate = endOfYear.toISOString().split('T')[0];
		}
	});"""
new_effect = """	$effect(() => {
		if (dateFilter === 'week') {
			customStartDate = new Date(startOfWeek).toISOString().split('T')[0];
			customEndDate = new Date(startOfWeek + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
		} else if (dateFilter === 'last_week') {
			const start = new Date(startOfWeek - 7 * 24 * 60 * 60 * 1000);
			customStartDate = start.toISOString().split('T')[0];
			customEndDate = new Date(startOfWeek - 1000).toISOString().split('T')[0];
		} else if (dateFilter === 'month') {
			customStartDate = new Date(startOfMonth).toISOString().split('T')[0];
			const endOfMonth = new Date(new Date(startOfMonth).getFullYear(), new Date(startOfMonth).getMonth() + 1, 0);
			customEndDate = endOfMonth.toISOString().split('T')[0];
		} else if (dateFilter === 'last_month') {
			const d = new Date(startOfMonth);
			d.setMonth(d.getMonth() - 1);
			customStartDate = d.toISOString().split('T')[0];
			const endOfMonth = new Date(d.getFullYear(), d.getMonth() + 1, 0);
			customEndDate = endOfMonth.toISOString().split('T')[0];
		} else if (dateFilter === 'year') {
			customStartDate = new Date(startOfYear).toISOString().split('T')[0];
			const endOfYear = new Date(new Date(startOfYear).getFullYear(), 11, 31);
			customEndDate = endOfYear.toISOString().split('T')[0];
		}
	});"""
content = content.replace(old_effect, new_effect)

# 3. Remove showDescription state
content = content.replace("	let showDescription = $state(true);", "")

# 4. Update retainerTarget
old_target = """		if (dateFilter === 'week') {
			return $globalSettings.retainerPeriod === 'weekly' ? hours : hours / 4;
		} else if (dateFilter === 'month') {
			return $globalSettings.retainerPeriod === 'monthly' ? hours : hours * 4;
		} else if (dateFilter === 'year') {
			return $globalSettings.retainerPeriod === 'monthly' ? hours * 12 : hours * 52;
		}"""
new_target = """		if (dateFilter === 'week' || dateFilter === 'last_week') {
			return $globalSettings.retainerPeriod === 'weekly' ? hours : hours / 4;
		} else if (dateFilter === 'month' || dateFilter === 'last_month') {
			return $globalSettings.retainerPeriod === 'monthly' ? hours : hours * 4;
		} else if (dateFilter === 'year') {
			return $globalSettings.retainerPeriod === 'monthly' ? hours * 12 : hours * 52;
		}"""
content = content.replace(old_target, new_target)

# 5. Update reportPeriodString
old_report = """		} else if (dateFilter === 'month') {"""
new_report = """		} else if (dateFilter === 'last_week') {
			const start = new Date(startOfWeek - 7 * 24 * 60 * 60 * 1000);
			const endStr = new Date(startOfWeek - 1000).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
			return `Last Week (${start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${endStr})`;
		} else if (dateFilter === 'month') {
			return `Month of ${new Date(startOfMonth).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}`;
		} else if (dateFilter === 'last_month') {
			const d = new Date(startOfMonth);
			d.setMonth(d.getMonth() - 1);
			return `Last Month (${d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })})`;"""
content = content.replace(old_report, new_report)

# 6. Update exportRows filter
old_export = """		if (dateFilter === 'week') filtered = filtered.filter(e => e.startTime >= startOfWeek);
		if (dateFilter === 'month') filtered = filtered.filter(e => e.startTime >= startOfMonth);"""
new_export = """		if (dateFilter === 'week') filtered = filtered.filter(e => e.startTime >= startOfWeek);
		if (dateFilter === 'last_week') {
			const start = startOfWeek - 7 * 24 * 60 * 60 * 1000;
			filtered = filtered.filter(e => e.startTime >= start && e.startTime < startOfWeek);
		}
		if (dateFilter === 'month') filtered = filtered.filter(e => e.startTime >= startOfMonth);
		if (dateFilter === 'last_month') {
			const d = new Date(startOfMonth);
			d.setMonth(d.getMonth() - 1);
			filtered = filtered.filter(e => e.startTime >= d.getTime() && e.startTime < startOfMonth);
		}"""
content = content.replace(old_export, new_export)

# 7. handleExportCSV change
old_export_call = """	function handleExportCSV() {
		exportToCSV(
			exportRows(), 
			groupBy === 'none', 
			groupBy !== 'project', 
			showDescription, 
			dateFilter,
			reportPeriodString(),
			totalExportHours()
		);
	}"""
new_export_call = """	function handleExportCSV() {
		exportToCSV(
			exportRows(), 
			groupBy === 'none', 
			groupBy !== 'project', 
			false, // No description
			dateFilter,
			reportPeriodString(),
			totalExportHours()
		);
	}"""
content = content.replace(old_export_call, new_export_call)

# 8. HTML Select Options
old_options = """							<option value="week">This Week</option>
							<option value="month">This Month</option>"""
new_options = """							<option value="week">This Week</option>
							<option value="last_week">Last Week</option>
							<option value="month">This Month</option>
							<option value="last_month">Last Month</option>"""
content = content.replace(old_options, new_options)


# 9. HTML Remove Checkbox
checkbox = """				<div class="flex items-center gap-2 self-end mb-1">
					<input type="checkbox" id="showDescription" bind:checked={showDescription} class="w-4 h-4 bg-[#252526] border border-[#3c3c3c] rounded text-[#007acc] focus:ring-[#007acc] focus:ring-offset-0 focus:ring-1 cursor-pointer appearance-none checked:bg-[#007acc] checked:border-[#007acc]" />
					<label for="showDescription" class="text-xs text-[#cccccc] cursor-pointer select-none">Show Description</label>
				</div>"""
content = content.replace(checkbox, "")

# 10. HTML Remove Description Headers
content = content.replace("""							{#if showDescription}
								<th class="p-3 text-xs font-semibold uppercase tracking-wider text-[#858585]">Description</th>
							{/if}""", "")

content = content.replace("""								{#if showDescription}
									<td class="p-3 text-xs text-[#858585] truncate max-w-[250px]" title={row.description}>{row.description || '-'}</td>
								{/if}""", "")

content = content.replace("""							{#if showDescription}
								<td></td>
							{/if}""", "")

with open('src/routes/reports/+page.svelte', 'w') as f:
    f.write(content)
