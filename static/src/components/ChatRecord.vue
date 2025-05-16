<script setup>
import { defineProps, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';

const props = defineProps({
  chatHistory: {
    type: Array,
    required: true,
  },
});

const containerHeight = ref('calc(100vh - 180px)');

const calculateHeight = () => {
  containerHeight.value = `${window.innerHeight - 280}px`;
};

onMounted(() => {
  calculateHeight();
  window.addEventListener('resize', calculateHeight);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', calculateHeight);
});

// 监听chatHistory变化并自动滚动到底部
watch(() => props.chatHistory, () => {
  nextTick(() => {
    const container = document.querySelector('.arco-card-body');
    if (container) {
      container.scrollTop = container.scrollHeight;
      const lastMessage = container.lastElementChild;
      if (lastMessage) {
        lastMessage.scrollIntoView({ behavior: 'smooth' });
      }
    }
  });
}, { deep: true });

const getAvatar = (role) => {
  const avatars = {
    system: 'data:image/jpeg;base64,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',
    assistant: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABAAEADASIAAhEBAxEB/8QAGgABAAMBAQEAAAAAAAAAAAAAAAYHCAQCCv/EACYQAAEEAgICAQUBAQAAAAAAAAIAAQMEBQYREgcTFQgUNXa0FiH/xAAbAQEAAgIDAAAAAAAAAAAAAAAABQYDBAcICf/EACERAAICAgMBAAMBAAAAAAAAAAIDAQQABQYREhMUISIj/9oADAMBAAIRAxEAPwD6iERF5r51nwiImMIiJjCIiYwiImMKWYbRtr2DDZPYMPiJLuIw/v8AkLQWaUbwvWrDcnEK09mK3ZKOsYSuNWCYnYhEWc3YVE1tjC5yr4yLxZ47sjCxZ2vYtbS0j9jhtZ5jgoRGwAwvH8lKdQjk4YKtQXPluZGunC+Oa7fWrh7q4/X6qmuok7deVwcbHa3U0NYkpatoQqWMdZsfzBRVqPmDX19Bm9Jra2wa4rrmV6iRSBOX57izbeFeqE+xKPEkRtZ+omFJZMEPXqMTqR7HqewanNTr7Bj/AI+XIUxv0w+6pWvdUMyAZe1KzZGPkhJvXKQSNxy4Mzs79m+a0eo7dncA4kMFK9IVFy7v3x1lms0C7n/0y+0liCQuSb3DIPYnF3Vt/UX+Y039Rq/1TrXXx0V6nl1i9L07LjV3VUhQBhCJbau26lwXiSiYfzmtHxlbFREyUnDImIjGOtgam5ZY+gWdY6oiAGR+cm57UuhkSEkXn5x4kSD99zPqJiIzqiIqnkRhERMZZviDWP8AVb9hKcod6VCV81kG5bh6uNIJRA2JiYo7FwqtWQeGd45y4cXblrP2zyT4mzWyXclltHzGYyFay9SHL19kyNSOaHHyFDVsU4qeSrw14iEGni9UYF2N5ScpSMyojXNw2LUnvlr2QbHHk6zVLsjU6FmSWuzm7RhJcq2Drtybk5VihMiYCcneONxjSu1DlgabjtfU62pVfbs7KzsNye31Ot2VQ5UtSNSqku4NqO6y/wAtrHGhDAbaNa5NfZTOV9uNLWrqVkqY5lllm6VypWspmREF1BSLobH+Y/YyMlrITbIjMj3M6U83x0ts1/T/AChh4TCtkq54bIgZlJLXmhksSVI5yHkHkgmjyVWaZ+rmQ1xZzZw45fqL/Mab+o1f6p1TUe37FHrU2njkXfXJ7LXJMcdWlIzWBlinY4rUlYr0De6EJHjgsxxE7ydgdppmk87HtmwbZNTsbBkPkJcfTGhTP7WlV9NQDIxi60q1YZOCIn9konI/PDm7MzNI7rmGs2lLkchWuL2XJa3Fm3Z+FZdONvqCfG1cv52SMa9z0qwiYT7l7HixahEDZs3dzVtI2XS3DZ2atUb/APNQpi5Tk/yzHy2ShTv5YvoPUmTIIQiIIo4iIuOMrWERExhERMYRETGERExn/9k=',
    user: 'data:image/jpeg;base64,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',
  };
  return avatars[role];
};
</script>

<template>
  <a-card title="对话记录" :style="{ height: containerHeight }">
    <template #extra>
      <a-space>
        <slot name="actions">
          <!-- Default action slot -->
        </slot>
      </a-space>
    </template>
    <a-comment v-for="(item, index) in chatHistory" :key="index" :content="item.content" :class="{
      'system-bubble': item.role === 'system',
      'ai-bubble': item.role === 'assistant',
      'user-bubble': item.role === 'user'
    }">
      <template #avatar>
        <a-avatar>
          <img :src="getAvatar(item.role)" alt="avatar" />
        </a-avatar>
      </template>
    </a-comment>
  </a-card>
</template>

<style scoped>
/* 聊天记录容器样式 */
:deep(.arco-card-body) {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

/* 气泡对话框基础样式 */
:deep(.arco-comment-content) {
  position: relative;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 8px 0;
  max-width: 80%;
  width: fit-content;
  min-width: 10%;
  word-break: break-word;
}


.user-bubble :deep(.arco-comment-content) {
  background-color: #E6F7FF;
  border: 1px solid #91D5FF;
  color: #0050B3;
  margin-left: auto;
}


.system-bubble :deep(.arco-comment-content) {
  background-color: #F6FFED;
  border: 1px solid #B7EB8F;
  color: #135200;
  margin-right: auto;
}


.ai-bubble :deep(.arco-comment-content) {
  background-color: #FFF7E6;
  border: 1px solid #FFD591;
  color: #874D00;
  margin-right: auto;
}

/* 头像位置调整 */
.user-bubble :deep(.arco-comment-avatar) {
  order: 1;
  margin-left: 12px;
}

.user-comment :deep(.arco-comment-avatar) {
  order: 1;
  margin-left: 12px;
  margin-right: 0;
}

.user-comment :deep(.arco-comment-content) {
  order: 0;
}

/* 用户角色气泡 - 名称和头像都在右侧 */
.user-bubble :deep(.arco-comment) {
  flex-direction: row-reverse;
  justify-content: flex-end;
}

.user-bubble :deep(.arco-comment-main) {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-bubble :deep(.arco-comment-avatar) {
  order: 1;
  margin-left: 12px;
  margin-right: 0;
}

.user-bubble :deep(.arco-comment-author) {
  order: 0;
  text-align: right;
  margin-left: 0;
  margin-right: 12px;
}

.user-bubble :deep(.arco-comment-content) {
  margin-left: auto;
  order: -1;
}
</style>
