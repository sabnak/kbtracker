class TrackedItemsManager {
	constructor(profileId, gameId) {
		this.profileId = profileId;
		this.gameId = gameId;
		this.shopsGrouped = [];
		this.itemsData = [];
		this.debounceTimers = {};
	}

	async init() {
		try {
			await this.loadShopsGrouped();
			await this.loadItems();
			this.render();
		} catch (error) {
			this.showError('Failed to load tracked items: ' + error.message);
		}
	}

	async loadShopsGrouped() {
		const response = await fetch(`/api/games/${this.gameId}/shops-grouped`);
		if (!response.ok) {
			throw new Error('Failed to load shops');
		}
		this.shopsGrouped = await response.json();
	}

	async loadItems() {
		const response = await fetch(`/api/profiles/${this.profileId}/tracked`);
		if (!response.ok) {
			throw new Error('Failed to load items');
		}
		this.itemsData = await response.json();
	}

	render() {
		const container = document.getElementById('items-container');

		if (this.itemsData.length === 0) {
			container.innerHTML = `
				<div class="alert alert-info">
					No items available. Import game data first.
				</div>
			`;
			return;
		}

		let html = '<div class="accordion" id="itemsAccordion">';

		this.itemsData.forEach((itemData, index) => {
			const item = itemData.item;
			const trackedShops = itemData.tracked_shops;
			const hasTracked = trackedShops.length > 0;

			html += `
				<div class="accordion-item mb-2">
					<h2 class="accordion-header">
						<button class="accordion-button ${hasTracked ? '' : 'collapsed'}"
								type="button"
								data-bs-toggle="collapse"
								data-bs-target="#item-${item.id}">
							<div class="w-100">
								<strong>${this.escapeHtml(item.name)}</strong>
								<span class="badge bg-primary ms-2">${item.price} gold</span>
								${hasTracked ? `<span class="badge bg-success ms-2">${trackedShops.length} shop${trackedShops.length !== 1 ? 's' : ''}</span>` : ''}
								${item.hint ? `<br><small class="text-muted">${this.escapeHtml(item.hint.substring(0, 100))}</small>` : ''}
							</div>
						</button>
					</h2>
					<div id="item-${item.id}"
						 class="accordion-collapse collapse ${hasTracked ? 'show' : ''}"
						 data-bs-parent="#itemsAccordion">
						<div class="accordion-body">
							${this.renderTrackedShops(item, trackedShops)}
							${this.renderAddShopButton(item)}
						</div>
					</div>
				</div>
			`;
		});

		html += '</div>';
		container.innerHTML = html;

		this.attachEventHandlers();
	}

	renderTrackedShops(item, trackedShops) {
		if (trackedShops.length === 0) {
			return '<p class="text-muted">No shops tracked yet.</p>';
		}

		let html = '<div class="list-group mb-3">';
		trackedShops.forEach(ts => {
			html += `
				<div class="list-group-item" data-item-id="${item.id}" data-shop-id="${ts.shop_id}">
					<div class="row align-items-center">
						<div class="col-md-4">
							<strong>${this.escapeHtml(ts.shop_name)}</strong>
							<br>
							<small class="text-muted">${this.escapeHtml(ts.location_name)}</small>
						</div>
						<div class="col-md-4">
							<label class="form-label mb-1">Quantity:</label>
							<input type="number"
								   class="form-control form-control-sm quantity-input"
								   value="${ts.count}"
								   min="0"
								   max="99999"
								   data-item-id="${item.id}"
								   data-shop-id="${ts.shop_id}">
						</div>
						<div class="col-md-4 text-end">
							<button class="btn btn-sm btn-danger delete-shop-btn"
									data-item-id="${item.id}"
									data-shop-id="${ts.shop_id}">
								Delete
							</button>
						</div>
					</div>
				</div>
			`;
		});
		html += '</div>';
		return html;
	}

	renderAddShopButton(item) {
		return `
			<button class="btn btn-sm btn-success add-shop-btn"
					data-item-id="${item.id}">
				+ Add Shop
			</button>
			<div class="add-shop-form mt-2 d-none" data-item-id="${item.id}">
				${this.renderShopDropdown(item)}
				<div class="row mt-2">
					<div class="col-md-6">
						<label class="form-label">Quantity:</label>
						<input type="number"
							   class="form-control form-control-sm new-shop-quantity"
							   value="1"
							   min="0"
							   max="99999">
					</div>
				</div>
				<div class="mt-2">
					<button class="btn btn-sm btn-primary save-new-shop-btn"
							data-item-id="${item.id}">
						Save
					</button>
					<button class="btn btn-sm btn-secondary cancel-add-shop-btn"
							data-item-id="${item.id}">
						Cancel
					</button>
				</div>
			</div>
		`;
	}

	renderShopDropdown(item) {
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

	attachEventHandlers() {
		document.querySelectorAll('.quantity-input').forEach(input => {
			input.addEventListener('input', (e) => {
				const itemId = e.target.dataset.itemId;
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

		document.querySelectorAll('.delete-shop-btn').forEach(btn => {
			btn.addEventListener('click', (e) => {
				const itemId = e.target.dataset.itemId;
				const shopId = e.target.dataset.shopId;
				this.deleteShop(itemId, shopId);
			});
		});

		document.querySelectorAll('.add-shop-btn').forEach(btn => {
			btn.addEventListener('click', (e) => {
				const itemId = e.target.dataset.itemId;
				const form = document.querySelector(`.add-shop-form[data-item-id="${itemId}"]`);
				form.classList.remove('d-none');
				e.target.classList.add('d-none');
			});
		});

		document.querySelectorAll('.cancel-add-shop-btn').forEach(btn => {
			btn.addEventListener('click', (e) => {
				const itemId = e.target.dataset.itemId;
				const form = document.querySelector(`.add-shop-form[data-item-id="${itemId}"]`);
				const addBtn = document.querySelector(`.add-shop-btn[data-item-id="${itemId}"]`);
				form.classList.add('d-none');
				addBtn.classList.remove('d-none');
			});
		});

		document.querySelectorAll('.save-new-shop-btn').forEach(btn => {
			btn.addEventListener('click', (e) => {
				const itemId = e.target.dataset.itemId;
				const form = document.querySelector(`.add-shop-form[data-item-id="${itemId}"]`);
				const shopId = form.querySelector('.new-shop-select').value;
				const count = parseInt(form.querySelector('.new-shop-quantity').value) || 1;

				if (!shopId) {
					alert('Please select a shop');
					return;
				}

				this.addShop(itemId, shopId, count);
			});
		});
	}

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
			await this.loadItems();
			this.render();
		}
	}

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
			await this.loadItems();
			this.render();
		} catch (error) {
			this.showError('Failed to remove shop: ' + error.message);
		}
	}

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
			await this.loadItems();
			this.render();
		} catch (error) {
			this.showError('Failed to add shop: ' + error.message);
		}
	}

	showError(message) {
		this.showToast(message, 'danger');
	}

	showSuccess(message) {
		this.showToast(message, 'success');
	}

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

	escapeHtml(text) {
		if (!text) return '';
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}
}

document.addEventListener('DOMContentLoaded', function() {
	const manager = new TrackedItemsManager(PROFILE_ID, GAME_ID);
	manager.init();
});
