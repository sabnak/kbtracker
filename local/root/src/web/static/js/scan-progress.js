document.addEventListener('DOMContentLoaded', function() {
	const scanForm = document.getElementById('scan-form');
	const scanFormContainer = document.getElementById('scan-form-container');
	const progressContainer = document.getElementById('scan-progress-container');
	const resultsContainer = document.getElementById('scan-results-container');
	const errorContainer = document.getElementById('scan-error-container');
	const statusMessage = document.getElementById('status-message');
	const progressList = document.getElementById('progress-list');
	const gameId = window.location.pathname.split('/')[2]; // Extract from /games/{id}/scan

	let eventSource = null;

	// Form submission handler
	scanForm.addEventListener('submit', function(e) {
		e.preventDefault();

		const language = document.getElementById('language').value;
		if (!language) {
			alert('Please select a language');
			return;
		}

		startScan(language);
	});

	// Retry/Scan Again handlers
	const scanAgainBtn = document.getElementById('scan-again-btn');
	const retryScanBtn = document.getElementById('retry-scan-btn');

	if (scanAgainBtn) {
		scanAgainBtn.addEventListener('click', resetForm);
	}

	if (retryScanBtn) {
		retryScanBtn.addEventListener('click', resetForm);
	}

	/**
	 * Start SSE-based scan
	 */
	function startScan(language) {
		// Hide form, show progress
		scanFormContainer.style.display = 'none';
		progressContainer.style.display = 'block';
		resultsContainer.style.display = 'none';
		errorContainer.style.display = 'none';

		// Reset progress UI
		resetProgressUI();

		// Create EventSource connection
		const url = `/games/${gameId}/scan/stream?language=${encodeURIComponent(language)}`;
		eventSource = new EventSource(url);

		// Handle incoming events
		eventSource.onmessage = function(event) {
			const data = JSON.parse(event.data);
			handleScanEvent(data);
		};

		// Handle connection errors
		eventSource.onerror = function(error) {
			console.error('SSE connection error:', error);
			eventSource.close();

			// Show error if we haven't already shown completion/error
			if (progressContainer.style.display !== 'none') {
				showError('Connection lost. The scan may have failed or completed.');
			}
		};
	}

	/**
	 * Handle individual scan event
	 */
	function handleScanEvent(event) {
		console.log('Scan event:', event);

		switch (event.event_type) {
			case 'scan_started':
				statusMessage.textContent = event.message;
				break;

			case 'extraction_started':
				updateResourceStatus('extraction', 'in_progress');
				statusMessage.textContent = event.message;
				break;

			case 'extraction_completed':
				updateResourceStatus('extraction', 'completed');
				statusMessage.textContent = event.message;
				break;

			case 'extraction_warning':
				console.warn('Extraction warning:', event.message);
				break;

			case 'resource_started':
				updateResourceStatus(event.resource_type, 'in_progress');
				statusMessage.textContent = event.message;
				break;

			case 'resource_completed':
				updateResourceStatus(event.resource_type, 'completed', event.count);
				statusMessage.textContent = event.message;
				break;

			case 'scan_completed':
				eventSource.close();
				showResults();
				break;

			case 'scan_error':
				eventSource.close();
				showError(event);
				break;
		}
	}

	/**
	 * Update status icon and count for a resource
	 */
	function updateResourceStatus(resourceType, status, count = null) {
		const item = progressList.querySelector(`[data-resource="${resourceType}"]`);
		if (!item) return;

		const icon = item.querySelector('.status-icon');
		const badge = item.querySelector('.count-badge');

		if (status === 'in_progress') {
			icon.textContent = '⏳';
			item.classList.add('list-group-item-warning');
		} else if (status === 'completed') {
			icon.textContent = '✅';
			item.classList.remove('list-group-item-warning');
			item.classList.add('list-group-item-success');

			if (count !== null) {
				badge.textContent = count;
				badge.style.display = 'inline-block';
				badge.classList.remove('bg-secondary');
				badge.classList.add('bg-success');
			}
		}
	}

	/**
	 * Show final results
	 */
	function showResults() {
		progressContainer.style.display = 'none';
		resultsContainer.style.display = 'block';

		// Collect counts from badges
		const counts = {
			items: parseInt(progressList.querySelector('[data-resource="items"] .count-badge')?.textContent || 0),
			sets: parseInt(progressList.querySelector('[data-resource="sets"] .count-badge')?.textContent || 0),
			units: parseInt(progressList.querySelector('[data-resource="units"] .count-badge')?.textContent || 0),
			spells: parseInt(progressList.querySelector('[data-resource="spells"] .count-badge')?.textContent || 0),
			atoms: parseInt(progressList.querySelector('[data-resource="atoms"] .count-badge')?.textContent || 0),
			actors: parseInt(progressList.querySelector('[data-resource="actors"] .count-badge')?.textContent || 0),
			localizations: parseInt(progressList.querySelector('[data-resource="localizations"] .count-badge')?.textContent || 0)
		};

		// Build summary
		const summary = `
			Items scanned: ${counts.items}<br>
			Sets scanned: ${counts.sets}<br>
			Units scanned: ${counts.units}<br>
			Spells scanned: ${counts.spells}<br>
			Atoms scanned: ${counts.atoms}<br>
			Actors scanned: ${counts.actors}<br>
			Localizations scanned: ${counts.localizations}
		`;

		document.getElementById('results-summary').innerHTML = summary;
	}

	/**
	 * Show error message
	 *
	 * :param errorData:
	 *     Error data object or string
	 */
	function showError(errorData) {
		progressContainer.style.display = 'none';
		errorContainer.style.display = 'block';

		const errorMessageEl = document.getElementById('error-message');
		const errorTypeBadge = document.getElementById('error-type-badge');
		const errorDetailsContainer = document.getElementById('error-details-container');
		const errorTracebackContent = document.getElementById('error-traceback-content');

		// Handle both string and object error data
		if (typeof errorData === 'string') {
			errorMessageEl.textContent = errorData;
			errorTypeBadge.style.display = 'none';
			errorDetailsContainer.style.display = 'none';
		} else {
			// Display main error message
			errorMessageEl.textContent = errorData.error || errorData.message || 'Unknown error occurred';

			// Display error type badge if available
			if (errorData.error_type) {
				errorTypeBadge.textContent = errorData.error_type;
				errorTypeBadge.style.display = 'inline-block';
			} else {
				errorTypeBadge.style.display = 'none';
			}

			// Display traceback if available
			if (errorData.error_traceback) {
				errorTracebackContent.textContent = errorData.error_traceback;
				errorDetailsContainer.style.display = 'block';
			} else {
				errorDetailsContainer.style.display = 'none';
			}
		}
	}

	/**
	 * Reset UI to initial state
	 */
	function resetForm() {
		scanFormContainer.style.display = 'block';
		progressContainer.style.display = 'none';
		resultsContainer.style.display = 'none';
		errorContainer.style.display = 'none';

		if (eventSource) {
			eventSource.close();
			eventSource = null;
		}
	}

	/**
	 * Reset progress UI to pending state
	 */
	function resetProgressUI() {
		const items = progressList.querySelectorAll('li');
		items.forEach(item => {
			const icon = item.querySelector('.status-icon');
			const badge = item.querySelector('.count-badge');

			icon.textContent = '⏸️';
			badge.style.display = 'none';
			badge.textContent = '0';

			item.classList.remove('list-group-item-warning', 'list-group-item-success');
			badge.classList.remove('bg-success');
			badge.classList.add('bg-secondary');
		});

		statusMessage.textContent = 'Initializing scan...';
	}
});
