import http from "./http";

export const triggerManualBackup = async () => {
  const response = await http.post("/admin/backup", {}, { responseType: "blob" });
  return response;
};

export const getBackupHistory = async () => {
  const response = await http.get("/admin/backup/history");
  return response.data;
};

export const downloadBackupFile = async (filename) => {
  const response = await http.get(
    `/admin/backup/download/${encodeURIComponent(filename)}`,
    { responseType: "blob" }
  );
  return response;
};

export const restoreBackup = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await http.post("/admin/backup/restore", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};