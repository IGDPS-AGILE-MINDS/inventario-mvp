import { FormEvent, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createProduct, getProduct, updateProduct } from '../api/products'
import { getCategories } from '../api/categories'
import { getSuppliers } from '../api/suppliers'
import type { Category, Product, Supplier } from '../types'

const empty = {
  sku: '', name: '', description: '', category_id: '' as string | number, supplier_id: '' as string | number,
  quantity: 0 as string | number, unit: 'unidad', min_stock: 0 as string | number,
  purchase_price: '' as string | number, sale_price: 0 as string | number,
  entry_date: new Date().toISOString().slice(0, 10), expiration_date: '', location: '', status: 'vigente',
}

export default function ProductFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({ ...empty })
  const [categories, setCategories] = useState<Category[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setLoadError(false)
      setError(null)
      try {
        const [cats, sups, product] = await Promise.all([
          getCategories(), getSuppliers(), id ? getProduct(Number(id)) : Promise.resolve(null),
        ])
        setCategories(cats)
        setSuppliers(sups)
        if (product) setForm({
          ...empty, ...product,
          category_id: product.category_id ?? '', supplier_id: product.supplier_id ?? '',
          description: product.description ?? '', expiration_date: product.expiration_date ?? '',
          location: product.location ?? '',
        })
      } catch (e) {
        setLoadError(true)
        setError(e instanceof Error ? e.message : 'No se pudo cargar el formulario')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const set = (key: string, value: string | number) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!form.sku.trim() || !form.name.trim()) {
      setError('SKU y nombre son obligatorios')
      return
    }
    const quantity = Number(form.quantity)
    const minStock = Number(form.min_stock)
    const salePrice = Number(form.sale_price)
    const initialCost = form.purchase_price === '' ? null : Number(form.purchase_price)
    if (![quantity, minStock, salePrice, ...(initialCost === null ? [] : [initialCost])].every((value) => Number.isFinite(value) && value >= 0)) {
      setError('Cantidad, stock mínimo y precios deben ser números iguales o mayores que cero')
      return
    }
    if (!Number.isInteger(quantity) || !Number.isInteger(minStock)) {
      setError('La cantidad y el stock mínimo deben ser números enteros')
      return
    }
    if (quantity > 0 && initialCost === null) {
      setError('El costo unitario inicial es obligatorio si registras existencias')
      return
    }
    const payload = {
      ...form,
      sku: form.sku.trim(), name: form.name.trim(),
      category_id: form.category_id === '' ? null : Number(form.category_id),
      supplier_id: form.supplier_id === '' ? null : Number(form.supplier_id),
      description: form.description || null,
      expiration_date: form.expiration_date || null,
      location: form.location || null,
      quantity, min_stock: minStock, purchase_price: initialCost, sale_price: salePrice,
      status: form.status as Product['status'],
    }
    setSaving(true)
    try {
      if (id) await updateProduct(Number(id), { ...payload, purchase_price: initialCost ?? 0 })
      else await createProduct(payload)
      navigate('/productos', { state: { notice: id ? 'Producto actualizado' : 'Producto creado' } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar el producto')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p role="status" className="text-gray-500">Cargando formulario…</p>
  if (loadError) return <div><p role="alert" className="text-red-600">{error}</p><button className="text-blue-600" onClick={() => navigate('/productos')}>Volver al listado</button></div>

  return (
    <div className="max-w-3xl">
      <h2 className="text-xl font-semibold mb-4">{id ? 'Editar producto' : 'Nuevo producto'}</h2>
      {error && <p role="alert" className="text-red-600 mb-3">{error}</p>}
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-6 rounded-lg shadow">
        <label className="flex flex-col text-sm">SKU *<input required maxLength={60} className="border rounded px-3 py-2 mt-1" value={form.sku} onChange={(e) => set('sku', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Nombre *<input required maxLength={160} className="border rounded px-3 py-2 mt-1" value={form.name} onChange={(e) => set('name', e.target.value)} /></label>
        <label className="flex flex-col text-sm md:col-span-2">Descripción<textarea maxLength={1000} className="border rounded px-3 py-2 mt-1" value={form.description} onChange={(e) => set('description', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Categoría
          <select className="border rounded px-3 py-2 mt-1" value={form.category_id} onChange={(e) => set('category_id', e.target.value)}>
            <option value="">Sin categoría</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <label className="flex flex-col text-sm">Proveedor
          <select className="border rounded px-3 py-2 mt-1" value={form.supplier_id} onChange={(e) => set('supplier_id', e.target.value)}>
            <option value="">Sin proveedor</option>
            {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </label>
        <label className="flex flex-col text-sm">Cantidad inicial<input type="number" min={0} step={1} required className="border rounded px-3 py-2 mt-1" value={form.quantity} onChange={(e) => set('quantity', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Unidad<input required maxLength={30} className="border rounded px-3 py-2 mt-1" value={form.unit} onChange={(e) => set('unit', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Stock mínimo<input type="number" min={0} step={1} required className="border rounded px-3 py-2 mt-1" value={form.min_stock} onChange={(e) => set('min_stock', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Costo unitario inicial{Number(form.quantity) > 0 ? ' *' : ''}<input type="number" step="0.01" min={0} required={Number(form.quantity) > 0} className="border rounded px-3 py-2 mt-1" value={form.purchase_price} onChange={(e) => set('purchase_price', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Precio de venta<input type="number" step="0.01" min={0} required className="border rounded px-3 py-2 mt-1" value={form.sale_price} onChange={(e) => set('sale_price', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Fecha de ingreso<input type="date" required className="border rounded px-3 py-2 mt-1" value={form.entry_date} onChange={(e) => set('entry_date', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Fecha de vencimiento<input type="date" className="border rounded px-3 py-2 mt-1" value={form.expiration_date} onChange={(e) => set('expiration_date', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Ubicación<input maxLength={120} className="border rounded px-3 py-2 mt-1" value={form.location} onChange={(e) => set('location', e.target.value)} /></label>
        <label className="flex flex-col text-sm">Estado
          <select className="border rounded px-3 py-2 mt-1" value={form.status} onChange={(e) => set('status', e.target.value)}>
            <option value="vigente">Vigente</option><option value="proximo_a_vencer">Próximo a vencer</option>
            <option value="vencido">Vencido</option><option value="agotado">Agotado</option>
          </select>
        </label>
        <div className="md:col-span-2 flex justify-end gap-3 mt-2">
          <button type="button" className="border px-4 py-2 rounded" onClick={() => navigate('/productos')}>Cancelar</button>
          <button disabled={saving} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{saving ? 'Guardando…' : 'Guardar'}</button>
        </div>
      </form>
    </div>
  )
}
