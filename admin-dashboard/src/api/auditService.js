// admin-dashboard/src/api/auditService.js
import http from "./http";

export const getAuditLogs = async () => {
  try {
    const response = await http.get("/admin/audit-logs");
    return response.data;
  } catch (error) {
    console.error("Error fetching audit logs:", error);
    return []; // Return empty array if backend isn't ready yet so it doesn't crash
  }
};

// You can use this function later in your other views to create a log!
export const createAuditLog = async (action, details, entityType) => {
  return http.post("/admin/audit-logs", {
    action,
    details,
    entity_type: entityType,
  });
};
