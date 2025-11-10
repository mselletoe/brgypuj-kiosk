// Set this to your backend's running URL
const API_URL = 'http://127.0.0.1:8000/equipment';

/**
 * Fetches the list of all available equipment from the inventory.
 */
export async function getInventory() {
  const response = await fetch(`${API_URL}/inventory`);
  if (!response.ok) throw new Error('Failed to fetch inventory');
  return response.json();
}

/**
 * Submits the complete borrowing request from the Kiosk.
 * @param {object} payload - The complete request object from ReviewRequest.vue
 */
export async function createKioskRequest(payload) {
  const response = await fetch(`${API_URL}/kiosk/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
     const err = await response.json();
     throw new Error(err.detail || 'Failed to create request');
  }
  return response.json();
}