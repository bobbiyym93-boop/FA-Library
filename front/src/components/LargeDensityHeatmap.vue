<script setup>
import * as echarts from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapContinuousComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

echarts.use([HeatmapChart,GridComponent,TooltipComponent,VisualMapContinuousComponent,CanvasRenderer])

const props=defineProps({
  layer:{type:String,required:true},
  seedKey:{type:[String,Number],required:true}
})

const chartEl=ref(null)
let chart
let resizeObserver

function hash(text){let value=2166136261;for(const char of String(text)){value^=char.charCodeAt(0);value=Math.imul(value,16777619)}return value>>>0}
function createPoints(){
  const columns=160,rows=100,seed=hash(`${props.seedKey}-${props.layer}`),points=[]
  const phaseX=(seed%97)/17,phaseY=(seed%71)/13
  for(let y=0;y<rows;y+=1){
    for(let x=0;x<columns;x+=1){
      const wave=Math.sin(x/13+phaseX)*.025+Math.cos(y/9+phaseY)*.021
      const radial=Math.exp(-(((x-(36+seed%80))**2)/900+((y-(24+seed%48))**2)/420))*.07
      const grain=(((Math.imul(x+11,73856093)^Math.imul(y+7,19349663)^seed)>>>0)%1000)/1000*.018
      const value=Math.max(.38,Math.min(.59,.445+wave+radial+grain))
      points.push([x,y,Number(value.toFixed(4))])
    }
  }
  return points
}

function renderChart(){
  if(!chartEl.value)return
  if(!chart)chart=echarts.init(chartEl.value,null,{renderer:'canvas'})
  chart.setOption({
    animation:false,
    grid:{top:12,right:24,bottom:54,left:52},
    tooltip:{trigger:'item',confine:true,formatter:params=>`<b>${props.layer}</b><br>X: ${params.value[0]}<br>Y: ${params.value[1]}<br>Density: ${params.value[2].toFixed(4)}`},
    xAxis:{type:'category',data:Array.from({length:160},(_,index)=>index),name:'X',nameLocation:'middle',nameGap:27,splitLine:{show:false},axisTick:{show:false},axisLine:{lineStyle:{color:'#98a2b3'}},axisLabel:{interval:29,color:'#667085',fontSize:10}},
    yAxis:{type:'category',data:Array.from({length:100},(_,index)=>index),name:'Y',nameLocation:'middle',nameGap:34,splitLine:{show:false},axisTick:{show:false},axisLine:{lineStyle:{color:'#98a2b3'}},axisLabel:{interval:19,color:'#667085',fontSize:10}},
    visualMap:{type:'continuous',min:.38,max:.59,dimension:2,orient:'horizontal',left:'center',bottom:3,itemWidth:12,itemHeight:180,text:['0.5900','0.3800'],textStyle:{color:'#667085',fontSize:10},calculable:false,inRange:{color:['#2456d6','#1da1f2','#31d3c5','#75df33','#f4df3d','#f28c28','#d83b3b']}},
    series:[{name:props.layer,type:'heatmap',data:createPoints(),progressive:0,animation:false,emphasis:{disabled:true},itemStyle:{borderWidth:0}}]
  },true)
}

onMounted(()=>{nextTick(renderChart);resizeObserver=new ResizeObserver(()=>chart?.resize());resizeObserver.observe(chartEl.value)})
watch(()=>[props.layer,props.seedKey],()=>nextTick(renderChart))
onBeforeUnmount(()=>{resizeObserver?.disconnect();chart?.dispose();chart=null})
</script>

<template><div ref="chartEl" class="large-density-heatmap" role="img" :aria-label="`${layer} Density Heatmap，包含 16000 个模拟点`"></div></template>

<style scoped>
.large-density-heatmap{width:100%;height:380px;min-height:320px}
@media(max-width:900px){.large-density-heatmap{height:330px}}
</style>
