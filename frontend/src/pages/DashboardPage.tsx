import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardSummary, getDashboardSummary } from '../api/dashboard'

const cards = [
  { key: 'total_products', label: 'Productos registrados', color: 'bg-blue-100 text-blue-800' },
  { key: 'total_units', label: 'Unidades disponibles', color: 'bg-indigo-100 text-indigo-800' },
  { key: 'low_stock', label: 'Stock bajo', color: 'bg-orange-100 text-orange-800' },
  { key: 'expiring_soon', label: 'Próximos a vencer', color: 'bg-yellow-100 text-yellow-800' },
  { key: 'expired', label: 'Vencidos', color: 'bg-red-100 text-red-800' },
] as const

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    setError(null)
    getDashboardSummary()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Error al cargar'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  if (loading) return <p className="text-gray-500">Cargando dashboard...</p>
  if (error) return <div role="alert"><p className="text-red-600">{error}</p><button className="text-blue-600 underline" onClick={load}>Reintentar</button></div>
  if (!data) return null

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Dashboard</h2>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.key} className={`rounded-lg p-4 ${c.color}`}>
            <p className="text-3xl font-bold">{data[c.key].toLocaleString()}</p>
            <p className="text-sm mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      <h3 className="text-lg font-semibold mb-3">Últimos movimientos</h3>
      {data.last_movements.length === 0 ? (
        <p className="text-gray-500">Aún no hay movimientos registrados.</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-left">
              <tr>
                <th className="p-3">Fecha</th>
                <th className="p-3">Producto</th>
                <th className="p-3">Tipo</th>
                <th className="p-3">Cantidad</th>
              </tr>
            </thead>
            <tbody>
              {data.last_movements.map((m) => (
                <tr key={m.id} className="border-t">
                  <td className="p-3">{new Date(m.created_at).toLocaleString()}</td>
                  <td className="p-3">{m.product_name ?? `#${m.product_id}`}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${m.movement_type === 'IN' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {m.movement_type === 'IN' ? 'Entrada' : 'Salida'}
                    </span>
                  </td>
                  <td className="p-3">{m.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Link to="/movimientos" className="inline-block mt-4 text-blue-600">Ver todos los movimientos →</Link>
    </div>
  )
}
