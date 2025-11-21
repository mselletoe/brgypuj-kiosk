import api from './api'

// --- INVENTORY ---
export async function getInventory() {
  const response = await api.get('/equipment/inventory');
  return response.data;
}

export async function updateInventory(item) {
  const payload = {
    name: item.name,
    total: item.total,
    available: item.available,
    rate: item.rate
  };
  const response = await api.put(`/equipment/inventory/${item.id}`, payload);
  return response.data;
}

// --- REQUESTS ---
export async function getRequests(status = '') {
  const url = status ? `/equipment/requests?status=${status}` : '/equipment/requests';
  const response = await api.get(url);
  return response.data;
}

export async function createRequest(requestData) {
  const response = await api.post('/equipment/requests', requestData);
  return response.data;
}

// --- STATUS CHANGES ---
async function updateRequestStatus(requestId, action) {
  const response = await api.put(`/equipment/requests/${requestId}/${action}`);
  return response.data;
}

export const markAsPaid = (id) => updateRequestStatus(id, 'pay');
export const approveRequest = (id) => updateRequestStatus(id, 'approve');
export const rejectRequest = (id) => updateRequestStatus(id, 'reject');
export const markAsPickedUp = (id) => updateRequestStatus(id, 'pickup');
export const markAsReturned = (id) => updateRequestStatus(id, 'return');
export const issueRefund = (id) => updateRequestStatus(id, 'refund');