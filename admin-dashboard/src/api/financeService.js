import api from './http'

export async function exportFinancialStatement({ dateFrom, dateTo, service = null }) {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to:   dateTo,
  })

  if (service) {
    params.append('service', service)
  }

  const response = await api.get(`/admin/finance/statement/export?${params.toString()}`, {
    responseType: 'blob',
  })

  const serviceSlug = service || 'all-services'
  const fromSlug    = dateFrom.replace(/-/g, '')
  const toSlug      = dateTo.replace(/-/g, '')
  const filename    = `financial-statement_${serviceSlug}_${fromSlug}-${toSlug}.pdf`

  const url  = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href  = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()

  link.remove()
  window.URL.revokeObjectURL(url)
}