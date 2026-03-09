// admin-dashboard/src/api/systemConfigService.js
import http from "./http";

/**
 * Fetch the full system config.
 * Called on mount by each settings tab.
 */
export const getSystemConfig = async () => {
  try {
    const response = await http.get("/admin/settings");
    return response.data;
  } catch (error) {
    console.error("Error fetching system config:", error);
    return null;
  }
};

/**
 * Partial update — pass only the fields you want to change.
 * Each tab calls this with its own subset of fields.
 *
 * @example
 * // General tab
 * await updateSystemConfig({ brgy_name: "Barangay San Jose", brgy_subname: "District 4" });
 *
 * // Security tab
 * await updateSystemConfig({ auto_logout_minutes: 30, max_failed_attempts: 5 });
 *
 * // Preferences tab
 * await updateSystemConfig({ maintenance_mode: true });
 */
export const updateSystemConfig = async (fields = {}) => {
  const response = await http.patch("/admin/settings", fields);
  return response.data;
};

/**
 * Upload a new barangay logo.
 * @param {File} file - The image file from an <input type="file">
 */
export const uploadBrgyLogo = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await http.post("/admin/settings/logo", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};