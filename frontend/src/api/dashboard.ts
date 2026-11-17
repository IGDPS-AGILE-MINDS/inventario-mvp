import { api } from './client'

export interface MovementSummary {
  id: number
  product_id: number | null
  product_name: string | null
  movement_type: 'IN' | 'OUT'
  quantity: number
  created_at: string
}

export interface DashboardSummary {
  total_products: number
  total_units: number
  low_stock: number
  expiring_soon: number
  expired: number
  last_movements: MovementSummary[]
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>('/dashboard/summary')
  return data
}
