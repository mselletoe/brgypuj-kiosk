import http from "./http";

export const getSystemConfig = async () => {
  try {
    const response = await http.get("/admin/settings");
    return response.data;
  } catch (error) {
    console.error("Error fetching system config:", error);
    return null;
  }
};

export const updateSystemConfig = async (fields = {}) => {
  const response = await http.patch("/admin/settings", fields);
  return response.data;
};

export const uploadBrgyLogo = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  await http.put("/admin/settings/logo", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getBrgyLogoUrl = async () => {
  try {
    const response = await http.get("/admin/settings/logo", { responseType: "blob" });
    return URL.createObjectURL(response.data);
  } catch (err) {
    if (err.response?.status === 404) return null;
    throw err;
  }
};

export const removeBrgyLogo = async () => {
  await http.delete("/admin/settings/logo");
};