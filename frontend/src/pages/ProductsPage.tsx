import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { deleteProduct, getProducts } from '../api/products'
import { getCategories } from '../api/categories'
import Badge from '../components/ui/Badge'
import ExpirationBadge from '../components/ui/ExpirationBadge'
import Modal from '../components/ui/Modal'
import Pagination from '../components/ui/Pagination'
import type { Category, Paginated, Product, ProductQuery, ProductStatus } from '../types'

const LIMIT = 10

export default function ProductsPage() {
  const location = useLocation()
  const [data, setData] = useState<Paginated<Product> | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState<number | undefined>()
  const [status, setStatus] = useState<ProductStatus | undefined>()
  const [expiration, setExpiration] = useState<string | undefined>()
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toDelete, setToDelete] = useState<Product | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  useEffect(() => { if (location.state?.notice) setNotice(location.state.notice) }, [location.state])

  const load = async (filters: ProductQuery = { search, category_id: categoryId, status, expiration, limit: LIMIT, offset }) => {
    setLoading(true)
    setError(null)
    try {
      const [products, cats] = await Promise.all([
        getProducts({ ...filters, search: filters.search || undefined, limit: LIMIT }),
        getCategories(),
      ])
      setData(products)
      setCategories(cats)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al cargar')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset, categoryId, status, expiration])

  const confirmDelete = async () => {
    if (!toDelete) return
    setNotice(null)
    setError(null)
    setDeleting(true)
    try {
      await deleteProduct(toDelete.id)
      setNotice('Producto eliminado')
      setToDelete(null)
      load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al eliminar')
    } finally {
      setDeleting(false)
    }
  }

  const searchNow = () => {
    if (offset === 0) load()
    else setOffset(0)
  }

  const clearFilters = () => {
    setSearch('')
    setCategoryId(undefined)
    setStatus(undefined)
    setExpiration(undefined)
    setOffset(0)
    load({ search: undefined, category_id: undefined, status: undefined, expiration: undefined, limit: LIMIT, offset: 0 })
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Productos</h2>
        <Link to="/productos/nuevo" className="bg-blue-600 text-white px-4 py-2 rounded">Nuevo producto</Link>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <input className="border rounded px-3 py-2" aria-label="Buscar por nombre o SKU" placeholder="Buscar por nombre o SKU" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); searchNow() } }} />
        <select className="border rounded px-3 py-2" value={categoryId ?? ''} onChange={(e) => { setOffset(0); setCategoryId(e.target.value ? Number(e.target.value) : undefined) }}>
          <option value="">Todas las categorías</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select className="border rounded px-3 py-2" value={status ?? ''} onChange={(e) => { setOffset(0); setStatus((e.target.value || undefined) as ProductStatus | undefined) }}>
          <option value="">Todos los estados</option>
          <option value="vigente">Vigente</option>
          <option value="proximo_a_vencer">Próximo a vencer</option>
          <option value="vencido">Vencido</option>
          <option value="agotado">Agotado</option>
        </select>
        <select className="border rounded px-3 py-2" value={expiration ?? ''} onChange={(e) => { setOffset(0); setExpiration(e.target.value || undefined) }}>
          <option value="">Cualquier vencimiento</option>
          <option value="vigente">Vigente</option>
          <option value="proximo_a_vencer">Próximo a vencer</option>
          <option value="vencido">Vencido</option>
          <option value="sin_fecha">Sin fecha</option>
        </select>
        <button className="border rounded px-4 py-2" onClick={searchNow}>Buscar</button>
      </div>

      {notice && <p className="text-green-600 mb-3">{notice}</p>}
      {error && <div role="alert" className="text-red-600 mb-3"><p>{error}</p><button className="underline" onClick={() => load()}>Reintentar</button></div>}
      {loading && <p className="text-gray-500">Cargando...</p>}

      {!loading && data?.items.length === 0 && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-700 mb-3">No se encontraron productos con los criterios de búsqueda.</p>
          <button className="border rounded px-4 py-2" onClick={clearFilters}>Limpiar filtros</button>
        </div>
      )}

      {!loading && data && data.items.length > 0 && (
        <div className="overflow-x-auto bg-white rounded-lg shadow">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-left">
              <tr>
                <th className="p-3">Imagen</th><th className="p-3">SKU</th><th className="p-3">Nombre</th><th className="p-3">Cantidad</th><th className="p-3">Estado</th><th className="p-3">Vencimiento</th><th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="p-3"><img src={`https://picsum.photos/seed/${p.id}/160/160`} alt={p.name} className="w-16 h-16 object-cover rounded" /></td>
                  <td className="p-3">{p.sku}</td>
                  <td className="p-3">{p.name}</td>
                  <td className="p-3">
                    {p.quantity} {p.unit}
                    {p.quantity <= p.min_stock && <span className="ml-2 px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-700">Stock bajo</span>}
                  </td>
                  <td className="p-3"><Badge status={p.status} /></td>
                  <td className="p-3"><ExpirationBadge status={p.expiration_status} /> {p.expiration_date ?? ''}</td>
                  <td className="p-3 flex gap-3">
                    <Link className="text-blue-600" to={`/productos/${p.id}`}>Ver</Link>
                    <Link className="text-gray-600" to={`/productos/${p.id}/editar`}>Editar</Link>
                    <button className="text-red-600" onClick={() => setToDelete(p)}>Eliminar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && <Pagination total={data.total} limit={LIMIT} offset={offset} onPage={setOffset} />}

      {toDelete && (
        <Modal title="Eliminar producto" onClose={() => setToDelete(null)}>
          <p className="mb-4">¿Seguro que deseas eliminar <strong>{toDelete.name}</strong>?</p>
          {error && <p role="alert" className="text-red-600 mb-3">{error}</p>}
          <div className="flex justify-end gap-3">
            <button className="border px-4 py-2 rounded" onClick={() => setToDelete(null)}>Cancelar</button>
            <button disabled={deleting} className="bg-red-600 text-white px-4 py-2 rounded disabled:opacity-50" onClick={confirmDelete}>{deleting ? 'Eliminando…' : 'Eliminar'}</button>
          </div>
        </Modal>
      )}
    </div>
  )
}

