<script setup>
import { computed } from 'vue'
const props = defineProps({ products: { type: Array, default: () => [] }, projects: { type: Array, default: () => [] } })
const colors = ['#387deb', '#4db88c', '#f5a33d', '#a673e5', '#e56b6f', '#45a9c7']
const total = computed(() => props.products.reduce((sum, item) => sum + item.value, 0))
const maximum = computed(() => Math.max(1, ...props.projects.map(item => item.value)))
const pieStyle = computed(() => {
  if (!total.value) return { background: '#edf0f5' }
  let cursor = 0
  return { background: `conic-gradient(${props.products.map((item, index) => { const start = cursor; cursor += item.value / total.value * 100; return `${colors[index % colors.length]} ${start}% ${cursor}%` }).join(',')})` }
})
</script>
<template>
  <section class="charts" aria-label="Dashboard charts">
    <article class="card product-chart"><h2>Product Distribution</h2><div class="product-chart-body"><div class="pie" :style="pieStyle"></div><ul class="legend"><li v-for="(item,index) in products" :key="item.name"><i :style="{background:colors[index % colors.length]}"></i><span>{{ item.name }}&nbsp;&nbsp;{{ item.value }} ({{ total ? Math.round(item.value / total * 100) : 0 }}%)</span></li><li v-if="!products.length" class="muted">暂无数据</li></ul></div></article>
    <article class="card bar-chart"><h2>Cases by Project</h2><span class="axis-title-y">Case count</span><div class="plot dynamic-plot"><div class="grid-line top"></div><div class="grid-line middle"></div><div class="grid-line bottom"></div><div v-for="item in projects" :key="item.name" class="bar-column"><div class="bar" :style="{height:`${Math.max(4,item.value / maximum * 86)}px`}" :title="`${item.name}: ${item.value}`"></div><span>{{ item.name }}</span></div><span v-if="!projects.length" class="chart-empty">暂无数据</span></div><span class="axis-title-x">Project</span></article>
  </section>
</template>
