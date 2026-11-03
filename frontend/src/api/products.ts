import { api } from './client'
import type { Paginated, Product, ProductQuery } from '../types'

export async function getProducts(query: ProductQuery): Promise<Paginated<Product>> {
  const params: Record<string, string | number> = { limit: query.limit, offset: query.offset }
  if (query.search) params.search = query.search
  if (query.category_id) params.category_id = query.category_id
  if (query.status) params.status = query.status
  if (query.expiration) params.expiration = query.expiration
  const { data } = await api.get<Paginated<Product>>('/products/', { params })
  return data
}

export async function getProduct(id: number): Promise<Product> {
  const { data } = await api.get<Product>(`/products/${id}`)
  return data
}

export type ProductInput = Omit<Product, 'id' | 'created_at' | 'updated_at' | 'weighted_average_cost' | 'expiration_status'>
export type ProductCreateInput = Omit<ProductInput, 'purchase_price'> & { purchase_price: number | null }

export async function createProduct(input: ProductCreateInput): Promise<Product> {
  const { data } = await api.post<Product>('/products/', input)
  return data
}

export async function updateProduct(id: number, input: Partial<ProductInput>): Promise<Product> {
  const { data } = await api.put<Product>(`/products/${id}`, input)
  return data
}

export async function deleteProduct(id: number): Promise<void> {
  await api.delete(`/products/${id}`)
}
