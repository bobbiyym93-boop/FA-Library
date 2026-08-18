<script setup>
import * as echarts from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapPiecewiseComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

echarts.use([HeatmapChart,GridComponent,TooltipComponent,VisualMapPiecewiseComponent,CanvasRenderer])

const props=defineProps({layer:{type:String,required:true},seedKey:{type:[String,Number],required:true},negativeSpec:{type:Number,required:true},positiveSpec:{type:Number,required:true}})
const chartEl=ref(null)
let chart,resizeObserver

function hash(text){let value=2166136261;for(const char of String(text)){value^=char.charCodeAt(0);value=Math.imul(value,16777619)}return value>>>0}
function createPoints(){const columns=160,rows=100,seed=hash(`${props.seedKey}-${props.layer}-gradient`),points=[];for(let y=0;y<rows;y+=1){for(let x=0;x<columns;x+=1){const wave=Math.sin((x+seed%31)/11)*.035+Math.cos((y+seed%23)/8)*.028,hotspot=Math.exp(-(((x-(45+seed%70))**2)/700+((y-(25+seed%50))**2)/340))*.075,grain=((((Math.imul(x+3,73856093)^Math.imul(y+5,19349663)^seed)>>>0)%1000)/1000-.5)*.018,value=Math.max(-.14,Math.min(.14,wave+hotspot+grain-.018));points.push([x,y,Number(value.toFixed(4))])}}return points}
function renderChart(){if(!chartEl.value)return;if(!chart)chart=echarts.init(chartEl.value,null,{renderer:'canvas'});const neutral=Math.min(Math.abs(props.negativeSpec),Math.abs(props.positiveSpec))*.25,negativeNeutral=-neutral,positiveNeutral=neutral;chart.setOption({animation:false,grid:{top:12,right:24,bottom:74,left:52},tooltip:{trigger:'item',confine:true,formatter:params=>`<b>${props.layer}</b><br>X: ${params.value[0]}<br>Y: ${params.value[1]}<br>Gradient: ${params.value[2].toFixed(4)}`},xAxis:{type:'category',data:Array.from({length:160},(_,index)=>index),name:'X',nameLocation:'middle',nameGap:27,splitLine:{show:false},axisTick:{show:false},axisLine:{lineStyle:{color:'#98a2b3'}},axisLabel:{interval:29,color:'#667085',fontSize:10}},yAxis:{type:'category',data:Array.from({length:100},(_,index)=>index),name:'Y',nameLocation:'middle',nameGap:34,splitLine:{show:false},axisTick:{show:false},axisLine:{lineStyle:{color:'#98a2b3'}},axisLabel:{interval:19,color:'#667085',fontSize:10}},visualMap:{type:'piecewise',dimension:2,orient:'horizontal',left:'center',bottom:4,itemWidth:14,itemHeight:20,textStyle:{color:'#667085',fontSize:10},pieces:[{lte:props.negativeSpec,label:`≤ ${props.negativeSpec.toFixed(3)}`,color:'#244cc8'},{gt:props.negativeSpec,lte:negativeNeutral,label:`(${props.negativeSpec.toFixed(3)}, ${negativeNeutral.toFixed(3)}]`,color:'#38a8df'},{gt:negativeNeutral,lte:positiveNeutral,label:`(${negativeNeutral.toFixed(3)}, ${positiveNeutral.toFixed(3)}]`,color:'#e8eef5'},{gt:positiveNeutral,lt:props.positiveSpec,label:`(${positiveNeutral.toFixed(3)}, ${props.positiveSpec.toFixed(3)})`,color:'#f4a340'},{gte:props.positiveSpec,label:`≥ ${props.positiveSpec.toFixed(3)}`,color:'#d83b3b'}]},series:[{name:`${props.layer} gradient`,type:'heatmap',data:createPoints(),progressive:0,animation:false,emphasis:{disabled:true},itemStyle:{borderWidth:0}}]},true)}
onMounted(()=>{nextTick(renderChart);resizeObserver=new ResizeObserver(()=>chart?.resize());resizeObserver.observe(chartEl.value)})
watch(()=>[props.layer,props.seedKey,props.negativeSpec,props.positiveSpec],()=>nextTick(renderChart))
onBeforeUnmount(()=>{resizeObserver?.disconnect();chart?.dispose();chart=null})
</script>

<template><div ref="chartEl" class="large-gradient-heatmap" role="img" :aria-label="`${layer} Density Gradient Heatmap`"></div></template>

<style scoped>.large-gradient-heatmap{width:100%;height:380px;min-height:320px}@media(max-width:900px){.large-gradient-heatmap{height:330px}}</style>
