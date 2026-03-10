// admin-dashboard/src/api/backupService.js
import http from "./http";

/**
 * Trigger a manual backup.
 * The server runs pg_dump and streams the .sql file back as a download.
 * @returns {Promise<Blob>} The raw blob to trigger a browser download.
 */
export const triggerManualBackup = async () => {
  const response = await http.post("/admin/backup", {}, { responseType: "blob" });
  return response;
};

/**
 * Fetch the list of saved backup files on the Pi.
 * @returns {Promise<Array>} Array of backup metadata objects.
 */
export const getBackupHistory = async () => {
  const response = await http.get("/admin/backup/history");
  return response.data;
};

/**
 * Download a specific saved backup file from the Pi.
 * @param {string} filename - The backup filename (e.g. backup_auto_20260310_020000.sql)
 * @returns {Promise<Blob>} The raw blob to trigger a browser download.
 */
export const downloadBackupFile = async (filename) => {
  const response = await http.get(
    `/admin/backup/download/${encodeURIComponent(filename)}`,
    { responseType: "blob" }
  );
  return response;
};

/**
 * Restore the database from an uploaded .sql file.
 * ⚠️ This overwrites all current data.
 * @param {File} file - A .sql backup file.
 */
export const restoreBackup = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await http.post("/admin/backup/restore", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};