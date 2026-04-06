import http from "./http";

export const getAuditLogs = async () => {
  try {
    const response = await http.get("/admin/audit-logs");
    return response.data;
  } catch (error) {
    console.error("Error fetching audit logs:", error);
    return []; 
  }
};

export const createAuditLog = async (action, details, entityType) => {
  return http.post("/admin/audit-logs", {
    action,
    details,
    entity_type: entityType,
  });
};
