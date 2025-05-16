<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  chatHistory: {
    type: Array,
    default: () => []
  },
  newChatRecord: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:visible', 'submit']);

  const handleBeforeOk = (done) => {
    // 获取当前所有记录
    const systemRecord = props.chatHistory.find(item => item.role === 'system');
    const existingRecords = props.chatHistory.filter(item => 
      item.role !== 'system' || item.content === ''
    );
    
    // 创建新历史记录
    const newHistory = [];
    
    // 添加系统提示词（如果有）
    if (systemRecord) {
      newHistory.push(systemRecord);
    }
    
    // 保留非系统记录和有效记录
    newHistory.push(...existingRecords);
    
    // 添加新记录
    newHistory.push({
      role: props.newChatRecord.Role.toLowerCase(),
      content: props.newChatRecord.content
    });
    
    // 触发提交事件并关闭模态框
    emit('submit', newHistory);
    // 清空输入框内容
    props.newChatRecord.content = '';
    props.newChatRecord.Role = 'user';
    done();
  };

const handleCancel = () => {
  emit('update:visible', false);
};
</script>

<template>
  <a-modal 
    :visible="visible" 
    title="添加对话记录" 
    @cancel="handleCancel" 
    @before-ok="handleBeforeOk"
    @update:visible="val => emit('update:visible', val)"
  >
    <a-form :model="newChatRecord">
      <a-form-item field="Role" label="角色">
        <a-select v-model="newChatRecord.Role">
          <a-option value="system">系统</a-option>
          <a-option value="assistant">AI</a-option>
          <a-option value="user">用户</a-option>
        </a-select>
      </a-form-item>
      <a-form-item field="content" label="内容">
        
        <a-textarea v-model="newChatRecord.content" placeholder="对话内容" :max-length="100" allow-clear show-word-limit />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
