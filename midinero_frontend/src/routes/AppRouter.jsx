import { Routes, Route, Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import ProtectedRoute from "../componentes/ProtectedRoute";
import DashboardLayout from "../componentes/layout/DashboardLayout";
import LoginPage from "../pages/Auth/LoginPage";
import RegisterPage from "../pages/Auth/RegisterPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";
import TransactionListPage from "../pages/Transactions/TransactionListPage";
import TransactionListForm from "../pages/Transactions/TransactionListForm";


export default function AppRouter() {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <Routes>
      {/* --------------------- */}
      {/* RUTAS PÚBLICAS        */}
      {/* --------------------- */}
      <Route
        path="/login"
        element={
          !isAuthenticated ? (
            <LoginPage />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />

      <Route
        path="/register"
        element={
          !isAuthenticated ? (
            <RegisterPage />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />

      {/* --------------------- */}
      {/* RUTAS PROTEGIDAS      */}
      {/* --------------------- */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="transactions" element={<TransactionListPage />} />
        <Route path="transactions/new" element={<TransactionListForm />} />
        <Route path="transactions/edit/:id" element={<TransactionListForm />} />
      </Route>

      {/* --------------------- */}
      {/* REDIRECCIÓN GLOBAL    */}
      {/* --------------------- */}
      <Route
        path="*"
        element={
          <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
        }
      />
    </Routes>
  );
}
