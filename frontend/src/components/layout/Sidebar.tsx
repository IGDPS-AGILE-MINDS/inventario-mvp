import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/productos', label: 'Productos' },
  { to: '/movimientos', label: 'Movimientos' },
  { to: '/categorias', label: 'Categorías' },
  { to: '/proveedores', label: 'Proveedores' },
  { to: '/configuracion', label: 'Configuración' },
]

export default function Sidebar() {
  return (
    <aside className="bg-gray-900 text-gray-200 p-4 md:w-56 md:min-h-screen">
      <h1 className="text-xl font-bold mb-3 md:mb-6 text-white">Inventario</h1>
      <nav aria-label="Navegación principal" className="flex flex-wrap md:flex-col gap-1">
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.to === '/'}
            className={({ isActive }) => `px-3 py-2 rounded ${isActive ? 'bg-gray-700 text-white' : 'hover:bg-gray-800'}`}>
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
