import api from './api.js'; // Import the axios instance

/**
 * Fetches the list of all available equipment from the inventory.
 */
export async function getInventory() {
  const response = await api.get('/equipment/inventory');
  return response.data;
}

/**
 * Submits the complete borrowing request from the Kiosk.
 * @param {object} payload - The complete request object from ReviewRequest.vue
 */
export async function createKioskRequest(payload) {
  const response = await api.post('/equipment/kiosk/request', payload);
  return response.data;
}