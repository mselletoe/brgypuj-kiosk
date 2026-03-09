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
 */
export const updateSystemConfig = async (fields = {}) => {
  const response = await http.patch("/admin/settings", fields);
  return response.data;
};

/**
 * Upload or replace the barangay logo.
 * Stored as bytes in DB — no folder created on the server.
 * @param {File} file - PNG, JPEG, WebP, or SVG under 2 MB.
 */
export const uploadBrgyLogo = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  await http.put("/admin/settings/logo", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

/**
 * Fetches the barangay logo as a blob URL for use in <img> src.
 * Returns null if no logo has been uploaded yet (404).
 * @returns {Promise<string|null>} Object URL string or null.
 */
export const getBrgyLogoUrl = async () => {
  try {
    const response = await http.get("/admin/settings/logo", { responseType: "blob" });
    return URL.createObjectURL(response.data);
  } catch (err) {
    if (err.response?.status === 404) return null;
    throw err;
  }
};

/**
 * Removes the barangay logo.
 */
export const removeBrgyLogo = async () => {
  await http.delete("/admin/settings/logo");
};