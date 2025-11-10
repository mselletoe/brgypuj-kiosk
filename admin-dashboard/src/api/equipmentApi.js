// Set this to your backend's running URL
const API_URL = 'http://127.0.0.1:8000/equipment';

// --- INVENTORY ---

export async function getInventory() {
  const response = await fetch(`${API_URL}/inventory`);
  if (!response.ok) throw new Error('Failed to fetch inventory');
  return response.json();
}

export async function updateInventory(item) {
  // The 'item' from the frontend has different names, so we map them
  const payload = {
    name: item.name,
    total: item.total,
    available: item.available,
    rate: item.rate
  };
  
  const response = await fetch(`${API_URL}/inventory/${item.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to update item');
  return response.json();
}

// --- REQUESTS ---

export async function getRequests(status = '') {
  const url = status ? `${API_URL}/requests?status=${status}` : `${API_URL}/requests`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch requests');
  return response.json();
}

export async function createRequest(requestData) {
  // The 'requestData' from the form matches the Pydantic schema
  const response = await fetch(`${API_URL}/requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
  if (!response.ok) {
     const err = await response.json();
     throw new Error(err.detail || 'Failed to create request');
  }
  return response.json();
}

// --- STATUS CHANGES ---

// Generic helper function
async function updateRequestStatus(requestId, action) {
  const response = await fetch(`${API_URL}/requests/${requestId}/${action}`, {
    method: 'PUT',
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || `Failed to ${action}`);
  }
  return response.json();
}

export function markAsPaid(requestId) {
  return updateRequestStatus(requestId, 'pay');
}

export function approveRequest(requestId) {
  return updateRequestStatus(requestId, 'approve');
}

export function rejectRequest(requestId) {
  return updateRequestStatus(requestId, 'reject');
}

export function markAsPickedUp(requestId) {
  return updateRequestStatus(requestId, 'pickup');
}

export function markAsReturned(requestId) {
  return updateRequestStatus(requestId, 'return');
}

export function issueRefund(requestId) {
  return updateRequestStatus(requestId, 'refund');
}