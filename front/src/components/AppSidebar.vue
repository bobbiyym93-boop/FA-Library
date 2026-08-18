<script setup>
defineProps({ activeView:{type:String,default:'cases'}, collapsed:{type:Boolean,default:false} })
const emit=defineEmits(['navigate','toggle'])
</script>

<template>
  <aside class="sidebar" :class="{collapsed}">
    <button class="sidebar-toggle" :title="collapsed?'展开侧边栏':'收起侧边栏'" @click="emit('toggle')">
      <span>{{ collapsed ? '›' : '‹' }}</span><b v-if="!collapsed">收起</b>
    </button>
    <nav>
      <button class="nav-parent" :title="collapsed?'资料库':''"><span>⌄</span><span v-if="!collapsed">资料库</span></button>
      <button class="nav-child" :class="{active:activeView==='cases'}" :title="collapsed?'FA Library':''" @click="emit('navigate','cases')"><span v-if="collapsed">FA</span><span v-else>FA Library</span></button>
      <button class="nav-parent nav-section" :title="collapsed?'工程工具':''"><span>⌄</span><span v-if="!collapsed">工程工具</span></button>
      <button class="nav-child" :class="{active:activeView==='density'}" :title="collapsed?'GDS Density':''" @click="emit('navigate','density')"><span v-if="collapsed">GD</span><span v-else>GDS Density</span></button>
      <button class="nav-parent nav-section" :title="collapsed?'系统管理':''"><span>⌄</span><span v-if="!collapsed">系统管理</span></button>
      <button class="nav-child" :class="{active:activeView==='dictionary'}" :title="collapsed?'数据字典':''" @click="emit('navigate','dictionary')"><span v-if="collapsed">字</span><span v-else>数据字典</span></button>
    </nav>
  </aside>
</template>
