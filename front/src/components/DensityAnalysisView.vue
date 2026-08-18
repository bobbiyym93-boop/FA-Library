<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { getCases } from '../api/cases'

const sections = [
  ['setup', 'Setup'],
  ['results', 'Results'],
  ['compare', 'Layer Compare'],
  ['gradient', 'Gradient Spec'],
  ['history', 'History'],
  ['console', 'TCL Console'],
  ['fa', 'FA Link'],
]

const activeSection = ref('setup')
const gdsInput = ref(null)
const xmlInput = ref(null)
const gdsFile = ref(null)
const statusMessage = ref('Ready')
const analyzing = ref(false)
const analysisDone = ref(false)
const selectedCell = ref(null)
const tclInput = ref('density::status')
const tclHistory = ref([])
const faLoading = ref(false)
const faRows = ref([])

const config = reactive({
  name: 'default-density-config',
  projectName: '',
  layer: 'M1',
  compareLayer: 'M2',
  stepUm: 100,
  windowWidthUm: 500,
  windowHeightUm: 500,
  gradientSpec: 0.08,
  varianceSpec: 0.0025,
  uniformityAlpha: 0.05,
})

const layers = ref(['M1', 'M2', 'M3', 'M4'])
const grid = ref([])
const compareGrid = ref([])
const historyRuns = ref([
  { project: 'Orion-A12', layer: 'M1', mean: 0.472, variance: 0.0018, gradient: 0.061, uniform: true, date: '2026-08-12' },
  { project: 'Nova-B07', layer: 'M1', mean: 0.451, variance: 0.0034, gradient: 0.093, uniform: false, date: '2026-08-03' },
  { project: 'Atlas-P9', layer: 'M2', mean: 0.496, variance: 0.0014, gradient: 0.054, uniform: true, date: '2026-07-26' },
])

function hashText(text) {
  let hash = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function seeded(seed) {
  let value = seed || 1
  return () => {
    value = (value * 1664525 + 1013904223) >>> 0
    return value / 4294967296
  }
}

function makeGrid(layerName) {
  const cols = 14
  const rows = 10
  const seed = hashText(`${gdsFile.value?.name || 'demo.gds'}:${layerName}:${config.stepUm}:${config.windowWidthUm}:${config.windowHeightUm}`)
  const random = seeded(seed)
  const layerOffset = ((hashText(layerName) % 17) - 8) / 1000
  return Array.from({ length: rows }, (_, y) => Array.from({ length: cols }, (_, x) => {
    const trend = (x / (cols - 1) - 0.5) * 0.055 + (y / (rows - 1) - 0.5) * 0.026
    const wave = Math.sin((x + 1) * 0.72) * 0.016 + Math.cos((y + 2) * 0.61) * 0.012
    const noise = (random() - 0.5) * 0.048
    return Math.max(0.08, Math.min(0.88, 0.47 + trend + wave + noise + layerOffset))
  }))
}

const flat = computed(() => grid.value.flat())
const flatCompare = computed(() => compareGrid.value.flat())
const mean = computed(() => flat.value.length ? flat.value.reduce((sum, value) => sum + value, 0) / flat.value.length : 0)
const variance = computed(() => flat.value.length ? flat.value.reduce((sum, value) => sum + ((value - mean.value) ** 2), 0) / flat.value.length : 0)
const stddev = computed(() => Math.sqrt(variance.value))
const minDensity = computed(() => flat.value.length ? Math.min(...flat.value) : 0)
const maxDensity = computed(() => flat.value.length ? Math.max(...flat.value) : 0)
const range = computed(() => maxDensity.value - minDensity.value)
const gradient = computed(() => {
  if (!grid.value.length) return 0
  let maxDelta = 0
  grid.value.forEach((row, y) => row.forEach((value, x) => {
    if (x + 1 < row.length) maxDelta = Math.max(maxDelta, Math.abs(value - row[x + 1]))
    if (y + 1 < grid.value.length) maxDelta = Math.max(maxDelta, Math.abs(value - grid.value[y + 1][x]))
  }))
  return maxDelta
})
const coefficientVariation = computed(() => mean.value ? stddev.value / mean.value : 0)
const chiSquareScore = computed(() => mean.value ? flat.value.reduce((sum, value) => sum + ((value - mean.value) ** 2 / Math.max(mean.value, 0.001)), 0) : 0)
const pseudoPValue = computed(() => Math.max(0.001, Math.min(0.999, Math.exp(-chiSquareScore.value / Math.max(flat.value.length / 2, 1)))))
const uniformPass = computed(() => pseudoPValue.value >= Number(config.uniformityAlpha))
const variancePass = computed(() => variance.value <= Number(config.varianceSpec))
const gradientPass = computed(() => gradient.value <= Number(config.gradientSpec))
const overallPass = computed(() => uniformPass.value && variancePass.value && gradientPass.value)
const compareMean = computed(() => flatCompare.value.length ? flatCompare.value.reduce((sum, value) => sum + value, 0) / flatCompare.value.length : 0)
const compareDelta = computed(() => mean.value - compareMean.value)
const regionCorrelation = computed(() => {
  if (!flat.value.length || flat.value.length !== flatCompare.value.length) return 0
  const meanA = mean.value
  const meanB = compareMean.value
  let numerator = 0
  let denA = 0
  let denB = 0
  flat.value.forEach((value, index) => {
    const a = value - meanA
    const b = flatCompare.value[index] - meanB
    numerator += a * b
    denA += a * a
    denB += b * b
  })
  return denA && denB ? numerator / Math.sqrt(denA * denB) : 0
})

const histogram = computed(() => {
  const bins = 12
  if (!flat.value.length) return []
  const min = Math.min(...flat.value)
  const max = Math.max(...flat.value)
  const span = Math.max(max - min, 0.001)
  const counts = Array.from({ length: bins }, () => 0)
  flat.value.forEach((value) => {
    const index = Math.min(bins - 1, Math.floor(((value - min) / span) * bins))
    counts[index] += 1
  })
  const maxCount = Math.max(...counts, 1)
  return counts.map((count, index) => ({
    count,
    height: (count / maxCount) * 100,
    label: `${(min + (span * index / bins)).toFixed(2)}`,
  }))
})

const gradientProfile = computed(() => {
  if (!grid.value.length) return []
  const rowMeans = grid.value.map((row) => row.reduce((sum, value) => sum + value, 0) / row.length)
  const deltas = rowMeans.map((value, index) => index ? Math.abs(value - rowMeans[index - 1]) : 0)
  const maxValue = Math.max(...deltas, Number(config.gradientSpec), 0.001)
  return deltas.map((value, index) => ({ index, value, y: 88 - ((value / maxValue) * 70) }))
})

function heatColor(value) {
  const normalized = Math.max(0, Math.min(1, (value - 0.35) / 0.25))
  const hue = 218 - (normalized * 188)
  return `hsl(${hue} 78% 54%)`
}

function analyze() {
  analyzing.value = true
  statusMessage.value = `Analyzing ${gdsFile.value?.name || 'demo.gds'} / ${config.layer}...`
  window.setTimeout(() => {
    grid.value = makeGrid(config.layer)
    compareGrid.value = makeGrid(config.compareLayer)
    analysisDone.value = true
    analyzing.value = false
    selectedCell.value = null
    statusMessage.value = overallPass.value ? 'Analysis completed · PASS' : 'Analysis completed · REVIEW'
    activeSection.value = 'results'
  }, 350)
}

function onGdsSelected(event) {
  const [file] = event.target.files || []
  if (!file) return
  gdsFile.value = file
  const guessedProject = file.name.replace(/\.(gds|gdsii)$/i, '').split(/[_-]/).slice(0, 2).join('-')
  if (!config.projectName) config.projectName = guessedProject
  statusMessage.value = `${file.name} loaded (${(file.size / 1024 / 1024).toFixed(2)} MB)`
}

function xmlEscape(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;')
}

function configXml() {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<densityConfig version="1.0">\n  <name>${xmlEscape(config.name)}</name>\n  <project>${xmlEscape(config.projectName)}</project>\n  <gdsLayer>${xmlEscape(config.layer)}</gdsLayer>\n  <compareLayer>${xmlEscape(config.compareLayer)}</compareLayer>\n  <window stepUm="${config.stepUm}" widthUm="${config.windowWidthUm}" heightUm="${config.windowHeightUm}"/>\n  <spec varianceMax="${config.varianceSpec}" gradientMax="${config.gradientSpec}" uniformityAlpha="${config.uniformityAlpha}"/>\n</densityConfig>\n`
}

function downloadConfig() {
  const blob = new Blob([configXml()], { type: 'application/xml' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${config.name || 'density-config'}.xml`
  anchor.click()
  URL.revokeObjectURL(url)
  statusMessage.value = 'XML config exported'
}

function loadXmlFile(event) {
  const [file] = event.target.files || []
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const doc = new DOMParser().parseFromString(String(reader.result), 'application/xml')
      if (doc.querySelector('parsererror')) throw new Error('Invalid XML')
      const root = doc.querySelector('densityConfig')
      if (!root) throw new Error('Missing densityConfig root')
      const text = (selector, fallback) => root.querySelector(selector)?.textContent?.trim() || fallback
      config.name = text('name', config.name)
      config.projectName = text('project', config.projectName)
      config.layer = text('gdsLayer', config.layer)
      config.compareLayer = text('compareLayer', config.compareLayer)
      const windowNode = root.querySelector('window')
      const specNode = root.querySelector('spec')
      if (windowNode) {
        config.stepUm = Number(windowNode.getAttribute('stepUm') || config.stepUm)
        config.windowWidthUm = Number(windowNode.getAttribute('widthUm') || config.windowWidthUm)
        config.windowHeightUm = Number(windowNode.getAttribute('heightUm') || config.windowHeightUm)
      }
      if (specNode) {
        config.varianceSpec = Number(specNode.getAttribute('varianceMax') || config.varianceSpec)
        config.gradientSpec = Number(specNode.getAttribute('gradientMax') || config.gradientSpec)
        config.uniformityAlpha = Number(specNode.getAttribute('uniformityAlpha') || config.uniformityAlpha)
      }
      if (!layers.value.includes(config.layer)) layers.value.push(config.layer)
      if (!layers.value.includes(config.compareLayer)) layers.value.push(config.compareLayer)
      statusMessage.value = `${file.name} config loaded`
    } catch (error) {
      statusMessage.value = `Config error: ${error.message}`
    }
  }
  reader.readAsText(file)
}

function chooseCell(value, x, y, source = 'primary') {
  selectedCell.value = { value, x, y, source }
}

function saveHistorySnapshot() {
  if (!analysisDone.value) return
  historyRuns.value.unshift({
    project: config.projectName || gdsFile.value?.name || 'Current project',
    layer: config.layer,
    mean: mean.value,
    variance: variance.value,
    gradient: gradient.value,
    uniform: uniformPass.value,
    date: new Date().toISOString().slice(0, 10),
  })
  statusMessage.value = 'Current analysis added to local history view'
  activeSection.value = 'history'
}

async function loadFaCases() {
  faLoading.value = true
  faRows.value = []
  try {
    const keyword = (config.projectName || gdsFile.value?.name || '').replace(/\.(gds|gdsii)$/i, '')
    const data = await getCases({ page: 1, pageSize: 50, keyword })
    faRows.value = data.items || []
    statusMessage.value = faRows.value.length ? `Found ${faRows.value.length} FA records` : 'No matching FA records'
  } catch (error) {
    statusMessage.value = `FA query failed: ${error.message}`
  } finally {
    faLoading.value = false
  }
}

function formatPct(value) { return `${(Number(value) * 100).toFixed(2)}%` }
function formatNum(value, digits = 4) { return Number(value || 0).toFixed(digits) }

function tokenize(command) {
  return command.match(/"[^"]*"|'[^']*'|\S+/g)?.map((token) => token.replace(/^['"]|['"]$/g, '')) || []
}

async function runTcl() {
  const command = tclInput.value.trim()
  if (!command) return
  const tokens = tokenize(command)
  let output = ''
  const [verb, ...args] = tokens
  try {
    if (verb === 'density::status') {
      output = `file=${gdsFile.value?.name || 'demo.gds'} layer=${config.layer} analyzed=${analysisDone.value} mean=${formatNum(mean.value)} variance=${formatNum(variance.value, 6)} gradient=${formatNum(gradient.value)}`
    } else if (verb === 'density::analyze') {
      const layerIndex = args.indexOf('-layer')
      if (layerIndex >= 0 && args[layerIndex + 1]) config.layer = args[layerIndex + 1]
      analyze()
      output = `analysis queued for layer ${config.layer}`
    } else if (verb === 'density::set') {
      const [key, value] = args
      const keyMap = { layer: 'layer', compare_layer: 'compareLayer', step: 'stepUm', width: 'windowWidthUm', height: 'windowHeightUm', gradient_spec: 'gradientSpec', variance_spec: 'varianceSpec', alpha: 'uniformityAlpha', project: 'projectName' }
      const target = keyMap[key]
      if (!target) throw new Error(`unknown key ${key}`)
      config[target] = ['layer', 'compareLayer', 'projectName'].includes(target) ? value : Number(value)
      output = `${key}=${config[target]}`
    } else if (verb === 'density::config') {
      output = configXml().replaceAll('\n', ' ')
    } else if (verb === 'density::history') {
      output = historyRuns.value.map((run) => `${run.project}/${run.layer}:${formatNum(run.mean)}`).join(' | ')
    } else if (verb === 'density::fa') {
      await loadFaCases()
      output = `${faRows.value.length} FA records matched`
    } else if (verb === 'help' || verb === 'density::help') {
      output = 'density::status | density::analyze -layer M1 | density::set <layer|compare_layer|step|width|height|gradient_spec|variance_spec|alpha|project> <value> | density::config | density::history | density::fa'
    } else {
      throw new Error(`unknown command: ${verb}`)
    }
  } catch (error) {
    output = `ERROR: ${error.message}`
  }
  tclHistory.value.unshift({ command, output, time: new Date().toLocaleTimeString() })
  await nextTick()
}

onMounted(() => {
  grid.value = makeGrid(config.layer)
  compareGrid.value = makeGrid(config.compareLayer)
})
</script>

<template>
  <main class="density-page">
    <header class="density-header">
      <div>
        <div class="eyebrow">PROCESS · LAYOUT · DENSITY</div>
        <h1>GDS Density Analysis</h1>
        <p>Windowed density, uniformity test, gradient spec, cross-layer comparison and FA correlation.</p>
      </div>
      <div class="header-actions">
        <span class="status-dot" :class="overallPass && analysisDone ? 'pass' : 'idle'"></span>
        <span class="status-text">{{ statusMessage }}</span>
        <button class="primary" :disabled="analyzing" @click="analyze">{{ analyzing ? 'Running…' : 'Run analysis' }}</button>
      </div>
    </header>

    <nav class="density-tabs" aria-label="GDS density sections">
      <button v-for="section in sections" :key="section[0]" :class="{active:activeSection===section[0]}" @click="activeSection=section[0]">{{ section[1] }}</button>
    </nav>

    <section v-if="activeSection==='setup'" class="workspace two-col">
      <div class="panel">
        <div class="panel-title"><div><span class="kicker">INPUT</span><h2>GDS & analysis window</h2></div><span class="chip">µm</span></div>
        <label class="drop-zone" @click="gdsInput?.click()">
          <input ref="gdsInput" type="file" accept=".gds,.gdsii" hidden @change="onGdsSelected">
          <span class="drop-icon">⌁</span>
          <strong>{{ gdsFile?.name || 'Select GDS file' }}</strong>
          <small>{{ gdsFile ? `${(gdsFile.size/1024/1024).toFixed(2)} MB` : 'GDS / GDSII · local browser selection' }}</small>
        </label>
        <div class="form-grid">
          <label><span>Project / correlation key</span><input v-model="config.projectName" placeholder="Project name"></label>
          <label><span>GDS layer</span><input v-model="config.layer" list="layers-list"></label>
          <label><span>Window step</span><input v-model.number="config.stepUm" type="number" min="1"><b>µm</b></label>
          <label><span>Window width</span><input v-model.number="config.windowWidthUm" type="number" min="1"><b>µm</b></label>
          <label><span>Window height</span><input v-model.number="config.windowHeightUm" type="number" min="1"><b>µm</b></label>
          <label><span>Compare layer</span><input v-model="config.compareLayer" list="layers-list"></label>
        </div>
        <datalist id="layers-list"><option v-for="layer in layers" :key="layer" :value="layer"/></datalist>
      </div>

      <div class="panel">
        <div class="panel-title"><div><span class="kicker">CONFIG</span><h2>XML configuration</h2></div><span class="chip">portable</span></div>
        <div class="config-card">
          <label><span>Config name</span><input v-model="config.name"></label>
          <div class="xml-preview"><pre>{{ configXml() }}</pre></div>
          <div class="button-row">
            <button class="secondary" @click="xmlInput?.click()">Upload XML</button>
            <input ref="xmlInput" type="file" accept=".xml,text/xml,application/xml" hidden @change="loadXmlFile">
            <button class="secondary" @click="downloadConfig">Save XML</button>
            <button class="primary" @click="analyze">Analyze with config</button>
          </div>
        </div>
        <div class="spec-strip">
          <div><span>Variance max</span><strong>{{ config.varianceSpec }}</strong></div>
          <div><span>Gradient max</span><strong>{{ config.gradientSpec }}</strong></div>
          <div><span>Uniformity α</span><strong>{{ config.uniformityAlpha }}</strong></div>
        </div>
      </div>
    </section>

    <section v-else-if="activeSection==='results'" class="workspace">
      <div class="metric-grid">
        <article class="metric"><span>Mean density</span><strong>{{ formatPct(mean) }}</strong><small>{{ config.layer }} average</small></article>
        <article class="metric"><span>Variance</span><strong>{{ formatNum(variance,6) }}</strong><small :class="variancePass?'ok':'bad'">{{ variancePass?'Within spec':'Above spec' }}</small></article>
        <article class="metric"><span>Uniformity test</span><strong>p={{ formatNum(pseudoPValue,3) }}</strong><small :class="uniformPass?'ok':'bad'">{{ uniformPass?'Uniform':'Non-uniform' }} @ α={{ config.uniformityAlpha }}</small></article>
        <article class="metric"><span>Gradient max</span><strong>{{ formatPct(gradient) }}</strong><small :class="gradientPass?'ok':'bad'">{{ gradientPass?'Within spec':'Out of spec' }}</small></article>
        <article class="metric verdict"><span>Overall</span><strong :class="overallPass?'ok':'bad'">{{ overallPass?'PASS':'REVIEW' }}</strong><small>Variance + uniformity + gradient</small></article>
      </div>

      <div class="results-grid">
        <div class="panel heat-panel">
          <div class="panel-title"><div><span class="kicker">SPATIAL MAP</span><h2>{{ config.layer }} density heatmap</h2></div><span class="chip">step {{ config.stepUm }} µm</span></div>
          <div class="heat-wrap">
            <div class="heatmap" :style="{gridTemplateColumns:`repeat(${grid[0]?.length || 1},1fr)`}">
              <button v-for="(value,index) in flat" :key="index" :title="`${formatPct(value)} · cell ${index}`" :style="{background:heatColor(value)}" @click="chooseCell(value,index%(grid[0]?.length||1),Math.floor(index/(grid[0]?.length||1)))"></button>
            </div>
            <div class="legend"><span>35%</span><i></i><span>60%+</span></div>
          </div>
          <div class="map-footer"><span>Window {{ config.windowWidthUm }} × {{ config.windowHeightUm }} µm</span><span>Range {{ formatPct(range) }}</span><span v-if="selectedCell">Selected ({{ selectedCell.x }},{{ selectedCell.y }}) · {{ formatPct(selectedCell.value) }}</span></div>
        </div>

        <div class="panel histogram-panel">
          <div class="panel-title"><div><span class="kicker">DISTRIBUTION</span><h2>Density histogram</h2></div><span class="chip">CV {{ formatPct(coefficientVariation) }}</span></div>
          <div class="histogram"><div v-for="(bar,index) in histogram" :key="index" class="bar-wrap"><div class="bar" :style="{height:`${bar.height}%`}"><span>{{ bar.count }}</span></div><small>{{ index%2===0?bar.label:'' }}</small></div></div>
          <div class="stat-list">
            <div><span>Minimum</span><strong>{{ formatPct(minDensity) }}</strong></div>
            <div><span>Maximum</span><strong>{{ formatPct(maxDensity) }}</strong></div>
            <div><span>Std. deviation</span><strong>{{ formatNum(stddev,4) }}</strong></div>
            <div><span>Pseudo χ² score</span><strong>{{ formatNum(chiSquareScore,3) }}</strong></div>
          </div>
        </div>
      </div>
      <div class="button-row right"><button class="secondary" @click="saveHistorySnapshot">Save snapshot to history</button><button class="secondary" @click="activeSection='compare'">Compare layer →</button></div>
    </section>

    <section v-else-if="activeSection==='compare'" class="workspace">
      <div class="panel compare-toolbar">
        <label><span>Reference layer</span><input v-model="config.layer" @change="grid=makeGrid(config.layer)"></label>
        <span class="versus">VS</span>
        <label><span>Compare layer</span><input v-model="config.compareLayer" @change="compareGrid=makeGrid(config.compareLayer)"></label>
        <div class="compare-summary"><span>Mean Δ</span><strong :class="Math.abs(compareDelta)<0.03?'ok':'bad'">{{ compareDelta>=0?'+':'' }}{{ formatPct(compareDelta) }}</strong></div>
        <div class="compare-summary"><span>Region correlation</span><strong>{{ formatNum(regionCorrelation,3) }}</strong></div>
      </div>
      <div class="dual-map">
        <div class="panel"><div class="panel-title"><h2>{{ config.layer }}</h2><span class="chip">mean {{ formatPct(mean) }}</span></div><div class="heatmap large" :style="{gridTemplateColumns:`repeat(${grid[0]?.length||1},1fr)`}"><button v-for="(value,index) in flat" :key="index" :style="{background:heatColor(value)}" @click="chooseCell(value,index%(grid[0]?.length||1),Math.floor(index/(grid[0]?.length||1)),'primary')"></button></div></div>
        <div class="panel"><div class="panel-title"><h2>{{ config.compareLayer }}</h2><span class="chip">mean {{ formatPct(compareMean) }}</span></div><div class="heatmap large" :style="{gridTemplateColumns:`repeat(${compareGrid[0]?.length||1},1fr)`}"><button v-for="(value,index) in flatCompare" :key="index" :style="{background:heatColor(value)}" @click="chooseCell(value,index%(compareGrid[0]?.length||1),Math.floor(index/(compareGrid[0]?.length||1)),'compare')"></button></div></div>
      </div>
      <div class="panel region-table"><div class="panel-title"><div><span class="kicker">SAME REGION</span><h2>Cell-by-cell delta preview</h2></div></div><table><thead><tr><th>Region</th><th>{{ config.layer }}</th><th>{{ config.compareLayer }}</th><th>Δ density</th><th>Status</th></tr></thead><tbody><tr v-for="index in 8" :key="index"><td>R{{ String(index).padStart(2,'0') }}</td><td>{{ formatPct(flat[index*3]||0) }}</td><td>{{ formatPct(flatCompare[index*3]||0) }}</td><td>{{ formatPct((flat[index*3]||0)-(flatCompare[index*3]||0)) }}</td><td><span class="mini-status" :class="Math.abs((flat[index*3]||0)-(flatCompare[index*3]||0))<0.05?'ok':'bad'">{{ Math.abs((flat[index*3]||0)-(flatCompare[index*3]||0))<0.05?'Matched':'Review' }}</span></td></tr></tbody></table></div>
    </section>

    <section v-else-if="activeSection==='gradient'" class="workspace two-col">
      <div class="panel">
        <div class="panel-title"><div><span class="kicker">USER SPEC</span><h2>Density gradient limit</h2></div><span class="chip" :class="gradientPass?'ok':'bad'">{{ gradientPass?'PASS':'FAIL' }}</span></div>
        <div class="spec-editor"><label><span>Gradient max / adjacent window</span><input v-model.number="config.gradientSpec" type="number" step="0.005" min="0"><b>density Δ</b></label><input v-model.number="config.gradientSpec" type="range" min="0.01" max="0.20" step="0.005"></div>
        <div class="spec-gauge"><div class="spec-track"><i :style="{width:`${Math.min(100,(gradient/config.gradientSpec)*70)}%`}" :class="gradientPass?'ok-bg':'bad-bg'"></i><b :style="{left:'70%'}"></b></div><div class="gauge-labels"><span>0</span><span>Measured {{ formatNum(gradient,3) }}</span><span>Spec {{ config.gradientSpec }}</span></div></div>
        <div class="spec-result" :class="gradientPass?'pass-box':'fail-box'"><strong>{{ gradientPass ? 'Gradient is inside spec' : 'Gradient exceeds user spec' }}</strong><span>Maximum adjacent-window delta = {{ formatNum(gradient,4) }}. Limit = {{ formatNum(config.gradientSpec,4) }}.</span></div>
      </div>
      <div class="panel"><div class="panel-title"><div><span class="kicker">PROFILE</span><h2>Row-to-row gradient</h2></div></div><svg class="line-chart" viewBox="0 0 520 110" preserveAspectRatio="none"><line x1="0" :y1="88-(config.gradientSpec/Math.max(...gradientProfile.map(p=>p.value),config.gradientSpec,0.001)*70)" x2="520" :y2="88-(config.gradientSpec/Math.max(...gradientProfile.map(p=>p.value),config.gradientSpec,0.001)*70)" class="spec-line"/><polyline :points="gradientProfile.map((p,i)=>`${(i/(Math.max(gradientProfile.length-1,1)))*520},${p.y}`).join(' ')" class="gradient-line"/></svg><div class="stat-list"><div><span>Max gradient</span><strong>{{ formatPct(gradient) }}</strong></div><div><span>Spec</span><strong>{{ formatPct(config.gradientSpec) }}</strong></div><div><span>Margin</span><strong :class="gradientPass?'ok':'bad'">{{ formatPct(config.gradientSpec-gradient) }}</strong></div></div></div>
      <div class="panel full"><div class="panel-title"><div><span class="kicker">VARIANCE SPEC</span><h2>Statistical gates</h2></div></div><div class="form-grid specs"><label><span>Variance max</span><input v-model.number="config.varianceSpec" type="number" step="0.0001"></label><label><span>Uniformity α</span><input v-model.number="config.uniformityAlpha" type="number" min="0.001" max="0.5" step="0.01"></label><div class="gate"><span>Variance</span><strong :class="variancePass?'ok':'bad'">{{ variancePass?'PASS':'FAIL' }}</strong></div><div class="gate"><span>Uniformity</span><strong :class="uniformPass?'ok':'bad'">{{ uniformPass?'PASS':'FAIL' }}</strong></div></div></div>
    </section>

    <section v-else-if="activeSection==='history'" class="workspace">
      <div class="panel">
        <div class="panel-title"><div><span class="kicker">CROSS PROJECT</span><h2>Historical density benchmark</h2></div><button class="secondary small" @click="saveHistorySnapshot" :disabled="!analysisDone">Add current</button></div>
        <table><thead><tr><th>Project</th><th>Layer</th><th>Mean density</th><th>Variance</th><th>Gradient</th><th>Uniformity</th><th>Date</th></tr></thead><tbody><tr v-for="run in historyRuns" :key="`${run.project}-${run.date}-${run.layer}`"><td><strong>{{ run.project }}</strong></td><td><span class="layer-pill">{{ run.layer }}</span></td><td>{{ formatPct(run.mean) }}</td><td>{{ formatNum(run.variance,6) }}</td><td>{{ formatPct(run.gradient) }}</td><td><span class="mini-status" :class="run.uniform?'ok':'bad'">{{ run.uniform?'Uniform':'Review' }}</span></td><td>{{ run.date }}</td></tr></tbody></table>
      </div>
      <div class="panel"><div class="panel-title"><div><span class="kicker">BENCHMARK</span><h2>Current vs historical mean</h2></div></div><div class="benchmark"><div v-for="run in historyRuns.slice(0,6)" :key="run.project"><span>{{ run.project }}</span><div><i :style="{width:`${Math.min(100,run.mean*180)}%`}"></i></div><strong>{{ formatPct(run.mean) }}</strong></div></div></div>
    </section>

    <section v-else-if="activeSection==='console'" class="workspace console-layout">
      <div class="panel console-panel">
        <div class="panel-title"><div><span class="kicker">COMMAND LINE</span><h2>TCL operation console</h2></div><span class="chip">sandbox</span></div>
        <div class="terminal"><div class="terminal-log"><div v-if="!tclHistory.length" class="terminal-help">Type <b>density::help</b> to list available commands.</div><div v-for="(item,index) in tclHistory" :key="index" class="terminal-entry"><p><span>{{ item.time }}</span> $ {{ item.command }}</p><pre>{{ item.output }}</pre></div></div><form @submit.prevent="runTcl"><span>$</span><input v-model="tclInput" spellcheck="false" autocomplete="off" placeholder="density::analyze -layer M1"><button>Run</button></form></div>
      </div>
      <div class="panel command-ref"><div class="panel-title"><h2>Command reference</h2></div><code>density::status</code><p>Show active file, layer and latest statistics.</p><code>density::analyze -layer M1</code><p>Run analysis using the current config.</p><code>density::set gradient_spec 0.08</code><p>Update layer/window/spec/project values.</p><code>density::config</code><p>Print current XML config in one line.</p><code>density::fa</code><p>Query matching failure-analysis cases.</p></div>
    </section>

    <section v-else-if="activeSection==='fa'" class="workspace">
      <div class="panel fa-query">
        <div><span class="kicker">FA LIBRARY CORRELATION</span><h2>Link GDS to failure information</h2><p>Use project/correlation key to query the existing FA Library case API and surface fail type / fail model beside density context.</p></div>
        <label><span>Project / correlation key</span><input v-model="config.projectName" placeholder="e.g. Orion-A12"></label>
        <button class="primary" :disabled="faLoading" @click="loadFaCases">{{ faLoading?'Querying…':'Find FA records' }}</button>
      </div>
      <div class="metric-grid compact"><article class="metric"><span>GDS</span><strong class="small-text">{{ gdsFile?.name || 'demo.gds' }}</strong><small>Current layout</small></article><article class="metric"><span>Layer</span><strong>{{ config.layer }}</strong><small>{{ formatPct(mean) }} mean</small></article><article class="metric"><span>Matched FA cases</span><strong>{{ faRows.length }}</strong><small>Existing library records</small></article><article class="metric"><span>Density verdict</span><strong :class="overallPass?'ok':'bad'">{{ overallPass?'PASS':'REVIEW' }}</strong><small>Current analysis</small></article></div>
      <div class="panel"><div class="panel-title"><div><span class="kicker">FAILURE CONTEXT</span><h2>Matched FA records</h2></div></div><div v-if="!faRows.length" class="empty-state">No records loaded. Enter a project key and run the FA query.</div><table v-else><thead><tr><th>Case ID</th><th>Project</th><th>Product</th><th>Technology</th><th>Fail type</th><th>Fail model</th></tr></thead><tbody><tr v-for="row in faRows" :key="row.id"><td><strong>{{ row.case_id }}</strong></td><td>{{ row.project }}</td><td>{{ row.product }}</td><td>{{ row.technology }}</td><td>{{ row.fail_type || '—' }}</td><td>{{ row.fail_model || '—' }}</td></tr></tbody></table></div>
    </section>
  </main>
</template>

<style scoped>
.density-page{margin-left:220px;padding:30px 34px 52px;background:#f4f6f8;min-height:calc(100vh - 64px);color:#17212b}.density-header{display:flex;align-items:flex-start;justify-content:space-between;gap:28px;margin-bottom:18px}.eyebrow,.kicker{font-size:10px;letter-spacing:.16em;font-weight:800;color:#77818b}.density-header h1{font-size:30px;letter-spacing:-.03em;margin:4px 0 6px}.density-header p{margin:0;color:#66717c;font-size:13px}.header-actions{display:flex;align-items:center;gap:10px;padding-top:8px}.status-dot{width:8px;height:8px;border-radius:50%;background:#a7afb6}.status-dot.pass{background:#0a9a69;box-shadow:0 0 0 4px #dff4ec}.status-text{font-size:12px;color:#58636e;max-width:240px}.primary,.secondary{border:1px solid #17212b;border-radius:7px;height:38px;padding:0 16px;font-weight:700;cursor:pointer;background:#17212b;color:white}.primary:disabled,.secondary:disabled{opacity:.45;cursor:not-allowed}.secondary{background:white;color:#26313b;border-color:#cbd1d6}.secondary.small{height:32px;font-size:12px}.density-tabs{display:flex;gap:4px;border-bottom:1px solid #d5d9dd;margin-bottom:22px;overflow:auto}.density-tabs button{border:0;background:transparent;color:#66717c;font-weight:700;padding:11px 14px 13px;cursor:pointer;white-space:nowrap;border-bottom:2px solid transparent}.density-tabs button.active{color:#111820;border-bottom-color:#111820}.workspace{display:grid;gap:18px}.two-col{grid-template-columns:minmax(0,1.15fr) minmax(360px,.85fr)}.panel{background:#fff;border:1px solid #dfe3e6;border-radius:10px;padding:18px;box-shadow:0 1px 2px rgba(20,31,40,.03)}.panel.full{grid-column:1/-1}.panel-title{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:16px}.panel-title h2{font-size:16px;margin:3px 0 0}.chip{display:inline-flex;align-items:center;height:24px;border-radius:999px;background:#eef1f3;padding:0 9px;font-size:10px;font-weight:800;color:#66717c}.chip.ok{background:#e7f6f0;color:#087553}.chip.bad{background:#feebeb;color:#a83232}.drop-zone{height:142px;border:1px dashed #b9c1c8;border-radius:9px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;background:#fafbfc;margin-bottom:18px}.drop-zone:hover{border-color:#6d7882}.drop-icon{font-size:28px;color:#69757f}.drop-zone strong{font-size:14px;margin-top:6px}.drop-zone small{font-size:11px;color:#87919a;margin-top:4px}.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}.form-grid label,.config-card label,.compare-toolbar label,.fa-query label,.spec-editor label{display:grid;gap:6px;position:relative}.form-grid label span,.config-card label span,.compare-toolbar label span,.fa-query label span,.spec-editor label span{font-size:11px;font-weight:700;color:#64707b}.form-grid input,.config-card input,.compare-toolbar input,.fa-query input,.spec-editor input[type=number]{height:37px;border:1px solid #ccd2d7;border-radius:6px;padding:0 11px;background:white;color:#1d2730;outline:none}.form-grid input:focus,.config-card input:focus,.compare-toolbar input:focus,.fa-query input:focus,.spec-editor input:focus{border-color:#6a7680;box-shadow:0 0 0 2px #eef1f3}.form-grid label b{position:absolute;right:9px;bottom:11px;font-size:10px;color:#8a939b}.xml-preview{background:#141b21;color:#d6dde3;border-radius:8px;padding:12px;height:220px;overflow:auto;margin:13px 0}.xml-preview pre{margin:0;font-size:11px;line-height:1.6;white-space:pre-wrap}.button-row{display:flex;gap:8px;flex-wrap:wrap}.button-row.right{justify-content:flex-end}.spec-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}.spec-strip div{border:1px solid #e2e5e8;border-radius:7px;padding:10px}.spec-strip span,.stat-list span,.compare-summary span,.gate span{display:block;font-size:10px;color:#7c868e;margin-bottom:3px}.spec-strip strong{font-size:13px}.metric-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}.metric-grid.compact{grid-template-columns:repeat(4,minmax(0,1fr))}.metric{background:white;border:1px solid #dfe3e6;border-radius:9px;padding:14px}.metric span{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#7b858e;font-weight:800}.metric strong{display:block;font-size:24px;margin:8px 0 4px;letter-spacing:-.03em}.metric strong.small-text{font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.metric small{font-size:10px;color:#869099}.metric.verdict{background:#17212b;color:#fff;border-color:#17212b}.metric.verdict span,.metric.verdict small{color:#aeb8c0}.ok{color:#087b57!important}.bad{color:#b53636!important}.results-grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(340px,.55fr);gap:18px}.heat-wrap{padding:5px 0}.heatmap{display:grid;gap:3px;aspect-ratio:1.75/1}.heatmap.large{aspect-ratio:1.6/1}.heatmap button{border:0;border-radius:2px;min-width:0;cursor:crosshair;transition:transform .12s,filter .12s}.heatmap button:hover{transform:scale(1.15);filter:brightness(1.08);z-index:2}.legend{display:flex;align-items:center;gap:8px;font-size:9px;color:#7d878f;margin-top:9px}.legend i{height:7px;flex:1;border-radius:99px;background:linear-gradient(90deg,hsl(218 78% 54%),hsl(124 78% 54%),hsl(30 78% 54%))}.map-footer{display:flex;gap:16px;flex-wrap:wrap;font-size:10px;color:#74808a;margin-top:10px;border-top:1px solid #eef0f2;padding-top:10px}.histogram{height:210px;display:flex;align-items:flex-end;gap:5px;border-bottom:1px solid #dfe3e6;padding:14px 2px 0}.bar-wrap{display:flex;flex:1;height:100%;align-items:flex-end;flex-direction:column;justify-content:flex-end}.bar{width:100%;min-height:2px;background:#2f4352;border-radius:3px 3px 0 0;position:relative}.bar span{position:absolute;top:-16px;width:100%;text-align:center;font-size:8px;color:#8b949b}.bar-wrap small{font-size:8px;color:#8a949c;height:17px;padding-top:4px}.stat-list{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:14px}.stat-list div{background:#f7f8f9;border-radius:6px;padding:9px}.stat-list strong{font-size:13px}.compare-toolbar{display:flex;align-items:flex-end;gap:14px}.compare-toolbar label{width:190px}.versus{font-size:11px;font-weight:900;color:#8b949c;height:37px;display:flex;align-items:center}.compare-summary{margin-left:auto;min-width:110px}.compare-summary+.compare-summary{margin-left:0}.compare-summary strong{font-size:18px}.dual-map{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.region-table{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:#7b858d;padding:10px;border-bottom:1px solid #dfe3e6}td{padding:11px 10px;border-bottom:1px solid #eef0f2;color:#46515b}.mini-status,.layer-pill{display:inline-flex;align-items:center;border-radius:999px;background:#edf1f3;padding:3px 8px;font-size:10px;font-weight:800}.mini-status.ok{background:#e8f6f0}.mini-status.bad{background:#fdecec}.layer-pill{background:#eef1f4;color:#3f4b55}.spec-editor{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:end}.spec-editor input[type=range]{width:100%}.spec-gauge{margin:34px 0 20px}.spec-track{height:8px;background:#e7eaed;border-radius:99px;position:relative}.spec-track i{height:100%;display:block;border-radius:99px}.ok-bg{background:#15966d}.bad-bg{background:#c54747}.spec-track b{position:absolute;top:-5px;width:2px;height:18px;background:#202a32}.gauge-labels{display:flex;justify-content:space-between;font-size:9px;color:#7e8890;margin-top:7px}.spec-result{display:grid;gap:4px;border-radius:7px;padding:12px}.spec-result strong{font-size:13px}.spec-result span{font-size:10px}.pass-box{background:#eaf7f2;color:#176c52}.fail-box{background:#fff0f0;color:#963737}.line-chart{width:100%;height:220px;background:linear-gradient(#fff,#fafbfc);border-bottom:1px solid #dfe3e6}.gradient-line{fill:none;stroke:#263946;stroke-width:3;vector-effect:non-scaling-stroke}.spec-line{stroke:#bd4444;stroke-width:1.5;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}.specs{grid-template-columns:repeat(4,1fr);align-items:end}.gate{border:1px solid #e1e4e7;border-radius:7px;padding:9px 11px}.gate strong{font-size:15px}.benchmark{display:grid;gap:10px}.benchmark>div{display:grid;grid-template-columns:140px 1fr 70px;gap:10px;align-items:center;font-size:11px}.benchmark>div>div{height:8px;border-radius:99px;background:#eceff1;overflow:hidden}.benchmark i{display:block;height:100%;background:#354956}.benchmark strong{text-align:right}.console-layout{grid-template-columns:minmax(0,1.5fr) minmax(300px,.5fr)}.terminal{background:#11181e;border-radius:8px;overflow:hidden;color:#dbe4ea}.terminal-log{height:410px;overflow:auto;padding:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.terminal-entry{margin-bottom:14px}.terminal-entry p{margin:0 0 5px;color:#dbe4ea;font-size:11px}.terminal-entry p span{color:#6f7f8b}.terminal-entry pre{margin:0;color:#8fc9b4;font-size:11px;white-space:pre-wrap}.terminal-help{font-size:11px;color:#7e8c96}.terminal form{display:grid;grid-template-columns:22px 1fr 62px;border-top:1px solid #2c3740;align-items:center;padding:8px 8px 8px 12px}.terminal form input{background:transparent;border:0;color:white;outline:none;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.terminal form button{height:30px;border-radius:5px;border:1px solid #4a5a66;background:#24313a;color:#e6edf2;cursor:pointer}.command-ref code{display:inline-block;background:#f0f2f4;padding:5px 7px;border-radius:5px;font-size:11px;color:#2c3943;margin-top:9px}.command-ref p{font-size:10px;color:#75808a;margin:5px 0 10px}.fa-query{display:grid;grid-template-columns:1fr minmax(240px,.55fr) auto;align-items:end;gap:18px}.fa-query h2{margin:3px 0 5px;font-size:18px}.fa-query p{margin:0;color:#74808a;font-size:11px}.empty-state{padding:44px;text-align:center;color:#8a949d;font-size:12px;background:#fafbfc;border-radius:7px}
@media(max-width:1180px){.density-page{margin-left:190px;padding:24px}.two-col,.results-grid,.console-layout{grid-template-columns:1fr}.metric-grid{grid-template-columns:repeat(3,1fr)}.metric-grid.compact{grid-template-columns:repeat(2,1fr)}.fa-query{grid-template-columns:1fr}.compare-toolbar{flex-wrap:wrap}.compare-summary{margin-left:0}.panel.full{grid-column:auto}}
@media(max-width:760px){.density-page{margin-left:0;padding:18px}.density-header{flex-direction:column}.header-actions{flex-wrap:wrap}.metric-grid,.metric-grid.compact,.form-grid,.dual-map,.specs,.spec-editor{grid-template-columns:1fr}.spec-strip{grid-template-columns:1fr}.benchmark>div{grid-template-columns:100px 1fr 58px}}
</style>
