/**
 * Item tracking manager for hybrid table-based rendering
 *
 * Adapts TrackedItemsManager for integration into item_list.html
 * Supports profile selection and table-based tracking interface
 */
class ItemTrackingManager {

	constructor(gameId) {
		this.gameId = gameId;
		this.profileId = null;
		this.shopsGrouped = [];
		this.trackedItemsMap = {};
		this.debounceTimers = {};
		this.profiles = [];
	}

	/**
	 * Initialize the tracking manager
	 *
	 * :return:
	 */
	async init() {
		try {
			await this.loadProfiles();
			this.initProfileDropdown();
			this.attachProfileChangeHandler();
		} catch (error) {
			this.showError('Failed to initialize tracking: ' + error.message);
		}
	}

	/**
	 * Load all profiles for the current game
	 *
	 * :return:
	 */
	async loadProfiles() {
		const response = await fetch(`/api/games/${this.gameId}/profiles`);
		if (!response.ok) {
			throw new Error('Failed to load profiles');
		}
		this.profiles = await response.json();
	}

	/**
	 * Initialize the profile dropdown with options
	 *
	 * :return:
	 */
	initProfileDropdown() {
		const dropdown = document.getElementById('profile-select');
		if (!dropdown) {
			return;
		}

		dropdown.innerHTML = '<option value="">None (No Tracking)</option>';

		this.profiles.forEach(profile => {
			const option = document.createElement('option');
			option.value = profile.id;
			option.textContent = profile.name;
			dropdown.appendChild(option);
		});

		const savedProfileId = CookieManager.getProfileForGame(this.gameId);
		if (savedProfileId && this.profiles.some(p => p.id === parseInt(savedProfileId))) {
			dropdown.value = savedProfileId;
			this.enableTracking(parseInt(savedProfileId));
		}
	}

	/**
	 * Attach event handler for profile dropdown changes
	 *
	 * :return:
	 */
	attachProfileChangeHandler() {
		const dropdown = document.getElementById('profile-select');
		if (!dropdown) {
			return;
		}

		dropdown.addEventListener('change', async (e) => {
			const newProfileId = e.target.value;
			await this.onProfileChange(newProfileId);
		});
	}

	/**
	 * Handle profile selection change
	 *
	 * :param newProfileId:
	 *     The newly selected profile ID (empty string for "None")
	 * :return:
	 */
	async onProfileChange(newProfileId) {
		if (newProfileId === '') {
			this.disableTracking();
			CookieManager.setProfileForGame(this.gameId, null);
		} else {
			await this.enableTracking(parseInt(newProfileId));
			CookieManager.setProfileForGame(this.gameId, newProfileId);
		}
	}

	/**
	 * Enable tracking mode for a specific profile
	 *
	 * :param profileId:
	 *     The profile ID to enable tracking for
	 * :return:
	 */
	async enableTracking(profileId) {
		try {
			this.profileId = profileId;
			await this.loadShopsGrouped();
			await this.loadTrackedItems();
			this.showTrackingColumn();
			this.renderAllTrackingCells();
		} catch (error) {
			this.showError('Failed to enable tracking: ' + error.message);
		}
	}

	/**
	 * Disable tracking mode
	 *
	 * :return:
	 */
	disableTracking() {
		this.profileId = null;
		this.trackedItemsMap = {};
		this.hideTrackingColumn();
	}

	/**
	 * Load shops grouped by location
	 *
	 * :return:
	 */
	async loadShopsGrouped() {
		const response = await fetch(`/api/games/${this.gameId}/shops-grouped`);
		if (!response.ok) {
			throw new Error('Failed to load shops');
		}
		this.shopsGrouped = await response.json();
	}

	/**
	 * Load tracked items for the current profile
	 *
	 * :return:
	 */
	async loadTrackedItems() {
		const response = await fetch(`/api/profiles/${this.profileId}/tracked`);
		if (!response.ok) {
			throw new Error('Failed to load tracked items');
		}
		const data = await response.json();

		this.trackedItemsMap = {};
		data.forEach(itemData => {
			this.trackedItemsMap[itemData.item.id] = itemData.tracked_shops;
		});
	}

	/**
	 * Show the tracking column in the table
	 *
	 * :return:
	 */
	showTrackingColumn() {
		const header = document.getElementById('tracking-column-header');
		if (header) {
			header.classList.remove('d-none');
		}

		document.querySelectorAll('.tracking-cell').forEach(cell => {
			cell.classList.remove('d-none');
		});
	}

	/**
	 * Hide the tracking column in the table
	 *
	 * :return:
	 */
	hideTrackingColumn() {
		const header = document.getElementById('tracking-column-header');
		if (header) {
			header.classList.add('d-none');
		}

		document.querySelectorAll('.tracking-cell').forEach(cell => {
			cell.classList.add('d-none');
			cell.innerHTML = '';
		});
	}

	/**
	 * Render tracking UI for all items in the table
	 *
	 * :return:
	 */
	renderAllTrackingCells() {
		document.querySelectorAll('tr[data-item-id]').forEach(row => {
			const itemId = parseInt(row.dataset.itemId);
			const trackingCell = row.querySelector('.tracking-cell');
			if (trackingCell) {
				this.renderTrackingCell(trackingCell, itemId);
			}
		});
	}

	/**
	 * Render tracking UI for a single item
	 *
	 * :param cell:
	 *     The table cell element to render into
	 * :param itemId:
	 *     The item ID to render tracking for
	 * :return:
	 */
	renderTrackingCell(cell, itemId) {
		const trackedShops = this.trackedItemsMap[itemId] || [];

		let html = '';

		if (trackedShops.length > 0) {
			html += this.renderTrackedShopsList(itemId, trackedShops);
		}

		html += this.renderAddShopButton(itemId);

		cell.innerHTML = html;
		this.attachCellEventHandlers(cell, itemId);
	}

	/**
	 * Render the list of tracked shops for an item
	 *
	 * :param itemId:
	 *     The item ID
	 * :param trackedShops:
	 *     Array of tracked shop objects
	 * :return:
	 *     HTML string
	 */
	renderTrackedShopsList(itemId, trackedShops) {
		let html = '<div class="tracked-shops-list mb-2">';
		trackedShops.forEach(ts => {
			html += `
				<div class="tracked-shop-item d-flex mb-1">
					<div class="shop-name-row">
						<span class="shop-name text-truncate" title="${this.escapeHtml(ts.location_name)} / ${this.escapeHtml(ts.shop_name)}">
							${this.escapeHtml(ts.location_name)} / ${this.escapeHtml(ts.shop_name)}
						</span>
					</div>
					<div class="controls-row">
						<input type="number"
							   class="form-control form-control-sm quantity-input"
							   style="width: 60px;"
							   value="${ts.count}"
							   min="0"
							   max="99999"
							   data-item-id="${itemId}"
							   data-shop-id="${ts.shop_id}">
						<button class="btn btn-sm btn-outline-danger delete-shop-btn"
								data-item-id="${itemId}"
								data-shop-id="${ts.shop_id}"
								title="Remove shop">
							×
						</button>
					</div>
				</div>
			`;
		});
		html += '</div>';
		return html;
	}

	/**
	 * Render the add shop button and form
	 *
	 * :param itemId:
	 *     The item ID
	 * :return:
	 *     HTML string
	 */
	renderAddShopButton(itemId) {
		return `
			<button class="btn btn-sm btn-success add-shop-btn w-100"
					data-item-id="${itemId}">
				+ Add Shop
			</button>
			<div class="add-shop-form mt-2 d-none" data-item-id="${itemId}">
				${this.renderShopDropdown()}
				<div class="d-flex mt-1 gap-1">
					<input type="number"
						   class="form-control form-control-sm new-shop-quantity"
						   value="1"
						   min="0"
						   max="99999"
						   style="width: 60px;">
					<button class="btn btn-sm btn-primary save-new-shop-btn flex-grow-1"
							data-item-id="${itemId}">
						Save
					</button>
					<button class="btn btn-sm btn-secondary cancel-add-shop-btn"
							data-item-id="${itemId}">
						Cancel
					</button>
				</div>
			</div>
		`;
	}

	/**
	 * Render the shop dropdown grouped by location
	 *
	 * :return:
	 *     HTML string
	 */
	renderShopDropdown() {
		let html = '<select class="form-select form-select-sm new-shop-select">';
		html += '<option value="">-- Select Shop --</option>';

		this.shopsGrouped.forEach(group => {
			html += `<optgroup label="${this.escapeHtml(group.location.name)}">`;
			group.shops.forEach(shop => {
				html += `<option value="${shop.id}">${this.escapeHtml(shop.name)}</option>`;
			});
			html += '</optgroup>';
		});

		html += '</select>';
		return html;
	}

	/**
	 * Attach event handlers for a tracking cell
	 *
	 * :param cell:
	 *     The table cell element
	 * :param itemId:
	 *     The item ID
	 * :return:
	 */
	attachCellEventHandlers(cell, itemId) {
		cell.querySelectorAll('.quantity-input').forEach(input => {
			input.addEventListener('input', (e) => {
				const shopId = e.target.dataset.shopId;
				const newCount = parseInt(e.target.value) || 0;

				const key = `${itemId}-${shopId}`;
				if (this.debounceTimers[key]) {
					clearTimeout(this.debounceTimers[key]);
				}

				this.debounceTimers[key] = setTimeout(() => {
					this.updateQuantity(itemId, shopId, newCount);
				}, 500);
			});
		});

		cell.querySelectorAll('.delete-shop-btn').forEach(btn => {
			btn.addEventListener('click', (e) => {
				const shopId = e.target.dataset.shopId;
				this.deleteShop(itemId, shopId);
			});
		});

		const addBtn = cell.querySelector('.add-shop-btn');
		if (addBtn) {
			addBtn.addEventListener('click', (e) => {
				const form = cell.querySelector('.add-shop-form');
				form.classList.remove('d-none');
				e.target.classList.add('d-none');
			});
		}

		const cancelBtn = cell.querySelector('.cancel-add-shop-btn');
		if (cancelBtn) {
			cancelBtn.addEventListener('click', (e) => {
				const form = cell.querySelector('.add-shop-form');
				const addBtn = cell.querySelector('.add-shop-btn');
				form.classList.add('d-none');
				addBtn.classList.remove('d-none');
			});
		}

		const saveBtn = cell.querySelector('.save-new-shop-btn');
		if (saveBtn) {
			saveBtn.addEventListener('click', (e) => {
				const form = cell.querySelector('.add-shop-form');
				const shopId = form.querySelector('.new-shop-select').value;
				const count = parseInt(form.querySelector('.new-shop-quantity').value) || 1;

				if (!shopId) {
					alert('Please select a shop');
					return;
				}

				this.addShop(itemId, shopId, count);
			});
		}
	}

	/**
	 * Update the quantity for an item-shop tracking
	 *
	 * :param itemId:
	 *     The item ID
	 * :param shopId:
	 *     The shop ID
	 * :param count:
	 *     The new quantity
	 * :return:
	 */
	async updateQuantity(itemId, shopId, count) {
		try {
			const response = await fetch(
				`/api/profiles/${this.profileId}/items/${itemId}/shops/${shopId}`,
				{
					method: 'PATCH',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ count: count })
				}
			);

			if (!response.ok) {
				throw new Error('Failed to update quantity');
			}

			this.showSuccess('Quantity updated');
		} catch (error) {
			this.showError('Failed to update quantity: ' + error.message);
			await this.refreshItemTracking(itemId);
		}
	}

	/**
	 * Delete a shop from item tracking
	 *
	 * :param itemId:
	 *     The item ID
	 * :param shopId:
	 *     The shop ID
	 * :return:
	 */
	async deleteShop(itemId, shopId) {
		if (!confirm('Remove this shop from tracking?')) {
			return;
		}

		try {
			const response = await fetch(
				`/api/profiles/${this.profileId}/items/${itemId}/shops/${shopId}`,
				{
					method: 'DELETE'
				}
			);

			if (!response.ok) {
				throw new Error('Failed to delete shop');
			}

			this.showSuccess('Shop removed');
			await this.refreshItemTracking(itemId);
		} catch (error) {
			this.showError('Failed to remove shop: ' + error.message);
		}
	}

	/**
	 * Add a shop to item tracking
	 *
	 * :param itemId:
	 *     The item ID
	 * :param shopId:
	 *     The shop ID
	 * :param count:
	 *     The initial quantity
	 * :return:
	 */
	async addShop(itemId, shopId, count) {
		try {
			const response = await fetch(
				`/api/profiles/${this.profileId}/items/${itemId}/shops`,
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						shop_id: parseInt(shopId),
						count: count
					})
				}
			);

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Failed to add shop');
			}

			this.showSuccess('Shop added');
			await this.refreshItemTracking(itemId);
		} catch (error) {
			this.showError('Failed to add shop: ' + error.message);
		}
	}

	/**
	 * Refresh tracking data for a specific item and re-render its cell
	 *
	 * :param itemId:
	 *     The item ID to refresh
	 * :return:
	 */
	async refreshItemTracking(itemId) {
		await this.loadTrackedItems();
		const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
		if (row) {
			const cell = row.querySelector('.tracking-cell');
			if (cell) {
				this.renderTrackingCell(cell, itemId);
			}
		}
	}

	/**
	 * Show error message
	 *
	 * :param message:
	 *     Error message to display
	 * :return:
	 */
	showError(message) {
		this.showToast(message, 'danger');
	}

	/**
	 * Show success message
	 *
	 * :param message:
	 *     Success message to display
	 * :return:
	 */
	showSuccess(message) {
		this.showToast(message, 'success');
	}

	/**
	 * Show toast notification
	 *
	 * :param message:
	 *     Message to display
	 * :param type:
	 *     Bootstrap color type (success, danger, etc.)
	 * :return:
	 */
	showToast(message, type) {
		const toastContainer = this.getOrCreateToastContainer();

		const toastId = 'toast-' + Date.now();
		const toastHtml = `
			<div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
				<div class="d-flex">
					<div class="toast-body">${this.escapeHtml(message)}</div>
					<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
				</div>
			</div>
		`;

		toastContainer.insertAdjacentHTML('beforeend', toastHtml);

		const toastElement = document.getElementById(toastId);
		const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
		toast.show();

		toastElement.addEventListener('hidden.bs.toast', () => {
			toastElement.remove();
		});
	}

	/**
	 * Get or create the toast container element
	 *
	 * :return:
	 *     The toast container element
	 */
	getOrCreateToastContainer() {
		let container = document.getElementById('toast-container');
		if (!container) {
			container = document.createElement('div');
			container.id = 'toast-container';
			container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
			container.style.zIndex = '1050';
			document.body.appendChild(container);
		}
		return container;
	}

	/**
	 * Escape HTML to prevent XSS
	 *
	 * :param text:
	 *     Text to escape
	 * :return:
	 *     Escaped HTML string
	 */
	escapeHtml(text) {
		if (!text) return '';
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}
}


document.addEventListener('DOMContentLoaded', function() {
	const gameIdElement = document.querySelector('[data-game-id]');
	if (gameIdElement) {
		const gameId = parseInt(gameIdElement.dataset.gameId);
		const manager = new ItemTrackingManager(gameId);
		manager.init();
	}
});
