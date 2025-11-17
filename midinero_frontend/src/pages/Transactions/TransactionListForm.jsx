import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createTransaction,
  updateTransaction,
  getTransactionById,
} from "../../api/transactionService";
import { getCategories } from "../../api/categoryService";
import { toast } from "react-toastify";

const TransactionListForm = () => {
  const [formData, setFormData] = useState({
    amount: "",
    type: "expense", // "expense" o "income"
    category: "",
    description: "",
    date: new Date().toISOString().split("T")[0],
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);

  const { id } = useParams();
  const navigate = useNavigate();

  // 🔹 Cargar categorías y transacción (si estamos editando)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const cats = await getCategories();
        setCategories(Array.isArray(cats) ? cats : []);

        if (id) {
          const tx = await getTransactionById(id);
          setFormData({
            amount: tx.amount || "",
            type: tx.type || "expense",
            category: tx.category || "",
            description: tx.description || "",
            date: tx.date ? tx.date.split("T")[0] : "",
          });
        }
      } catch (error) {
        console.error("Error cargando datos:", error);
        toast.error("No se pudieron cargar los datos.");
      }
    };

    fetchData();
  }, [id]);

  // 🔹 Manejar cambios del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // 🔹 Manejar envío
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (id) {
        await updateTransaction(id, formData);
        toast.success("Transacción actualizada con éxito.");
      } else {
        await createTransaction(formData);
        toast.success("Transacción creada correctamente.");
      }
      navigate("/transactions");
    } catch (error) {
      console.error("Error guardando transacción:", error);
      toast.error("Error al guardar la transacción.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white shadow-md rounded-xl p-6">
      <h1 className="text-2xl font-semibold text-gray-800 mb-4">
        {id ? "Editar Transacción" : "Nueva Transacción"}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Monto */}
        <div>
          <label
            htmlFor="amount"
            className="block text-sm font-medium text-gray-700"
          >
            Monto
          </label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600"
            required
          />
        </div>

        {/* Tipo */}
        <div>
          <label
            htmlFor="type"
            className="block text-sm font-medium text-gray-700"
          >
            Tipo
          </label>
          <select
            id="type"
            name="type"
            value={formData.type}
            onChange={handleChange}
            className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600"
            required
          >
            <option value="expense">Gasto</option>
            <option value="income">Ingreso</option>
          </select>
        </div>

        {/* Categoría */}
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-gray-700"
          >
            Categoría
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600"
            required
          >
            <option value="">Selecciona una categoría</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        {/* Descripción */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700"
          >
            Descripción
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600"
            rows="3"
          />
        </div>

        {/* Fecha */}
        <div>
          <label
            htmlFor="date"
            className="block text-sm font-medium text-gray-700"
          >
            Fecha
          </label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600"
            required
          />
        </div>

        {/* Botón */}
        <div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
          >
            {loading
              ? "Guardando..."
              : id
              ? "Actualizar Transacción"
              : "Crear Transacción"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TransactionListForm;