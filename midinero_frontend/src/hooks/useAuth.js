import { useState, useContext } from "react";
import {
  register as registerService,
  login as loginService,
} from "../api/authService";
import { AuthContext } from "../context/AuthContext";

export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const { logout: contextLogout } = useContext(AuthContext);

  const handleRegister = async (userData) => {
    setLoading(true);
    setError("");
    setFieldErrors({});

    try {
      const result = await registerService(userData);

      if (!result.success) {
        setError(result.errors.message || "Error de validación");
        setFieldErrors(result.errors.errors || {});
        return { success: false };
      }

      return { success: true, data: result.data };
    } catch (err) {
      setError(err.detail || "Error al registrar usuario");
      return { success: false };
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (username, password) => {
    setLoading(true);
    setError("");

    try {
      const result = await loginService(username, password);
      setError("");
      return result;
    } catch (err) {
      setError(err.detail || "Error al iniciar sesión");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    contextLogout(); // usa el contexto correctamente
  };

  return {
    loading,
    error,
    fieldErrors,
    handleRegister,
    handleLogin,
    handleLogout,
  };
};
