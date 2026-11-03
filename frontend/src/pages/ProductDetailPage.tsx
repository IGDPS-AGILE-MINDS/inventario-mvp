import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getProduct } from '../api/products'
import Badge from '../components/ui/Badge'
import ExpirationBadge from '../components/ui/ExpirationBadge'
import type { Product } from '../types'

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState<Product | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) getProduct(Number(id)).then(setProduct).catch((e) => setError(e.message))
  }, [id])

  if (error) return <div><p role="alert" className="text-red-600 mb-3">{error}</p><button className="text-blue-600" onClick={() => navigate('/productos')}>Volver al listado</button></div>
  if (!product) return <p role="status" className="text-gray-500">Cargando producto…</p>

  const rows: [string, React.ReactNode][] = [
    ['SKU', product.sku], ['Nombre', product.name], ['Descripción', product.description ?? '—'],
    ['Cantidad', `${product.quantity} ${product.unit}`], ['Stock mínimo', product.min_stock],
    ['Costo promedio ponderado', product.weighted_average_cost === null ? 'Aún no establecido' : `$${product.weighted_average_cost}`],
    ['Costo unitario inicial', `$${product.purchase_price}`], ['Precio de venta', `$${product.sale_price}`],
    ['Ingreso', product.entry_date], ['Vencimiento', <span className="flex items-center gap-2"><ExpirationBadge status={product.expiration_status} />{product.expiration_date ?? '—'}</span>],
    ['Ubicación', product.location ?? '—'], ['Estado', <Badge status={product.status} />],
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
    </div>
  )
}
