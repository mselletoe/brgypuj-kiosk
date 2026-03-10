import api from './http'

/**
 * @file financeService.js
 * @description Admin service for exporting financial statements as PDF.
 * Accessible by all admin roles (Admin + Superadmin).
 */

/**
 * Downloads a financial statement PDF for the given date range and optional service filter.
 *
 * @param {Object}  params
 * @param {string}  params.dateFrom  - ISO date string "YYYY-MM-DD"
 * @param {string}  params.dateTo    - ISO date string "YYYY-MM-DD"
 * @param {string|null} params.service - "documents" | "id_services" | "equipment" | null (all)
 * @returns {Promise<void>}  Triggers browser file download on success
 */
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

  // Build a descriptive filename matching the backend
  const serviceSlug = service || 'all-services'
  const fromSlug    = dateFrom.replace(/-/g, '')
  const toSlug      = dateTo.replace(/-/g, '')
  const filename    = `financial-statement_${serviceSlug}_${fromSlug}-${toSlug}.pdf`

  // Trigger download
  const url  = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href  = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()

  // Cleanup
  link.remove()
  window.URL.revokeObjectURL(url)
}