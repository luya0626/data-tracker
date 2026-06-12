<template>
  <div class="chart-container" ref="containerRef">
    <div v-if="isEmpty" class="chart-empty">
      <p v-if="hasLines">所选日期范围内没有数据。</p>
      <p v-else>请添加折线并记录数据以查看图表。</p>
    </div>
    <div ref="chartDom" style="width:100%; height:100%;"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartData: { type: Array, required: true },
  displayMode: { type: String, default: 'hover' },
  showMarkPoint: { type: Boolean, default: true },
  showTags: { type: Boolean, default: true },
})

const emit = defineEmits(['point-click'])

const containerRef = ref(null)
const chartDom = ref(null)
let chart = null

const isEmpty = ref(true)
const hasLines = ref(false)

// Store mapping for click handler
let sortedDates = []
let pointMap = {} // {lineId: {dateIndex: pointObject}}

function buildChartOption() {
  const visibleLines = props.chartData.filter(l => l.visible)
  hasLines.value = props.chartData.length > 0

  if (visibleLines.length === 0) {
    isEmpty.value = true
    return null
  }

  // Collect all unique dates from visible lines
  const dateSet = new Set()
  visibleLines.forEach(line => {
    line.points.forEach(p => dateSet.add(p.date))
  })
  sortedDates = Array.from(dateSet).sort()

  if (sortedDates.length === 0) {
    isEmpty.value = true
    return null
  }

  isEmpty.value = false
  pointMap = {}
  const seriesLineIds = []  // seriesIndex -> line_id mapping

  // Build series
  const series = visibleLines.map(line => {
    seriesLineIds.push(line.line_id)
    const valueMap = new Map(line.points.map(p => [p.date, p]))
    const data = sortedDates.map((date, idx) => {
      const pt = valueMap.get(date)
      if (pt) {
        if (!pointMap[line.line_id]) pointMap[line.line_id] = {}
        pointMap[line.line_id][idx] = pt
        return pt.value
      }
      return null
    })

    return {
      name: line.line_name,
      type: 'line',
      data: data,
      connectNulls: true,
      lineStyle: { color: line.line_color, width: 2.5 },
      itemStyle: { color: line.line_color },
      symbol: 'circle',
      symbolSize: 7,
      emphasis: { symbolSize: 12 },
      _lineId: line.line_id,
      markPoint: props.showMarkPoint ? {
        data: [
          { type: 'max', name: '最大值', symbolSize: 50 },
          { type: 'min', name: '最小值', symbolSize: 50 },
        ],
        symbol: 'pin',
        label: { fontSize: 10, color: '#fff' },
        itemStyle: { color: line.line_color },
      } : undefined,
      label: {
        show: props.displayMode === 'all-labels',
        position: 'top',
        fontSize: 10,
        color: line.line_color,
        formatter: (p) => {
          if (p.value == null) return ''
          let txt = String(p.value)
          const lid = seriesLineIds[p.seriesIndex]
          const pt = pointMap[lid]?.[p.dataIndex]
          if (pt?.tag && props.showTags) {
            txt += '\n' + pt.tag
          }
          return txt
        },
      },
    }
  })

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#ccc',
      textStyle: { color: '#333', fontSize: 12 },
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const xDate = sortedDates[params[0].dataIndex]
        let html = `<strong>${xDate}</strong><br/>`
        params.forEach(p => {
          if (p.value != null) {
            html += `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color};margin-right:6px;"></span>`
            html += `${p.seriesName}: <strong>${p.value}</strong>`
            const lid = seriesLineIds[p.seriesIndex]
            const pt = pointMap[lid]?.[p.dataIndex]
            if (pt?.tag && props.showTags) {
              html += ` <span style="color:${p.color};font-size:11px;opacity:0.7;">[${pt.tag}]</span>`
            }
            html += '<br/>'
          }
        })
        return html
      },
    },
    legend: {
      data: series.map(s => s.name),
      bottom: 0,
      type: 'scroll',
      textStyle: { fontSize: 12 },
    },
    grid: { left: 55, right: 30, top: 25, bottom: 40 },
    xAxis: {
      type: 'category',
      data: sortedDates,
      axisLabel: {
        rotate: sortedDates.length > 15 ? 45 : 0,
        fontSize: 11,
      },
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: '数值',
      nameTextStyle: { fontSize: 11 },
      scale: true,
    },
    series: series,
    dataZoom: [
      {
        type: 'inside',
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: false,
      },
      {
        type: 'slider',
        bottom: 8,
        height: 12,
        borderColor: 'transparent',
        fillerColor: 'rgba(84,112,198,0.1)',
        handleStyle: { color: '#5470C6', width: 6 },
        textStyle: { fontSize: 9 },
        moveHandleSize: 0,
        showDetail: false,
      },
    ],
  }
}

function initChart() {
  if (!chartDom.value) return
  if (chart) chart.dispose()

  chart = echarts.init(chartDom.value)

  chart.on('click', (params) => {
    if (params.componentType === 'series' && params.seriesIndex != null) {
      const seriesOpt = chart.getOption().series[params.seriesIndex]
      const lineId = seriesOpt._lineId
      const dateIdx = params.dataIndex
      const pt = pointMap[lineId]?.[dateIdx]
      if (pt) {
        const line = props.chartData.find(l => l.line_id === lineId)
        emit('point-click', {
          id: pt.id,
          line_id: lineId,
          line_name: line?.line_name || '',
          date: pt.date,
          value: pt.value,
          tag: pt.tag || '',
        })
      }
    }
  })

  window.addEventListener('resize', handleResize)
  renderChart()
}

function handleResize() {
  chart?.resize()
}

function renderChart() {
  if (!chart) return
  const option = buildChartOption()
  if (option) {
    chart.setOption(option, true)
  } else {
    chart.clear()
  }
}

watch(() => [props.chartData, props.displayMode, props.showMarkPoint, props.showTags], () => {
  nextTick(renderChart)
}, { deep: true })

onMounted(() => {
  nextTick(initChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>
