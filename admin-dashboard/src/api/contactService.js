import api from './http';

const getContact = async () => {
  const res = await api.get('/admin/contact');
  return res.data;
};

const updateContact = async (payload) => {
  const res = await api.put('/admin/contact', payload);
  return res.data;
};

export default {
  getContact,
  updateContact,
};