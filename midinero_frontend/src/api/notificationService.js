import api from "./axiosConfig"; // tu instancia de axios configurada

export const getNotifications = async (token) => {
  const response = await api.get("/api/finances/notifications/", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  // Extraemos el array correcto
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};