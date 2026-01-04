/**
 * Profile save file scanner for shop inventories
 */
class ProfileScanner {

	constructor() {
		this.attachHandlers();
	}

	attachHandlers() {
		document.addEventListener('click', (e) => {
			if (e.target.classList.contains('scan-profile-btn')) {
				this.handleScanClick(e.target);
			}
		});
	}

	async handleScanClick(button) {
		const profileId = button.dataset.profileId;
		const gameId = button.dataset.gameId;

		const originalText = button.textContent;
		button.disabled = true;
		button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Scanning...';

		try {
			const response = await fetch(
				`/api/games/${gameId}/profiles/${profileId}/scan`,
				{ method: 'POST' }
			);

			if (!response.ok) {
				const errorData = await response.json();
				const detail = errorData.detail;

				this.showError({
					message: (typeof detail === 'object' ? detail.error : detail) || 'Scan failed',
					error_type: typeof detail === 'object' ? detail.error_type : null,
					error_traceback: typeof detail === 'object' ? detail.error_traceback : null,
					status: response.status,
					profileId: profileId
				});
				return;
			}

			const counts = await response.json();
			this.showSuccess(counts);
		} catch (error) {
			this.showError({
				message: error.message,
				error: error
			});
		} finally {
			button.disabled = false;
			button.textContent = originalText;
		}
	}

	showSuccess(counts) {
		const successContainer = document.getElementById('scan-success-container');
		const errorContainer = document.getElementById('scan-error-container');
		const messageEl = document.getElementById('success-message');

		if (!successContainer || !messageEl) return;

		if (errorContainer) {
			errorContainer.style.display = 'none';
		}

		const message = `
			Successfully scanned save file:
			${counts.items} items,
			${counts.spells} spells,
			${counts.units} units,
			${counts.garrison} garrison units added.
		`;

		messageEl.textContent = message;
		successContainer.style.display = 'block';

		setTimeout(() => {
			if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
				const bsAlert = new bootstrap.Alert(successContainer);
				bsAlert.close();
			}
		}, 5000);
	}

	showError(errorData) {
		const errorContainer = document.getElementById('scan-error-container');
		const successContainer = document.getElementById('scan-success-container');
		const errorMessageEl = document.getElementById('error-message');
		const errorDetailsContainer = document.getElementById('error-details-container');
		const errorDetailsContent = document.getElementById('error-details-content');

		if (!errorContainer || !errorMessageEl) return;

		if (successContainer) {
			successContainer.style.display = 'none';
		}

		if (typeof errorData === 'string') {
			errorMessageEl.textContent = errorData;
			errorDetailsContainer.style.display = 'none';
		} else {
			errorMessageEl.textContent = errorData.message || 'Unknown error occurred';

			const details = [];

			if (errorData.error_type) {
				details.push(`Error Type: ${errorData.error_type}`);
			}

			if (errorData.status) {
				details.push(`HTTP Status: ${errorData.status}`);
			}

			if (errorData.profileId) {
				details.push(`Profile ID: ${errorData.profileId}`);
			}

			details.push(`Timestamp: ${new Date().toISOString()}`);

			if (errorData.error_traceback) {
				details.push(`\nPython Traceback:\n${errorData.error_traceback}`);
			} else if (errorData.error && errorData.error.stack) {
				details.push(`\nJavaScript Stack:\n${errorData.error.stack}`);
			}

			if (details.length > 0) {
				errorDetailsContent.textContent = details.join('\n');
				errorDetailsContainer.style.display = 'block';
			} else {
				errorDetailsContainer.style.display = 'none';
			}
		}

		errorContainer.style.display = 'block';

		console.error('[ProfileScanner] Scan failed:', errorData);
	}
}

document.addEventListener('DOMContentLoaded', () => {
	new ProfileScanner();
});
