import { FormEvent, useEffect, useState } from 'react'
import { getMovements, registerMovement } from '../api/movements'
import { getProducts } from '../api/products'
import Modal from '../components/ui/Modal'
import Pagination from '../components/ui/Pagination'
import type { MovementList, MovementType, Product } from '../types'

const LIMIT = 10

export default function MovementsPage() {
  const [data, setData] = useState<MovementList | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [typeFilter, setTypeFilter] = useState<MovementType | undefined>()
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [productId, setProductId] = useState<number | ''>('')
  const [type, setType] = useState<MovementType>('IN')
  const [quantity, setQuantity] = useState(1)
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [movements, prods] = await Promise.all([
        getMovements({ movement_type: typeFilter, limit: LIMIT, offset }),
        getProducts({ limit: 100, offset: 0 }),
      ])
      setData(movements)
      setProducts(prods.items)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al cargar')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [offset, typeFilter])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!productId) { setError('Selecciona un producto'); return }
    if (quantity < 1) { setError('La cantidad debe ser mayor a 0'); return }
    setNotice(null)
    setSaving(true)
    try {
      await registerMovement(type, { product_id: Number(productId), quantity, note: note || undefined })
      setNotice('Movimiento registrado')
      setShowForm(false)
      setNote('')
      setQuantity(1)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrar')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Movimientos</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={() => setShowForm(true)}>Registrar movimiento</button>
      </div>

      <div className="mb-4">
        <select className="border rounded px-3 py-2" value={typeFilter ?? ''} onChange={(e) => { setOffset(0); setTypeFilter((e.target.value || undefined) as MovementType | undefined) }}>
          <option value="">Todos</option>
          <option value="IN">Entradas</option>
          <option value="OUT">Salidas</option>
        </select>
      </div>

      {notice && <p className="text-green-600 mb-3">{notice}</p>}
      {error && !showForm && <div role="alert" className="text-red-600 mb-3"><p>{error}</p>{!loading && <button className="underline" onClick={load}>Reintentar</button>}</div>}
      {loading && <p className="text-gray-500">Cargando...</p>}

      {data && data.items.length === 0 && !loading && <p className="text-gray-500">No hay movimientos.</p>}
      {data && data.items.length > 0 && (
        <div className="overflow-x-auto bg-white rounded-lg shadow">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-left">
              <tr><th className="p-3">Fecha</th><th className="p-3">Producto</th><th className="p-3">Tipo</th><th className="p-3">Cantidad</th><th className="p-3">Anterior</th><th className="p-3">Nuevo</th><th className="p-3">Nota</th></tr>
            </thead>
            <tbody>
              {data.items.map((m) => (
                <tr key={m.id} className="border-t">
                  <td className="p-3">{new Date(m.created_at).toLocaleString()}</td>
                  <td className="p-3">{m.product_name ?? m.product_id}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${m.movement_type === 'IN' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {m.movement_type === 'IN' ? 'Entrada' : 'Salida'}
                    </span>
                  </td>
                  <td className="p-3">{m.quantity}</td>
                  <td className="p-3">{m.previous_quantity}</td>
                  <td className="p-3">{m.new_quantity}</td>
                  <td className="p-3">{m.note ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && <Pagination total={data.total} limit={LIMIT} offset={offset} onPage={setOffset} />}

      {showForm && (
        <Modal title="Registrar movimiento" onClose={() => setShowForm(false)}>
          <form onSubmit={submit} className="flex flex-col gap-3">
            {error && <p role="alert" className="text-red-600">{error}</p>}
            <label className="text-sm flex flex-col">Producto
              <select className="border rounded px-3 py-2 mt-1" value={productId} onChange={(e) => setProductId(e.target.value ? Number(e.target.value) : '')}>
                <option value="">Selecciona...</option>
                {products.map((p) => <option key={p.id} value={p.id}>{p.name} (stock: {p.quantity})</option>)}
              </select>
            </label>
            <label className="text-sm flex flex-col">Tipo
              <select className="border rounded px-3 py-2 mt-1" value={type} onChange={(e) => setType(e.target.value as MovementType)}>
                <option value="IN">Entrada</option>
                <option value="OUT">Salida</option>
              </select>
            </label>
            <label className="text-sm flex flex-col">Cantidad
              <input type="number" min={1} className="border rounded px-3 py-2 mt-1" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} />
            </label>
            <label className="text-sm flex flex-col">Nota
              <input className="border rounded px-3 py-2 mt-1" value={note} onChange={(e) => setNote(e.target.value)} />
            </label>
            <div className="flex justify-end gap-3 mt-2">
              <button type="button" className="border px-4 py-2 rounded" onClick={() => setShowForm(false)}>Cancelar</button>
              <button disabled={saving} type="submit" className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{saving ? 'Guardando…' : 'Registrar'}</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
