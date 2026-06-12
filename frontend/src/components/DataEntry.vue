<template>
  <div class="sidebar-section">
    <h3>记录数据</h3>
    <div class="data-entry-form">
      <div class="field">
        <label>折线</label>
        <select v-model="selectedLineId">
          <option value="" disabled>-- 请选择 --</option>
          <option v-for="line in lines" :key="line.id" :value="line.id">{{ line.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>数值</label>
        <input
          v-model="valueStr"
          type="text"
          inputmode="decimal"
          placeholder="数字"
          @keyup.enter="submit"
        />
      </div>
      <div class="field">
        <label>日期</label>
        <input v-model="dateStr" type="date" />
      </div>
      <div class="field" style="flex:2;min-width:120px;">
        <label>标签（可选）</label>
        <input v-model="tagStr" type="text" placeholder="备注标签" maxlength="30" />
      </div>
      <div class="field">
        <label>&nbsp;</label>
        <button class="btn-primary" @click="submit" :disabled="!canSubmit || saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
    <div v-if="feedback" class="feedback" :class="feedback.type">{{ feedback.msg }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createOrUpdateDataPoint } from '../api.js'

const props = defineProps({
  lines: { type: Array, required: true },
})

const emit = defineEmits(['data-saved'])

const selectedLineId = ref('')
const valueStr = ref('')
const dateStr = ref(today())
const tagStr = ref('')
const feedback = ref(null)
const saving = ref(false)

function today() {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

const canSubmit = computed(() => {
  return selectedLineId.value !== '' && valueStr.value.trim() !== ''
})

async function submit() {
  if (!canSubmit.value || saving.value) return
  const val = parseFloat(valueStr.value.trim())
  if (isNaN(val)) {
    feedback.value = { type: 'toast-error', msg: '请输入有效数字。' }
    setTimeout(() => { feedback.value = null }, 2000)
    return
  }
  saving.value = true
  try {
    await createOrUpdateDataPoint(Number(selectedLineId.value), dateStr.value, val, tagStr.value.trim())
    feedback.value = { type: 'toast-success', msg: '数据保存成功！' }
    valueStr.value = ''
    tagStr.value = ''
    dateStr.value = today()
    emit('data-saved')
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || '保存失败。'
    feedback.value = { type: 'toast-error', msg }
  }
  saving.value = false
  setTimeout(() => { feedback.value = null }, 2000)
}
</script>

<style scoped>
.feedback {
  margin-top: 8px;
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
}
.feedback.toast-success {
  color: var(--color-success);
  background: #eafaf1;
}
.feedback.toast-error {
  color: var(--color-danger);
  background: #fdecea;
}
</style>
