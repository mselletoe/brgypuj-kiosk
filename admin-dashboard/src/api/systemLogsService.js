// admin-dashboard/src/api/systemLogService.js
import http from "./http";

export const getSystemLogs = async (params = {}) => {
  try {
    const response = await http.get("/admin/system-logs", { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching system logs:", error);
    return { total: 0, page: 1, page_size: 20, results: [] };
  }
};

export const getSystemLogDetail = async (logId) => {
  try {
    const response = await http.get(`/admin/system-logs/${logId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching system log detail:", error);
    return null;
  }
};

export const getSystemLogSummary = async () => {
  try {
    const response = await http.get("/admin/system-logs/summary/counts");
    return response.data;
  } catch (error) {
    console.error("Error fetching system log summary:", error);
    return { counts: { info: 0, warning: 0, error: 0, critical: 0 }, total_today: 0 };
  }
};