import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() =>
    !!sessionStorage.getItem("access_token")
  );

  const [user, setUser] = useState(() => {
    const stored = sessionStorage.getItem("user");
    try {
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const navigate = useNavigate();

  const login = (access, refresh, userData) => {
    sessionStorage.setItem("access_token", access);
    sessionStorage.setItem("refresh_token", refresh);

    if (userData) {
      sessionStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);
    }

    setIsAuthenticated(true);
    navigate("/dashboard", { replace: true });
  };

  const logout = () => {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    sessionStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
    navigate("/login", { replace: true });
  };

  const checkAuth = () => {
    if (!sessionStorage.getItem("access_token")) {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
