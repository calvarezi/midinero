import axios from "axios";

// Crear una instancia de axios con configuración global
const api = axios.create({
  baseURL: "http://localhost:8000/", // Podrías extraer esto a una variable de entorno
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let failedQueue = [];

// Función que procesa la cola de solicitudes que esperan el nuevo token
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = []; // Limpiar la cola después de procesarla
};

// Interceptor de solicitud para agregar el token de acceso al encabezado
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem("access_token"); // Obtener el token de acceso del sessionStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`; // Incluir el token en la cabecera
    }
    return config; // Devolver la configuración de la solicitud
  },
  (error) => {
    return Promise.reject(error); // Rechazar la solicitud si ocurre un error
  }
);

// Interceptor de respuesta para manejar errores y refrescar el token cuando sea necesario
api.interceptors.response.use(
  (response) => response, // Si la respuesta es exitosa, devolverla
  async (error) => {
    const originalRequest = error.config;

    // Si la respuesta es 401 (no autorizado), se trata de refrescar el token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya estamos refrescando el token, encolamos la solicitud
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest); // Reintentar la solicitud original con el nuevo token
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true; // Marcamos la solicitud como reintentada
      isRefreshing = true;

      const refreshToken = sessionStorage.getItem("refresh_token"); // Obtener el refresh token
      if (!refreshToken) {
        // Si no hay refresh token, redirigimos al login
        sessionStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        // Intentamos obtener un nuevo token de acceso usando el refresh token
        const response = await axios.post("http://localhost:8000/api/auth/refresh/", {
          refresh: refreshToken,
        });

        const { access } = response.data; // Extraemos el nuevo token de acceso
        sessionStorage.setItem("access_token", access); // Guardamos el nuevo token de acceso

        // Actualizamos el encabezado de Authorization en las futuras solicitudes
        api.defaults.headers.common["Authorization"] = `Bearer ${access}`;
        originalRequest.headers.Authorization = `Bearer ${access}`;

        processQueue(null, access); // Procesamos la cola de solicitudes en espera
        isRefreshing = false;

        return api(originalRequest); // Reintentamos la solicitud original
      } catch (refreshError) {
        // Si el refresh token también falla, limpiamos la sesión y redirigimos al login
        processQueue(refreshError, null);
        isRefreshing = false;
        
        sessionStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error); // Rechazamos cualquier otro error
  }
);

export default api;