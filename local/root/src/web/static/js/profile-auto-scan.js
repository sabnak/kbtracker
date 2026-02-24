/**
 * Profile Auto-Scan Toggle Handler
 */
class ProfileAutoScanToggle {

	constructor() {
		this.initializeTooltips();
		this.attachEventListeners();
	}

	initializeTooltips() {
		const tooltipTriggerList = [].slice.call(
			document.querySelectorAll('[data-bs-toggle="tooltip"]')
		);
		tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
	}

	attachEventListeners() {
		document.querySelectorAll('.auto-scan-toggle').forEach(toggle => {
			toggle.addEventListener('change', (e) => this.handleToggleChange(e));
		});
	}

	async handleToggleChange(event) {
		const toggle = event.target;
		const profileId = toggle.dataset.profileId;
		const gameId = toggle.dataset.gameId;
		const isEnabled = toggle.checked;
		const originalState = !isEnabled;

		toggle.disabled = true;

		try {
			const response = await fetch(
				`/api/games/${gameId}/profiles/${profileId}/auto-scan?is_enabled=${isEnabled}`,
				{ method: 'PATCH' }
			);

			if (!response.ok) {
				throw new Error('Update failed');
			}

			this.updateTooltip(toggle, isEnabled);

		} catch (error) {
			toggle.checked = originalState;
			alert('Failed to update auto-scan setting');
		} finally {
			toggle.disabled = false;
		}
	}

	updateTooltip(toggle, isEnabled) {
		const tooltip = bootstrap.Tooltip.getInstance(toggle);
		const newTitle = isEnabled
			? 'Auto-scan enabled - Profile will be scanned automatically'
			: 'Auto-scan disabled - Click to enable';

		toggle.setAttribute('data-bs-original-title', newTitle);

		if (tooltip) {
			tooltip.setContent({ '.tooltip-inner': newTitle });
		}
	}
}


document.addEventListener('DOMContentLoaded', () => {
	new ProfileAutoScanToggle();
});
