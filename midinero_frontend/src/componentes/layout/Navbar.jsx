import React, { useState, useEffect, useContext, useRef } from "react";
import { Link, NavLink as RouterNavLink, useNavigate } from "react-router-dom";
import { Bell, User, Settings, LogOut, Menu, X } from "lucide-react";
import { AuthContext } from "../../context/AuthContext";
import { useAuth } from "../../hooks/useAuth";
import { getNotifications } from "../../api/notificationService";

const Navbar = () => {
  const { user } = useContext(AuthContext);
  const { handleLogout } = useAuth();
  const navigate = useNavigate();

  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const userMenuRef = useRef(null);
  const notificationsRef = useRef(null);

  // 📌 Cargar notificaciones del backend
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const token = sessionStorage.getItem("access_token");
        if (!token) return;

        const data = await getNotifications(token);
        setNotifications(data);
        setUnreadCount(data.filter((n) => n.unread).length);
      } catch (error) {
        console.error("Error cargando notificaciones:", error);
        setNotifications([]);
        setUnreadCount(0);
      }
    };

    fetchNotifications();
  }, []);

  // 📌 Cerrar menús al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target)
      ) {
        setShowNotifications(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleUserMenu = () => {
    setShowUserMenu((prev) => !prev);
    setShowNotifications(false);
    setShowMobileMenu(false);
  };

  const toggleNotifications = () => {
    setShowNotifications((prev) => !prev);
    setShowUserMenu(false);
    setShowMobileMenu(false);
  };

  const toggleMobileMenu = () => {
    setShowMobileMenu((prev) => !prev);
    setShowUserMenu(false);
    setShowNotifications(false);
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between">

          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">M</span>
            </div>
            <span className="text-xl font-bold text-gray-800 hidden sm:block">
              MiDinero
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-1">
            <NavLink to="/dashboard" label="Dashboard" />
            <NavLink to="/transactions" label="Transacciones" />
            <NavLink to="/budgets" label="Presupuestos" />
            <NavLink to="/goals" label="Metas" />
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-2 sm:space-x-4">

            {/* Notifications */}
            <div className="relative" ref={notificationsRef}>
              <button
                onClick={toggleNotifications}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <Bell size={20} className="text-gray-600" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                )}
              </button>

              {/* DROPDOWN NOTIFICACIONES */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-lg shadow-xl border z-50 max-h-[80vh] overflow-hidden">

                  <div className="p-4 border-b bg-gray-50">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-800">Notificaciones</h3>
                      {unreadCount > 0 && (
                        <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                          {unreadCount} nueva{unreadCount !== 1 ? "s" : ""}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Lista */}
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center text-gray-500">
                        No hay notificaciones
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${
                            n.unread ? "bg-blue-50" : ""
                          }`}
                        >
                          <p className="text-sm text-gray-800">{n.message}</p>
                          <span className="text-xs text-gray-500">{n.time}</span>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="p-3 text-center border-t bg-gray-50">
                    <Link
                      to="/notifications"
                      className="text-sm text-blue-600 font-medium"
                      onClick={() => setShowNotifications(false)}
                    >
                      Ver todas las notificaciones
                    </Link>
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={toggleUserMenu}
                className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-lg"
              >
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User size={16} className="text-white" />
                </div>
                <span className="text-sm text-gray-700 hidden sm:block">
                  {user?.username}
                </span>
              </button>

              {/* DROPDOWN USUARIO */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white border rounded-lg shadow-xl z-50">

                  <div className="p-4 border-b bg-gray-50">
                    <p className="font-semibold text-gray-800">{user?.username}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>

                  <div className="py-2">
                    <MenuLink to="/profile" label="Mi Perfil" icon={<User size={16} />} />
                    <MenuLink to="/settings" label="Configuración" icon={<Settings size={16} />} />
                  </div>

                  {/* LOGOUT */}
                  <div className="border-t py-2">
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        handleLogout();
                        navigate("/login", { replace: true });
                      }}
                      className="flex items-center space-x-3 px-4 py-2 text-red-600 hover:bg-red-50 w-full"
                    >
                      <LogOut size={16} />
                      <span className="text-sm font-medium">Cerrar Sesión</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile Menu */}
            <button
              onClick={toggleMobileMenu}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              {showMobileMenu ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {showMobileMenu && (
          <div className="md:hidden mt-4 pb-4 border-t pt-4 space-y-1">
            <MobileNavLink to="/dashboard" label="Dashboard" onClick={toggleMobileMenu} />
            <MobileNavLink to="/transactions" label="Transacciones" onClick={toggleMobileMenu} />
            <MobileNavLink to="/budgets" label="Presupuestos" onClick={toggleMobileMenu} />
            <MobileNavLink to="/goals" label="Metas" onClick={toggleMobileMenu} />
          </div>
        )}
      </div>
    </nav>
  );
};

/* NAVLINKS */
const NavLink = ({ to, label }) => (
  <RouterNavLink
    to={to}
    className={({ isActive }) =>
      `px-3 py-2 text-sm rounded-lg ${
        isActive ? "text-blue-600 bg-blue-50" : "text-gray-600 hover:bg-blue-50"
      }`
    }
  >
    {label}
  </RouterNavLink>
);

const MobileNavLink = ({ to, label, onClick }) => (
  <RouterNavLink
    to={to}
    onClick={onClick}
    className={({ isActive }) =>
      `block px-4 py-3 text-base rounded-lg ${
        isActive ? "text-blue-600 bg-blue-50" : "text-gray-700 hover:bg-gray-50"
      }`
    }
  >
    {label}
  </RouterNavLink>
);

const MenuLink = ({ to, label, icon }) => (
  <Link to={to} className="flex items-center space-x-3 px-4 py-2 hover:bg-gray-50">
    <span>{icon}</span>
    <span>{label}</span>
  </Link>
);

export default Navbar;
