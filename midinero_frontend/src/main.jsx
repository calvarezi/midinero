// Solo se importa React para usar React.StrictMode
import React from "react";
import ReactDOM from "react-dom/client";

import { QueryClient, QueryClientProvider } from "react-query";
import { BrowserRouter } from "react-router-dom";
import AppRouter from "./routes/AppRouter";
import { AuthProvider } from "./context/AuthContext";

import { Toaster } from "react-hot-toast";
import "./index.css";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>

          {/* Toaster global — único, optimizado y con duración extendida */}
          <Toaster
            position="top-center"
            reverseOrder={false}
            toastOptions={{
              duration: 2500,
              style: {
                fontSize: "15px",
              },
            }}
          />

          {/* Rutas principales de la app */}
          <AppRouter />

        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
