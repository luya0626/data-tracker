<template>
  <div class="date-filter">
    <button
      v-for="btn in quickButtons"
      :key="btn.key"
      :class="{ 'btn-active': activeKey === btn.key }"
      @click="selectQuick(btn.key)"
    >{{ btn.label }}</button>
    <div v-if="activeKey === 'custom'" class="custom-range">
      <input type="date" :value="startDate" @input="$emit('update:dateRange', { start: $event.target.value, end: endDate })" />
      <span>~</span>
      <input type="date" :value="endDate" @input="$emit('update:dateRange', { start: startDate, end: $event.target.value })" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
})

const emit = defineEmits(['update:dateRange'])

const activeKey = ref('all')

function fmt(date) {
  return date.toISOString().slice(0, 10)
}

const quickButtons = [
  { key: 'all', label: '全部', getRange: () => ({ start: '', end: '' }) },
  { key: '7d', label: '近7天', getRange: () => {
    const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 6)
    return { start: fmt(s), end: fmt(e) }
  }},
  { key: '30d', label: '近30天', getRange: () => {
    const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 29)
    return { start: fmt(s), end: fmt(e) }
  }},
  { key: '90d', label: '近90天', getRange: () => {
    const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 89)
    return { start: fmt(s), end: fmt(e) }
  }},
  { key: '1y', label: '近1年', getRange: () => {
    const e = new Date(); const s = new Date(); s.setFullYear(s.getFullYear() - 1)
    return { start: fmt(s), end: fmt(e) }
  }},
  { key: 'custom', label: '自定义', getRange: null },
]

function selectQuick(key) {
  activeKey.value = key
  const btn = quickButtons.find(b => b.key === key)
  if (btn && btn.getRange) {
    emit('update:dateRange', btn.getRange())
  }
}

// Sync activeKey when props change externally
watch(() => [props.startDate, props.endDate], () => {
  for (const btn of quickButtons) {
    if (!btn.getRange) continue
    const r = btn.getRange()
    if (r.start === props.startDate && r.end === props.endDate) {
      activeKey.value = btn.key
      return
    }
  }
  if (props.startDate || props.endDate) {
    activeKey.value = 'custom'
  }
})
</script>
