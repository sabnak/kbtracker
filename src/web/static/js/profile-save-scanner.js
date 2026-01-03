/**
 * Profile save file scanner
 * Handles save directory selection and campaign data extraction
 */
class ProfileSaveScanner {

	constructor(gameId) {
		this.gameId = gameId;
		this.saveDirectories = {};
		this.currentScanData = null;
	}

	/**
	 * Initialize the scanner
	 */
	async init() {
		await this.loadSaveDirectories();
		this.populateDropdown();
		this.attachScanHandler();
		this.initializeTooltips();
	}

	/**
	 * Initialize Bootstrap tooltips
	 */
	initializeTooltips() {
		const wrapper = document.getElementById('create-profile-wrapper');
		if (wrapper && typeof bootstrap !== 'undefined') {
			this.tooltip = new bootstrap.Tooltip(wrapper);
		}
	}

	/**
	 * Load available save directories from API
	 */
	async loadSaveDirectories() {
		try {
			const response = await fetch(`/api/games/${this.gameId}/save-directories`);
			if (!response.ok) {
				throw new Error('Failed to load save directories');
			}
			this.saveDirectories = await response.json();
		} catch (error) {
			console.error('Error loading saves:', error);
			this.showError('Failed to load save directories');
		}
	}

	/**
	 * Populate the save directory dropdown with optgroups
	 */
	populateDropdown() {
		const dropdown = document.getElementById('save-select');
		if (!dropdown) return;

		dropdown.innerHTML = '<option value="">-- Select a save file --</option>';

		for (const [gameName, saves] of Object.entries(this.saveDirectories)) {
			if (saves.length === 0) continue;

			const optgroup = document.createElement('optgroup');
			optgroup.label = gameName;

			saves.forEach(save => {
				const option = document.createElement('option');
				// Store full path: gameName/saveDir
				option.value = `${gameName}/${save.name}`;
				option.textContent = this.formatTimestamp(save.timestamp);
				option.dataset.gameName = gameName;
				option.dataset.saveDir = save.name;
				optgroup.appendChild(option);
			});

			dropdown.appendChild(optgroup);
		}

		// Enable scan button when selection changes
		dropdown.addEventListener('change', () => {
			const scanBtn = document.getElementById('scan-button');
			if (scanBtn) {
				scanBtn.disabled = !dropdown.value;
			}
		});
	}

	/**
	 * Attach click handler to scan button
	 */
	attachScanHandler() {
		const scanBtn = document.getElementById('scan-button');
		if (!scanBtn) return;

		scanBtn.addEventListener('click', async () => {
			await this.scanSelectedSave();
		});
	}

	/**
	 * Scan the selected save file
	 */
	async scanSelectedSave() {
		const dropdown = document.getElementById('save-select');
		const fullPath = dropdown.value;

		if (!fullPath) {
			this.showError('Please select a save file');
			return;
		}

		// Extract game name and save directory from full path
		const selectedOption = dropdown.options[dropdown.selectedIndex];
		const gameName = selectedOption.dataset.gameName;
		const saveDir = selectedOption.dataset.saveDir;

		this.showLoading(true);

		try {
			const response = await fetch(
				`/api/games/${this.gameId}/scan-save`,
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ save_dir: saveDir })
				}
			);

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Scan failed');
			}

			this.currentScanData = await response.json();
			this.displayScanResults(fullPath);
		} catch (error) {
			console.error('Scan error:', error);
			this.showError(error.message);
		} finally {
			this.showLoading(false);
		}
	}

	/**
	 * Display scan results and populate form fields
	 */
	displayScanResults(fullPath) {
		const resultsDiv = document.getElementById('scan-results');
		if (!resultsDiv) return;

		const data = this.currentScanData;

		resultsDiv.innerHTML = `
			<div class="alert alert-success">
				<h5>Campaign Data Extracted</h5>
				<ul class="mb-0">
					<li><strong>Hero:</strong> ${data.full_name}</li>
					<li><strong>Save Directory:</strong> ${fullPath}</li>
				</ul>
			</div>
		`;
		resultsDiv.style.display = 'block';

		// Auto-fill form fields with full path (e.g., "Darkside/1767476204")
		document.getElementById('name').value = data.full_name || '';
		document.getElementById('full-name').value = data.full_name || '';
		document.getElementById('save-dir').value = fullPath || '';

		// Enable profile creation button and remove tooltip
		const createBtn = document.getElementById('create-profile-button');
		const wrapper = document.getElementById('create-profile-wrapper');

		if (createBtn) {
			createBtn.disabled = false;
		}

		// Dispose tooltip and remove wrapper attributes when button is enabled
		if (this.tooltip) {
			this.tooltip.dispose();
			this.tooltip = null;
		}

		if (wrapper) {
			wrapper.removeAttribute('data-bs-toggle');
			wrapper.removeAttribute('data-bs-placement');
			wrapper.removeAttribute('title');
		}
	}

	/**
	 * Format Unix timestamp to readable date
	 */
	formatTimestamp(timestamp) {
		const date = new Date(timestamp * 1000);
		return date.toLocaleString();
	}

	/**
	 * Show loading indicator
	 */
	showLoading(show) {
		const scanBtn = document.getElementById('scan-button');
		if (scanBtn) {
			scanBtn.disabled = show;
			scanBtn.textContent = show ? 'Scanning...' : 'Scan Save File';
		}
	}

	/**
	 * Show error message
	 */
	showError(message) {
		const resultsDiv = document.getElementById('scan-results');
		if (resultsDiv) {
			resultsDiv.innerHTML = `
				<div class="alert alert-danger">
					${message}
				</div>
			`;
			resultsDiv.style.display = 'block';
		}
	}
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
	const gameIdElement = document.querySelector('[data-game-id]');
	if (gameIdElement) {
		const gameId = gameIdElement.dataset.gameId;
		const scanner = new ProfileSaveScanner(gameId);
		scanner.init();
	}
});
