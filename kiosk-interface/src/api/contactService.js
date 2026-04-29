import api from './http';

const getKioskContact = async () => {
  const res = await api.get('/kiosk/contact');
  return res.data;
};

export default {
  getKioskContact,
};