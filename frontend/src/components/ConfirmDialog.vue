<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-box">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="modal-actions">
        <button @click="$emit('cancel')">取消</button>
        <button class="btn-danger" @click="$emit('confirm')">删除</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '确认' },
  message: { type: String, default: '确定要执行此操作吗？' },
})

defineEmits(['confirm', 'cancel'])
</script>
