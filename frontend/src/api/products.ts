import { api } from './client'
import type { Paginated, Product, ProductQuery } from '../types'

export async function getProducts(query: ProductQuery): Promise<Paginated<Product>> {
  const params: Record<string, string | number> = { limit: query.limit, offset: query.offset }
  if (query.search) params.search = query.search
  if (query.category_id) params.category_id = query.category_id
  if (query.status) params.status = query.status
  if (query.expiration) params.expiration = query.expiration
  if (query.is_active !== undefined) params.is_active = String(query.is_active)
  const { data } = await api.get<Paginated<Product>>('/products/', { params })
  return data
}

export async function getProduct(id: number): Promise<Product> {
  const { data } = await api.get<Product>(`/products/${id}`)
  return data
}

export type ProductEditableInput = Pick<Product,
  'sku' | 'name' | 'description' | 'category_id' | 'supplier_id' | 'unit' |
  'min_stock' | 'sale_price' | 'entry_date' | 'expiration_date' | 'location'
>
export type ProductCreateInput = ProductEditableInput & {
  quantity: number
  purchase_price: number | null
  status: Product['status']
}

export async function createProduct(input: ProductCreateInput): Promise<Product> {
  const { data } = await api.post<Product>('/products/', input)
  return data
}

export async function updateProduct(id: number, input: Partial<ProductEditableInput>): Promise<Product> {
  const { data } = await api.patch<Product>(`/products/${id}`, input)
  return data
}

export async function deactivateProduct(id: number): Promise<Product> {
  const { data } = await api.patch<Product>(`/products/${id}/deactivate`)
  return data
}
