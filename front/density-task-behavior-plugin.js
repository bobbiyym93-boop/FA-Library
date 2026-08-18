export function densityTaskBehaviorPlugin() {
  return {
    name: 'density-task-behavior',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/components/DensityTaskView.vue')) return null
      const target = "tasks.value.unshift(task);selectedTaskId.value=task.id;activeTab.value='results'"
      const replacement = "tasks.value.unshift(task);selectedTaskId.value=task.id"
      if (!code.includes(target)) return null
      return { code: code.replace(target, replacement), map: null }
    },
  }
}
