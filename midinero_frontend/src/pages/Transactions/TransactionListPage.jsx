import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getTransactions, deleteTransaction } from "../../api/transactionService";
import { toast } from "react-toastify";
import { Trash, Edit } from "lucide-react";

const TransactionListPage = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Obtener transacciones del backend
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const data = await getTransactions();

        // Validar si data es un array o usar data.results como fallback
        const transactionsArray = Array.isArray(data) ? data : data.results || [];
        setTransactions(transactionsArray);
      } catch (err) {
        console.error("Error fetching transactions:", err);
        setError("Error al obtener las transacciones.");
        setTransactions([]);
        toast.error("Hubo un error al obtener las transacciones.");
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  // Eliminar transacción
  const handleDelete = async (id) => {
    if (window.confirm("¿Estás seguro de que quieres eliminar esta transacción?")) {
      try {
        await deleteTransaction(id);
        setTransactions(transactions.filter((t) => t.id !== id));
        toast.success("Transacción eliminada correctamente.");
      } catch (err) {
        console.error("Error deleting transaction:", err);
        toast.error("Error al eliminar la transacción.");
      }
    }
  };

  if (loading) return <div>Cargando transacciones...</div>;

  return (
    <div className="px-6 py-4">
      <h1 className="text-2xl font-semibold text-gray-800">Lista de Transacciones</h1>

      {error && <div className="text-red-600 mt-4">{error}</div>}

      <div className="mt-6">
        <Link
          to="/transactions/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none mb-4 inline-block"
        >
          Crear Nueva Transacción
        </Link>

        {transactions.length > 0 ? (
          <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-md">
            <thead>
              <tr className="text-left bg-gray-100 border-b border-gray-200">
                <th className="px-4 py-2 text-sm font-medium text-gray-700">Descripción</th>
                <th className="px-4 py-2 text-sm font-medium text-gray-700">Categoría</th>
                <th className="px-4 py-2 text-sm font-medium text-gray-700">Monto</th>
                <th className="px-4 py-2 text-sm font-medium text-gray-700">Fecha</th>
                <th className="px-4 py-2 text-sm font-medium text-gray-700">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm text-gray-800">{t.description}</td>
                  <td className="px-4 py-2 text-sm text-gray-800">{t.category_detail.name}</td>
                  <td className="px-4 py-2 text-sm text-gray-800">{t.amount}</td>
                  <td className="px-4 py-2 text-sm text-gray-800">
                    {new Date(t.date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-800 flex space-x-2">
                    <Link
                      to={`/transactions/${t.id}/edit`}
                      className="text-blue-600 hover:text-blue-700"
                      aria-label="Editar"
                    >
                      <Edit size={16} />
                    </Link>
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="text-red-600 hover:text-red-700"
                      aria-label="Eliminar"
                    >
                      <Trash size={16} />    
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-gray-500 mt-4">No hay transacciones registradas.</div>
        )}
      </div>
    </div>
  );
};

export default TransactionListPage;