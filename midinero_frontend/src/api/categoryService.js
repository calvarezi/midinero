// src/api/categoryService.js
import api from "./axiosConfig";

// Obtener todas las categorías
const getCategories = async () => {
  const response = await api.get("/api/finances/categories/");
  return response.data.data || response.data.results || response.data;
};

// Obtener una categoría por ID
const getCategoryById = async (id) => {
  const response = await api.get(`/api/finances/categories/${id}/`);
  return response.data.data || response.data;
};

// Crear una nueva categoría
const createCategory = async (categoryData) => {
  const response = await api.post("/api/finances/categories/", categoryData);
  return response.data.data || response.data;
};

// Actualizar una categoría existente
const updateCategory = async (id, categoryData) => {
  const response = await api.put(`/api/finances/categories/${id}/`, categoryData);
  return response.data.data || response.data;
};

// Eliminar una categoría
const deleteCategory = async (id) => {
  const response = await api.delete(`/api/finances/categories/${id}/`);
  return response.data;
};

// ✅ Exportaciones nombradas
export {
  getCategories,
  getCategoryById,
  createCategory,
  updateCategory,
  deleteCategory,
};