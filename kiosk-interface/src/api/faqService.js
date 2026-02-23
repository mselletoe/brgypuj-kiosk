import api from './http';

/**
 * Fetch FAQs for the kiosk
 * @returns {Promise<Array>} list of FAQs
 */
const getKioskFAQs = async () => {
  try {
    const response = await api.get('/faqs/kiosk');
    return response.data;
  } catch (err) {
    console.error('Failed to fetch FAQs:', err);
    throw err;
  }
};

export default {
  getKioskFAQs,
};