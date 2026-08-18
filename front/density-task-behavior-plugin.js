export function densityTaskBehaviorPlugin() {
  return {
    name: 'density-task-behavior',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/components/DensityTaskView.vue')) return null

      let output = code
      output = output.replace(
        "const tabs = [['setup','Set Up'],['results','结果'],['compare','layer 对比'],['gradient','梯度 Spec'],['history','历史'],['fa','FA 关联']]",
        "const detailTabs = [['results','结果'],['compare','layer 对比'],['gradient','梯度 Spec'],['history','历史'],['fa','FA 关联']]"
      )

      output = output.replace(
        "tasks.value.unshift(task);selectedTaskId.value=task.id;activeTab.value='results'",
        "tasks.value.unshift(task);selectedTaskId.value=task.id"
      )

      const oldNav = '<nav class="density-task-tabs"><button v-for="tab in tabs" :key="tab[0]" :class="{active:activeTab===tab[0]}" @click="tab[0]===\'setup\'?activeTab=\'setup\':requireTask(tab[0])">{{ tab[1] }}</button></nav>'
      const newNav = '<nav v-if="activeTab===\'setup\'" class="density-task-tabs"><button class="active">Set Up</button></nav><nav v-else-if="selectedTask" class="density-task-tabs detail-tabs"><button class="setup-parent" @click="activeTab=\'setup\'">Set Up</button><span class="submenu-arrow">›</span><span class="submenu-task">{{ selectedTask.name }}</span><button v-for="tab in detailTabs" :key="tab[0]" :class="{active:activeTab===tab[0]}" @click="activeTab=tab[0]">{{ tab[1] }}</button></nav>'
      output = output.replace(oldNav, newNav)

      output = output.replace(
        '先在 Set Up 创建任务，再进入其他页签查看该任务的分析结果。',
        '先在 Set Up 创建任务，再从“已创建任务”点击“查看结果”进入该任务的结果子菜单。'
      )
      output = output.replace(
        '其他页签均从这里选择任务查看',
        '结果子菜单只能从这里的“查看结果”进入'
      )

      const stylePatch = '.detail-tabs{align-items:center}.detail-tabs .setup-parent{color:#2563eb}.detail-tabs .submenu-arrow{color:#98a2b3;padding:0 2px}.detail-tabs .submenu-task{font-size:12px;font-weight:700;color:#344054;padding:0 10px 0 2px;border-right:1px solid #e4e7ec;margin-right:4px}.detail-tabs button.active{color:#17212b;border-bottom-color:#17212b}'
      output = output.replace('</style>', `${stylePatch}</style>`)

      return output === code ? null : { code: output, map: null }
    },
  }
}
