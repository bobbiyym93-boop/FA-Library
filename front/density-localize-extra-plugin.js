const replacements = [
  ['Analysis completed · PASS', '分析完成 · 通过'],
  ['Analysis completed · REVIEW', '分析完成 · 需检查'],
  ['Current analysis added to local history view', '当前分析已加入本地历史记录'],
  ['No matching FA records', '未找到匹配的 FA 记录'],
  ['XML config exported', 'XML 配置已导出'],
  ['Config error:', '配置错误：'],
  ['FA query failed:', 'FA 查询失败：'],
  ['analysis queued for layer', '已提交分析任务，layer'],
  ['unknown command:', '未知命令：'],
  ['unknown key', '未知参数'],
  ["'PASS'", "'通过'"],
  ["'FAIL'", "'失败'"],
  ["'REVIEW'", "'需检查'"],
  ["'Matched'", "'匹配'"],
  ["'Review'", "'需检查'"],
  ["'Uniform'", "'均匀'"],
  ["'Non-uniform'", "'不均匀'"],
]

export function densityChineseExtraPlugin() {
  return {
    name: 'density-chinese-dynamic-localization',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/components/DensityAnalysisView.vue')) return null
      let output = code
      for (const [from, to] of replacements) output = output.split(from).join(to)
      output = output
        .replace(/\$\{file\.name\} loaded/g, '${file.name} 已加载')
        .replace(/\$\{file\.name\} config loaded/g, '${file.name} 配置已加载')
        .replace(/Found \$\{faRows\.value\.length\} FA records/g, '找到 ${faRows.value.length} 条 FA 记录')
        .replace(/\$\{faRows\.value\.length\} FA records matched/g, '${faRows.value.length} 条 FA 记录匹配')
      return { code: output, map: null }
    },
  }
}
