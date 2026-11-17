import { api } from './client'
import type { Movement, MovementList, MovementType } from '../types'

export async function getMovements(params: { product_id?: number; movement_type?: MovementType; limit: number; offset: number }): Promise<MovementList> {
  const query: Record<string, string | number> = { limit: params.limit, offset: params.offset }
  if (params.product_id) query.product_id = params.product_id
  if (params.movement_type) query.movement_type = params.movement_type
  const { data } = await api.get<MovementList>('/movements/', { params: query })
  return data
}

export async function registerMovement(type: MovementType, input: { product_id: number; quantity: number; note?: string; unit_cost?: number; reason?: 'consumo' | 'perdida' | 'ajuste' }): Promise<Movement> {
  const { data } = await api.post<Movement>(`/movements/${type === 'IN' ? 'in' : 'out'}`, input)
  return data
}
