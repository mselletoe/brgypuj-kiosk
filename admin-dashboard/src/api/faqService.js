import api from './http';

// Kiosk
const getKioskFAQs = async () => {
  const res = await api.get('/admin/faqs/kiosk');
  return res.data;
};

// Admin
const getAllFAQs = async () => {
  const res = await api.get('/admin/faqs/admin');
  return res.data;
};

const createFAQ = async (payload) => {
  const res = await api.post('/admin/faqs', payload);
  return res.data;
};

const updateFAQ = async (id, payload) => {
  const res = await api.put(`/admin/faqs/${id}`, payload);
  return res.data;
};

const deleteFAQ = async (id) => {
  await api.delete(`/admin/faqs/${id}`);
};

const bulkDeleteFAQs = async (ids) => {
  const res = await api.post(`/admin/faqs/bulk-delete`, ids);
  return res.data;
};

export default {
  getKioskFAQs,
  getAllFAQs,
  createFAQ,
  updateFAQ,
  deleteFAQ,
  bulkDeleteFAQs,
};