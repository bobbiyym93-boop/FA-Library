function bindTaskTypeModals() {
  document.addEventListener('click', (event) => {
    const label = event.target.closest('.density-task-page .task-options label')
    if (!label) return
    if (event.target.closest('.config-button')) return

    const hiddenConfigButton = label.querySelector('.config-button')
    if (!hiddenConfigButton) return

    window.setTimeout(() => hiddenConfigButton.click(), 0)
  })
}

bindTaskTypeModals()
