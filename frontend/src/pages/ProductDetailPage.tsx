import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getProduct } from '../api/products'
import { getMovements } from '../api/movements'
import Badge from '../components/ui/Badge'
import ExpirationBadge from '../components/ui/ExpirationBadge'
import StockConditionBadge from '../components/ui/StockConditionBadge'
import Pagination from '../components/ui/Pagination'
import type { MovementList, Product } from '../types'
import { formatMoney } from '../utils/formatMoney'

const MOVEMENT_LIMIT = 10

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState<Product | null>(null)
  const [movements, setMovements] = useState<MovementList | null>(null)
  const [movementOffset, setMovementOffset] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      Promise.all([
        getProduct(Number(id)),
        getMovements({ product_id: Number(id), limit: MOVEMENT_LIMIT, offset: movementOffset }),
      ]).then(([loadedProduct, loadedMovements]) => {
        setProduct(loadedProduct)
        setMovements(loadedMovements)
      }).catch((e) => setError(e.message))
    }
  }, [id, movementOffset])

  if (error) return <div><p role="alert" className="text-red-600 mb-3">{error}</p><button className="text-blue-600" onClick={() => navigate('/productos')}>Volver al listado</button></div>
  if (!product) return <p role="status" className="text-gray-500">Cargando producto…</p>

  const rows: [string, React.ReactNode][] = [
    ['SKU', product.sku], ['Nombre', product.name], ['Descripción', product.description ?? '—'],
    ['Cantidad', `${product.quantity} ${product.unit}`], ['Stock mínimo', product.min_stock],
    ['Condición del stock', <StockConditionBadge condition={product.stock_condition} />],
    ['Costo promedio ponderado', product.weighted_average_cost === null ? 'Aún no establecido' : formatMoney(product.weighted_average_cost)],
    ['Costo unitario inicial', formatMoney(product.purchase_price)], ['Precio de venta', formatMoney(product.sale_price)],
    ['Ingreso', product.entry_date], ['Vencimiento', <span className="flex items-center gap-2"><ExpirationBadge status={product.expiration_status} />{product.expiration_date ?? '—'}</span>],
    ['Ubicación', product.location ?? '—'], ['Estado', <Badge status={product.status} />],
    ['Disponibilidad', product.is_active ? 'Activo' : 'Desactivado'],
    ['Creado', product.created_at], ['Actualizado', product.updated_at],
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{product.name}</h2>
        <Link to={`/productos/${product.id}/editar`} className="text-blue-600">Editar</Link>
      </div>
      <img src={`https://picsum.photos/seed/${product.id}/800/500`} alt={product.name} className="w-full max-w-2xl rounded-lg mb-4 object-cover" />
      <dl className="bg-white rounded-lg shadow divide-y">
        {rows.map(([k, v]) => (
          <div key={k} className="grid grid-cols-3 p-3">
            <dt className="text-gray-500">{k}</dt>
            <dd className="col-span-2">{v}</dd>
          </div>
        ))}
      </dl>
      <section className="mt-6">
        <h3 className="text-lg font-semibold mb-3">Historial de movimientos</h3>
        {movements?.items.length === 0 && <p className="text-gray-500">Este producto no tiene movimientos registrados.</p>}
        {movements && movements.items.length > 0 && <>
          <div className="overflow-x-auto bg-white rounded-lg shadow">
            <table className="w-full text-sm">
              <thead className="bg-gray-100 text-left"><tr><th className="p-3">Fecha</th><th className="p-3">Tipo</th><th className="p-3">Cantidad</th><th className="p-3">Anterior</th><th className="p-3">Nueva</th><th className="p-3">Costo unitario</th><th className="p-3">Nota</th></tr></thead>
              <tbody>{movements.items.map((movement) => <tr key={movement.id} className="border-t">
                <td className="p-3">{new Date(movement.created_at).toLocaleString()}</td>
                <td className="p-3">{movement.movement_type === 'IN' ? 'Entrada' : `Salida · ${movement.reason}`}</td>
                <td className="p-3">{movement.quantity}</td><td className="p-3">{movement.previous_quantity}</td><td className="p-3">{movement.new_quantity}</td>
                <td className="p-3">{movement.unit_cost === null ? '—' : formatMoney(movement.unit_cost)}</td><td className="p-3">{movement.note ?? '—'}</td>
              </tr>)}</tbody>
            </table>
          </div>
          <Pagination total={movements.total} limit={MOVEMENT_LIMIT} offset={movementOffset} onPage={setMovementOffset} />
        </>}
      </section>
    </div>
  )
}
