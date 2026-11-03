export interface Category {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface Supplier {
  id: number
  name: string
  contact_name: string | null
  email: string | null
  phone: string | null
  address: string | null
  created_at: string
  updated_at: string
}

export type ProductStatus = 'vigente' | 'proximo_a_vencer' | 'vencido' | 'agotado'

export interface Product {
  id: number
  sku: string
  name: string
  description: string | null
  category_id: number | null
  supplier_id: number | null
  quantity: number
  unit: string
  min_stock: number
  purchase_price: number
  weighted_average_cost: number | null
  sale_price: number
  entry_date: string
  expiration_date: string | null
  location: string | null
  status: ProductStatus
  expiration_status: 'vigente' | 'proximo_a_vencer' | 'vencido' | 'sin_fecha'
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ProductQuery {
  search?: string
  category_id?: number
  status?: ProductStatus
  expiration?: string
  limit: number
  offset: number
}

export type MovementType = 'IN' | 'OUT'

export interface Movement {
  id: number
  product_id: number
  product_name: string | null
  movement_type: MovementType
  quantity: number
  previous_quantity: number
  new_quantity: number
  note: string | null
  created_at: string
}

export interface MovementList {
  items: Movement[]
  total: number
  limit: number
  offset: number
}
