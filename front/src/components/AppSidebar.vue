<script setup>
defineProps({ activeView:{type:String,default:'cases'} })
const emit=defineEmits(['navigate'])
</script>

<template>
  <aside class="sidebar">
    <nav>
      <button class="nav-parent"><span>⌄</span><span>Library</span></button>
      <button class="nav-child" :class="{active:activeView==='cases'}" @click="emit('navigate','cases')">FA Library</button>
      <button class="nav-parent nav-section"><span>⌄</span><span>工程工具</span></button>
      <button class="nav-child" :class="{active:activeView==='density'}" @click="emit('navigate','density')">GDS Density</button>
      <button class="nav-parent nav-section"><span>⌄</span><span>系统管理</span></button>
      <button class="nav-child" :class="{active:activeView==='dictionary'}" @click="emit('navigate','dictionary')">数据字典</button>
    </nav>
  </aside>
</template>
