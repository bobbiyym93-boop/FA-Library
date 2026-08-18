<script setup>
defineProps({ activeView:{type:String,default:'cases'} })
const emit=defineEmits(['navigate'])
</script>

<template>
  <aside class="sidebar">
    <nav>
      <button class="nav-parent"><span>⌄</span><span>Library</span></button>
      <button class="nav-child" :class="{active:activeView==='cases'}" @click="emit('navigate','cases')">FA Library</button>
      <button class="nav-parent nav-section"><span>⌄</span><span>Engineering Tools</span></button>
      <button class="nav-child" :class="{active:activeView==='density'}" @click="emit('navigate','density')">GDS Density</button>
      <button class="nav-parent nav-section"><span>⌄</span><span>System Management</span></button>
      <button class="nav-child" :class="{active:activeView==='dictionary'}" @click="emit('navigate','dictionary')">Data Dictionary</button>
    </nav>
  </aside>
</template>
