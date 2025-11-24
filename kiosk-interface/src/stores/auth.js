import { reactive, watch } from "vue";

const storedUser = JSON.parse(localStorage.getItem("auth_user"));

export const auth = reactive({
  user: storedUser?.user || null,
  isGuest: storedUser?.isGuest || false,
  token: storedUser?.token || null,           // NEW: JWT token
  loginMethod: storedUser?.loginMethod || null // NEW: Track login method
});

// Persist changes to localStorage
watch(
  () => auth,
  (newVal) => {
    localStorage.setItem("auth_user", JSON.stringify(newVal));
  },
  { deep: true }
);

/**
 * Login with user data and token (from backend response)
 * @param {Object} userData - User info from backend
 * @param {string} token - JWT access token
 */
export const login = (userData, token = null) => {
  auth.user = userData;
  auth.token = token;
  auth.isGuest = userData.is_guest || false;
  auth.loginMethod = userData.login_method || 'rfid';
};

/**
 * Continue as guest (legacy support)
 * NOTE: Now calls backend to get a proper guest token
 */
export const continueAsGuest = () => {
  auth.user = { name: "Guest User", is_guest: true };
  auth.isGuest = true;
  auth.token = null; // Will be set by Login.vue after API call
  auth.loginMethod = 'guest';
};

/**
 * Logout - clear all auth data
 */
export const logout = () => {
  auth.user = null;
  auth.isGuest = false;
  auth.token = null;
  auth.loginMethod = null;
  localStorage.removeItem("auth_user");
};

// ==============================================================================
// NEW HELPER FUNCTIONS
// ==============================================================================

/**
 * Restore authentication from localStorage on app load
 * Call this in main.js
 */
export const restoreAuth = () => {
  const stored = localStorage.getItem('auth_user');
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      auth.user = parsed.user;
      auth.token = parsed.token;
      auth.isGuest = parsed.isGuest || false;
      auth.loginMethod = parsed.loginMethod || null;
    } catch (e) {
      console.error('Failed to restore auth:', e);
      logout();
    }
  }
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = () => {
  return !!auth.token;
};

/**
 * Check if user logged in via RFID (registered resident)
 */
export const isRfidUser = () => {
  return auth.loginMethod === 'rfid' && !auth.isGuest && auth.user?.resident_id;
};

/**
 * Get resident ID (null for guests)
 */
export const getResidentId = () => {
  return auth.user?.resident_id || null;
};

/**
 * Check if user is admin
 */
export const isAdmin = () => {
  return auth.user?.is_admin === true || auth.loginMethod === 'admin';
};

/**
 * Get user's full name
 */
export const getUserName = () => {
  return auth.user?.name || 'Guest';
};