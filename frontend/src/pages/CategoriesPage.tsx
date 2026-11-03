import { FormEvent, useEffect, useState } from 'react'
import { createCategory, deleteCategory, getCategories, updateCategory } from '../api/categories'
import Modal from '../components/ui/Modal'
import type { Category } from '../types'

export default function CategoriesPage() {
  const [items, setItems] = useState<Category[]>([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [editing, setEditing] = useState<Category | null>(null)
  const [toDelete, setToDelete] = useState<Category | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try { setItems(await getCategories()) }
    catch (e) { setError(e instanceof Error ? e.message : 'No se pudieron cargar las categorías') }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const openEdit = (c: Category) => { setEditing(c); setName(c.name); setDescription(c.description ?? '') }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!name.trim()) { setError('El nombre es obligatorio'); return }
    setNotice(null)
    setSaving(true)
    try {
      if (editing) await updateCategory(editing.id, { name, description: description || undefined })
      else await createCategory({ name, description: description || undefined })
      setNotice(editing ? 'Categoría actualizada' : 'Categoría creada')
      setEditing(null); setName(''); setDescription(''); load()
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
      await deleteCategory(toDelete.id)
      setNotice('Categoría eliminada')
      setToDelete(null)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar la categoría')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Categorías</h2>
      {notice && <p role="status" className="text-green-700 mb-3">{notice}</p>}
      {error && !toDelete && <div role="alert" className="text-red-600 mb-3"><p>{error}</p>{!loading && <button className="underline" onClick={load}>Reintentar</button>}</div>}
      <form onSubmit={submit} className="bg-white p-4 rounded-lg shadow mb-4 flex gap-3 flex-wrap">
        <input required maxLength={120} className="border rounded px-3 py-2 flex-1" placeholder="Nombre" value={name} onChange={(e) => setName(e.target.value)} />
        <input maxLength={500} className="border rounded px-3 py-2 flex-1" placeholder="Descripción" value={description} onChange={(e) => setDescription(e.target.value)} />
        <button disabled={saving} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{saving ? 'Guardando…' : editing ? 'Actualizar' : 'Agregar'}</button>
        {editing && <button type="button" className="border px-4 py-2 rounded" onClick={() => { setEditing(null); setName(''); setDescription('') }}>Cancelar</button>}
      </form>
      {loading && <p role="status" className="text-gray-500">Cargando categorías…</p>}
      {!loading && items.length === 0 && <p className="text-gray-500">No hay categorías todavía.</p>}
      {!loading && items.length > 0 && <div className="overflow-x-auto"><table className="w-full bg-white rounded-lg shadow text-sm">
        <thead className="bg-gray-100 text-left"><tr><th className="p-3">Nombre</th><th className="p-3">Descripción</th><th className="p-3"></th></tr></thead>
        <tbody>
          {items.map((c) => (
            <tr key={c.id} className="border-t">
              <td className="p-3">{c.name}</td>
              <td className="p-3">{c.description ?? '—'}</td>
              <td className="p-3 flex gap-3">
                <button className="text-gray-600" onClick={() => openEdit(c)}>Editar</button>
                <button className="text-red-600" onClick={() => setToDelete(c)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table></div>}
      {toDelete && (
        <Modal title="Eliminar categoría" onClose={() => setToDelete(null)}>
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
