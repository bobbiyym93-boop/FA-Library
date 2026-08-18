function getHeatmapCellInfo(cell) {
  const heatmap = cell.closest('.heatmap')
  if (!heatmap) return null
  const cells = Array.from(heatmap.querySelectorAll(':scope > i'))
  const index = cells.indexOf(cell)
  if (index < 0) return null

  const title = cell.getAttribute('title') || ''
  const match = title.match(/value\s+(-?\d+(?:\.\d+)?)/i)
  const value = match ? match[1] : '-'
  const columns = 15
  const x = index % columns
  const y = Math.floor(index / columns)

  // Prototype association: only some density windows have an SEM image.
  // This is intentionally sparse so blocks without SEM show coordinates/value only.
  const hasSem = index % 5 === 0 || index % 11 === 0
  const semType = index % 3 === 0 ? 'open' : index % 3 === 1 ? 'bridge' : 'hotspot'
  return { x, y, value, hasSem, semType }
}

function ensureTooltip() {
  let tooltip = document.querySelector('.density-hover-tooltip')
  if (tooltip) return tooltip
  tooltip = document.createElement('div')
  tooltip.className = 'density-hover-tooltip'
  document.body.appendChild(tooltip)
  return tooltip
}

function renderTooltip(tooltip, info) {
  const sem = info.hasSem
    ? `<div class="density-hover-sem sem-${info.semType}"><span>SEM</span><i></i></div>`
    : ''
  tooltip.innerHTML = `
    <div class="density-hover-values">
      <div><span>x</span><strong>${info.x}</strong></div>
      <div><span>y</span><strong>${info.y}</strong></div>
      <div><span>value</span><strong>${info.value}</strong></div>
    </div>
    ${sem}
  `
}

function moveTooltip(tooltip, event) {
  const gap = 14
  const rect = tooltip.getBoundingClientRect()
  let left = event.clientX + gap
  let top = event.clientY + gap
  if (left + rect.width > window.innerWidth - 8) left = event.clientX - rect.width - gap
  if (top + rect.height > window.innerHeight - 8) top = event.clientY - rect.height - gap
  tooltip.style.left = `${Math.max(8, left)}px`
  tooltip.style.top = `${Math.max(8, top)}px`
}

export function installHeatmapSemHover() {
  const tooltip = ensureTooltip()
  document.addEventListener('mouseover', event => {
    const cell = event.target.closest?.('.density-task-page .heatmap > i')
    if (!cell) return
    const info = getHeatmapCellInfo(cell)
    if (!info) return
    renderTooltip(tooltip, info)
    tooltip.classList.add('visible')
  })
  document.addEventListener('mousemove', event => {
    if (!tooltip.classList.contains('visible')) return
    moveTooltip(tooltip, event)
  })
  document.addEventListener('mouseout', event => {
    const cell = event.target.closest?.('.density-task-page .heatmap > i')
    if (!cell) return
    tooltip.classList.remove('visible')
  })
}
