<template>
  <div class="sidebar-section">
    <h3>折线管理</h3>

    <!-- Add line form -->
    <div class="add-line-form">
      <input
        v-model="newName"
        type="text"
        placeholder="折线名称..."
        maxlength="50"
        @keyup.enter="addLine"
      />
      <input v-model="newColor" type="color" title="选择颜色" />
      <button class="btn-primary btn-small" @click="addLine" :disabled="!newName.trim()">+ 添加</button>
    </div>

    <!-- Empty state -->
    <div v-if="lines.length === 0" class="empty-state">
      <p>暂无折线，请添加第一条折线开始使用！</p>
    </div>

    <!-- Line list -->
    <ul v-else class="line-list">
      <li v-for="line in lines" :key="line.id" class="line-item">
        <input
          type="checkbox"
          :checked="line.visible"
          @change="$emit('toggle-visible', line.id, !line.visible)"
          title="显示/隐藏"
        />
        <span class="color-dot" :style="{ background: line.color }"></span>

        <input
          v-if="editingId === line.id"
          v-model="editName"
          class="line-name editing"
          @keyup.enter="saveRename(line.id)"
          @keyup.escape="cancelRename"
          @blur="saveRename(line.id)"
          ref="renameInput"
        />
        <span
          v-else
          class="line-name"
          @dblclick="startRename(line)"
          :title="line.name + ' (双击重命名)'"
        >{{ line.name }}</span>

        <div class="line-actions">
          <input
            type="color"
            :value="line.color"
            @change="$emit('update-color', line.id, $event.target.value)"
            title="更改颜色"
            class="btn-small"
          />
          <button class="btn-small" @click="startRename(line)" title="重命名">✏️</button>
          <button class="btn-small btn-danger" @click="$emit('delete-line', line)" title="删除">🗑</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  lines: { type: Array, required: true },
})

const emit = defineEmits([
  'add-line',
  'delete-line',
  'rename-line',
  'toggle-visible',
  'update-color',
])

const newName = ref('')
const newColor = ref('#5470C6')
const editingId = ref(null)
const editName = ref('')
const renameInput = ref(null)

function addLine() {
  const name = newName.value.trim()
  if (!name) return
  emit('add-line', name, newColor.value)
  newName.value = ''
}

function startRename(line) {
  editingId.value = line.id
  editName.value = line.name
  nextTick(() => {
    if (renameInput.value) renameInput.value.focus()
  })
}

function saveRename(id) {
  const name = editName.value.trim()
  if (name && editingId.value === id) {
    emit('rename-line', id, name)
  }
  editingId.value = null
}

function cancelRename() {
  editingId.value = null
}
</script>
