import { reactive, watch } from "vue";

const storedUser = JSON.parse(localStorage.getItem("auth_user"));

export const auth = reactive({
  user: storedUser?.user || null,
  isGuest: storedUser?.isGuest || false,
});

// Persist changes to localStorage
watch(
  () => auth,
  (newVal) => {
    localStorage.setItem("auth_user", JSON.stringify(newVal));
  },
  { deep: true }
);

export const login = (userData) => {
  auth.user = userData;
  auth.isGuest = false;
};

export const continueAsGuest = () => {
  auth.user = null;
  auth.isGuest = true;
};

export const logout = () => {
  auth.user = null;
  auth.isGuest = false;
};