<script setup>
import deleteIcon from '../assets/icon-delete.svg'
import editIcon from '../assets/icon-edit.svg'

const props = defineProps({ cases:{type:Array,default:()=>[]}, selected:{type:Array,default:()=>[]}, loading:Boolean, allSelected:Boolean, total:{type:Number,default:0}, currentPage:{type:Number,default:1}, totalPages:{type:Number,default:0}, pageNumbers:{type:Array,default:()=>[]} })
const emit = defineEmits(['update:selected','toggle-all','view','edit','delete','page'])
function toggleRow(id, checked) { emit('update:selected', checked ? [...new Set([...props.selected,id])] : props.selected.filter(item => item !== id)) }
</script>
<template>
  <section class="table-area"><div class="table-card"><div class="table-scroll"><table>
    <thead><tr><th class="check"><input type="checkbox" :checked="allSelected" @change="emit('toggle-all')" /></th><th>Case ID</th><th>Project</th><th>Product</th><th>Technology</th><th>Fail Type</th><th>Fail Model</th><th>Operation</th></tr></thead>
    <tbody><tr v-for="row in cases" :key="row.id"><td class="check"><input type="checkbox" :checked="selected.includes(row.id)" @change="toggleRow(row.id,$event.target.checked)" /></td><td><a href="#" @click.prevent="emit('view',row)">{{ row.case_id }}</a></td><td>{{ row.project }}</td><td>{{ row.product }}</td><td>{{ row.technology }}</td><td>{{ row.fail_type }}</td><td>{{ row.fail_model }}</td><td><div class="row-actions"><button title="删除" @click="emit('delete',row)"><img :src="deleteIcon" alt="删除" /></button><button title="编辑" @click="emit('edit',row)"><img :src="editIcon" alt="编辑" /></button></div></td></tr><tr v-if="loading"><td colspan="8" class="empty">正在加载…</td></tr><tr v-else-if="!cases.length"><td colspan="8" class="empty">暂无匹配数据</td></tr></tbody>
  </table></div></div><div class="pagination"><span>Total {{ total }}</span><button :disabled="currentPage===1" @click="emit('page',currentPage-1)">Prev</button><button v-for="page in pageNumbers" :key="page" :class="{current:currentPage===page}" @click="emit('page',page)">{{ page }}</button><button :disabled="currentPage>=totalPages" @click="emit('page',currentPage+1)">Next</button></div></section>
</template>
