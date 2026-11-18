import type { StockCondition } from '../../types'

const labels: Record<StockCondition, string> = {
  agotado: 'Agotado',
  stock_bajo: 'Stock bajo',
  normal: 'Stock suficiente',
}

const colors: Record<StockCondition, string> = {
  agotado: 'bg-gray-200 text-gray-800',
  stock_bajo: 'bg-orange-100 text-orange-800',
  normal: 'bg-green-100 text-green-800',
}

export default function StockConditionBadge({ condition }: { condition: StockCondition }) {
  return <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${colors[condition]}`}>{labels[condition]}</span>
}
