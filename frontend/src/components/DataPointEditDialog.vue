<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <h3>编辑数据点</h3>

      <div class="form-row">
        <div class="field">
          <label>折线</label>
          <input :value="point.line_name" disabled />
        </div>
      </div>
      <div class="form-row">
        <div class="field">
          <label>日期</label>
          <input type="date" v-model="editDate" />
        </div>
        <div class="field">
          <label>数值</label>
          <input type="number" step="any" v-model="editValue" />
        </div>
      </div>
      <div class="form-row">
        <div class="field" style="flex:1;">
          <label>标签（可选）</label>
          <input type="text" v-model="editTag" placeholder="备注标签" maxlength="30" />
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-danger" @click="confirmDelete">删除</button>
        <button @click="$emit('close')">取消</button>
        <button class="btn-primary" @click="save" :disabled="!editDate || editValue === ''">保存</button>
      </div>

      <ConfirmDialog
        v-if="showDeleteConfirm"
        title="删除数据点"
        :message="'确定删除 ' + point.line_name + ' 于 ' + point.date + ' 的数据点？此操作不可撤销。'"
        @confirm="doDelete"
        @cancel="showDeleteConfirm = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  point: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['point-update', 'point-delete', 'close'])

const editDate = ref(props.point.date)
const editValue = ref(props.point.value)
const editTag = ref(props.point.tag || '')
const showDeleteConfirm = ref(false)

function save() {
  emit('point-update', {
    id: props.point.id,
    date: editDate.value,
    value: parseFloat(editValue.value),
    tag: editTag.value.trim(),
  })
}

function confirmDelete() {
  showDeleteConfirm.value = true
}

function doDelete() {
  showDeleteConfirm.value = false
  emit('point-delete', props.point.id)
}
</script>
