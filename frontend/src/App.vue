<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header">
      <h1><img src="/L.png" style="width:24px;height:24px;vertical-align:middle;margin-right:6px;" />L线 - 数据追踪</h1>
      <DateRangeFilter
        :startDate="dateRange.start"
        :endDate="dateRange.end"
        @update:dateRange="onDateRangeChange"
      />
      <div class="display-mode-toggle">
        <span>显示模式:</span>
        <button :class="{ 'btn-active': displayMode === 'hover' }" @click="displayMode = 'hover'">
          悬停
        </button>
        <button :class="{ 'btn-active': displayMode === 'all-labels' }" @click="displayMode = 'all-labels'">
          全标签
        </button>
        <span style="margin-left:8px">|</span>
        <label style="cursor:pointer;font-size:0.85rem;display:flex;align-items:center;gap:4px;">
          <input type="checkbox" v-model="showMarkPoint" />
          最大/最小值
        </label>
        <label style="cursor:pointer;font-size:0.85rem;display:flex;align-items:center;gap:4px;">
          <input type="checkbox" v-model="showTags" />
          标签
        </label>
      </div>
    </header>

    <!-- Sidebar -->
    <aside class="app-sidebar">
      <LineManager
        :lines="lines"
        @add-line="onAddLine"
        @delete-line="onDeleteLine"
        @rename-line="onRenameLine"
        @toggle-visible="onToggleVisible"
        @update-color="onUpdateColor"
      />
      <DataEntry
        :lines="lines"
        @data-saved="refreshAll"
      />
    </aside>

    <!-- Main Chart -->
    <main class="app-main">
      <ChartView
        :chartData="chartData"
        :displayMode="displayMode"
        :showMarkPoint="showMarkPoint"
        :showTags="showTags"
        @point-click="onPointClick"
      />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <span v-if="chartData.length > 0" style="color: var(--color-text-secondary)">
        {{ totalPoints }} 个数据点 / {{ visibleLineCount }}/{{ lines.length }} 条线
      </span>
    </footer>

    <!-- Modals -->
    <DataPointEditDialog
      v-if="editingPoint"
      :point="editingPoint"
      @point-update="onPointUpdate"
      @point-delete="onPointDelete"
      @close="editingPoint = null"
    />
    <ConfirmDialog
      v-if="deletingLine"
      title="删除折线"
      :message="'确定要永久删除折线 \'' + deletingLine.name + '\' 及其所有数据？此操作不可撤销。'"
      @confirm="confirmDeleteLine"
      @cancel="deletingLine = null"
    />

    <!-- Toast notifications -->
    <div class="toast-container">
      <div v-for="(t, i) in toasts" :key="i" class="toast" :class="'toast-' + t.type">
        {{ t.msg }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as api from './api.js'

import LineManager from './components/LineManager.vue'
import DataEntry from './components/DataEntry.vue'
import ChartView from './components/ChartView.vue'
import DateRangeFilter from './components/DateRangeFilter.vue'

import DataPointEditDialog from './components/DataPointEditDialog.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'

// ---- State ----
const lines = ref([])
const chartData = ref([])
const dateRange = ref({ start: '', end: '' })
const displayMode = ref('hover')
const showMarkPoint = ref(true)
const showTags = ref(true)
const editingPoint = ref(null)
const deletingLine = ref(null)
const toasts = ref([])

// ---- Computed ----
const totalPoints = computed(() => {
  return chartData.value.reduce((sum, l) => sum + l.points.length, 0)
})

const visibleLineCount = computed(() => {
  return chartData.value.filter(l => l.visible).length
})

// ---- Data Fetching ----
async function fetchLines() {
  try {
    lines.value = await api.getLines()
  } catch (e) {
    showToast('加载折线失败', 'error')
  }
}

async function fetchChartData() {
  try {
    chartData.value = await api.getDataPoints(dateRange.value.start, dateRange.value.end)
  } catch (e) {
    showToast('加载图表数据失败', 'error')
  }
}

async function refreshAll() {
  await fetchLines()
  await fetchChartData()
}

// ---- Event Handlers ----

function onDateRangeChange(range) {
  dateRange.value = { start: range.start || '', end: range.end || '' }
  fetchChartData()
}

async function onAddLine(name, color) {
  try {
    await api.createLine(name, color)
    showToast(`折线"${name}"已创建`, 'success')
    await fetchLines()
    await fetchChartData()
  } catch (e) {
    const msg = e.response?.data?.error || '创建折线失败'
    showToast(msg, 'error')
  }
}

function onDeleteLine(line) {
  deletingLine.value = line
}

async function confirmDeleteLine() {
  const name = deletingLine.value.name
  try {
    await api.deleteLine(deletingLine.value.id)
    showToast(`折线"${name}"已删除`, 'success')
    deletingLine.value = null
    await refreshAll()
  } catch (e) {
    showToast('删除折线失败', 'error')
  }
}

async function onRenameLine(id, newName) {
  try {
    await api.updateLine(id, { name: newName })
    await refreshAll()
  } catch (e) {
    showToast(e.response?.data?.error || '重命名失败', 'error')
  }
}

async function onToggleVisible(id, visible) {
  try {
    await api.updateLine(id, { visible })
    await fetchLines()
    await fetchChartData()
  } catch (e) {
    showToast('更新可见性失败', 'error')
  }
}

async function onUpdateColor(id, color) {
  try {
    await api.updateLine(id, { color })
    await fetchLines()
    await fetchChartData()
  } catch (e) {
    showToast('更新颜色失败', 'error')
  }
}

async function onDataAdded(payload) {
  try {
    const result = await api.createOrUpdateDataPoint(payload.line_id, payload.date, payload.value)
    const action = result.created_at === result.updated_at ? 'saved' : 'updated'
    showToast(`Data ${action}`, 'success')
    await fetchChartData()
  } catch (e) {
    showToast(e.response?.data?.error || '保存数据失败', 'error')
    throw e
  }
}

function onPointClick(point) {
  editingPoint.value = point
}

async function onPointUpdate(data) {
  try {
    await api.updateDataPoint(data.id, { date: data.date, value: data.value, tag: data.tag || '' })
    showToast('数据点已更新', 'success')
    editingPoint.value = null
    await fetchChartData()
  } catch (e) {
    showToast(e.response?.data?.error || '更新失败', 'error')
  }
}

async function onPointDelete(pointId) {
  try {
    await api.deleteDataPoint(pointId)
    showToast('数据点已删除', 'success')
    editingPoint.value = null
    await fetchChartData()
  } catch (e) {
    showToast('删除失败', 'error')
  }
}

// ---- Helpers ----
function showToast(msg, type = 'success') {
  const id = Date.now()
  toasts.value.push({ id, msg, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 2500)
}

// ---- Init ----
onMounted(() => {
  refreshAll()
})
</script>
