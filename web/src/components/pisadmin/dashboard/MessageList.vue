<template>
  <div class="message-list">
    <div v-for="msg in messages" :key="msg.id" class="message-item">
      <el-badge :is-dot="!msg.is_read" class="message-badge">
        <div class="message-content">
          <div class="message-title">{{ msg.title }}</div>
          <div class="message-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </el-badge>
    </div>
    <el-empty v-if="messages.length === 0" description="暂无消息" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  messages: Array<{
    id: number;
    title: string;
    content: string;
    is_read: boolean;
    created_at: string;
  }>;
}>();

function formatTime(time: string) {
  if (!time) return '';
  return new Date(time).toLocaleDateString();
}
</script>

<style scoped lang="scss">
.message-list {
  .message-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    &:last-child { border-bottom: none; }
  }
  .message-content {
    .message-title {
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
    .message-time {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }
}
</style>
