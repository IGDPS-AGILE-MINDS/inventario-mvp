import { FormEvent, useEffect, useState } from 'react'
import { createSupplier, deleteSupplier, getSuppliers, updateSupplier } from '../api/suppliers'
import Modal from '../components/ui/Modal'
import type { Supplier } from '../types'

const blank = { name: '', contact_name: '', email: '', phone: '', address: '' }

export default function SuppliersPage() {
  const [items, setItems] = useState<Supplier[]>([])
  const [form, setForm] = useState({ ...blank })
  const [editing, setEditing] = useState<Supplier | null>(null)
  const [toDelete, setToDelete] = useState<Supplier | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try { setItems(await getSuppliers()) }
    catch (e) { setError(e instanceof Error ? e.message : 'No se pudieron cargar los proveedores') }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const openEdit = (s: Supplier) => {
    setEditing(s)
    setForm({
      name: s.name,
      contact_name: s.contact_name ?? '',
      email: s.email ?? '',
      phone: s.phone ?? '',
      address: s.address ?? '',
    })
  }

  const set = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!form.name.trim()) { setError('El nombre es obligatorio'); return }
    setNotice(null)
    setSaving(true)
    const payload = {
      name: form.name,
      contact_name: form.contact_name || undefined,
      email: form.email || undefined,
      phone: form.phone || undefined,
      address: form.address || undefined,
    }
    try {
      if (editing) await updateSupplier(editing.id, payload)
      else await createSupplier(payload)
      setNotice(editing ? 'Proveedor actualizado' : 'Proveedor creado')
      setEditing(null); setForm({ ...blank }); load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error')
    } finally {
      setSaving(false)
    }
  }

  const confirmDelete = async () => {
    if (!toDelete) return
    setNotice(null)
    setDeleting(true)
    setError(null)
    try {
      await deleteSupplier(toDelete.id)
      setNotice('Proveedor eliminado')
      setToDelete(null)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar el proveedor')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Proveedores</h2>
      {notice && <p role="status" className="text-green-700 mb-3">{notice}</p>}
      {error && !toDelete && <div role="alert" className="text-red-600 mb-3"><p>{error}</p>{!loading && <button className="underline" onClick={load}>Reintentar</button>}</div>}
      <form onSubmit={submit} className="bg-white p-4 rounded-lg shadow mb-4 flex flex-wrap gap-3">
        <input required maxLength={120} className="border rounded px-3 py-2" placeholder="Nombre *" value={form.name} onChange={(e) => set('name', e.target.value)} />
        <input maxLength={120} className="border rounded px-3 py-2" placeholder="Contacto" value={form.contact_name} onChange={(e) => set('contact_name', e.target.value)} />
        <input type="email" maxLength={120} className="border rounded px-3 py-2" placeholder="Email" value={form.email} onChange={(e) => set('email', e.target.value)} />
        <input maxLength={40} className="border rounded px-3 py-2" placeholder="Teléfono" value={form.phone} onChange={(e) => set('phone', e.target.value)} />
        <input maxLength={255} className="border rounded px-3 py-2" placeholder="Dirección" value={form.address} onChange={(e) => set('address', e.target.value)} />
        <button disabled={saving} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{saving ? 'Guardando…' : editing ? 'Actualizar' : 'Agregar'}</button>
        {editing && <button type="button" className="border px-4 py-2 rounded" onClick={() => { setEditing(null); setForm({ ...blank }) }}>Cancelar</button>}
      </form>
      {loading && <p role="status" className="text-gray-500">Cargando proveedores…</p>}
      {!loading && items.length === 0 && <p className="text-gray-500">No hay proveedores todavía.</p>}
      {!loading && items.length > 0 && <div className="overflow-x-auto"><table className="w-full bg-white rounded-lg shadow text-sm">
        <thead className="bg-gray-100 text-left">
          <tr><th className="p-3">Nombre</th><th className="p-3">Contacto</th><th className="p-3">Email</th><th className="p-3">Teléfono</th><th className="p-3"></th></tr>
        </thead>
        <tbody>
          {items.map((s) => (
            <tr key={s.id} className="border-t">
              <td className="p-3">{s.name}</td>
              <td className="p-3">{s.contact_name ?? '—'}</td>
              <td className="p-3">{s.email ?? '—'}</td>
              <td className="p-3">{s.phone ?? '—'}</td>
              <td className="p-3 flex gap-3">
                <button className="text-gray-600" onClick={() => openEdit(s)}>Editar</button>
                <button className="text-red-600" onClick={() => setToDelete(s)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table></div>}
      {toDelete && (
        <Modal title="Eliminar proveedor" onClose={() => setToDelete(null)}>
          <p className="mb-4">¿Eliminar <strong>{toDelete.name}</strong>?</p>
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
