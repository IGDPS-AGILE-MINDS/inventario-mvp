import { FormEvent, useEffect, useState } from 'react'
import { getSettings, updateSettings } from '../api/settings'

export default function SettingsPage() {
  const [days, setDays] = useState(30)
  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try { const s = await getSettings(); setDays(s.expiration_warning_days) }
    catch (e) { setError(e instanceof Error ? e.message : 'No se pudo cargar la configuración') }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setNotice(null)
    setSaving(true)
    try {
      const s = await updateSettings(days)
      setDays(s.expiration_warning_days)
      setNotice('Configuración guardada')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-xl">
      <h2 className="text-xl font-semibold mb-4">Configuración</h2>
      {notice && <p className="text-green-600 mb-3">{notice}</p>}
      {error && <div role="alert" className="text-red-600 mb-3"><p>{error}</p>{!loading && <button className="underline" onClick={load}>Reintentar</button>}</div>}
      {loading ? <p role="status" className="text-gray-500">Cargando configuración…</p> : <form onSubmit={submit} className="bg-white p-6 rounded-lg shadow flex flex-col gap-4">
        <label className="text-sm flex flex-col">
          Días de anticipación para "próximo a vencer"
          <input type="number" min={0} max={365} required className="border rounded px-3 py-2 mt-1" value={days} onChange={(e) => setDays(Number(e.target.value))} />
        </label>
        <button disabled={saving} type="submit" className="bg-blue-600 text-white px-4 py-2 rounded self-start disabled:opacity-50">{saving ? 'Guardando…' : 'Guardar'}</button>
      </form>}
    </div>
  )
}
