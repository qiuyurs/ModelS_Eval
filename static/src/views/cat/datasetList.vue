<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import ChatRecord from '@/components/ChatRecord.vue'
import AddChatRecord from '@/components/AddChatRecord.vue'
import axios from '@/utils/request'

const sn = ref('')

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80
  },
  {
    title: '数据集名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at'
  },
  {
    title: '操作',
    key: 'action',
    width: 100,
    slotName: 'action'
  }
]

const datasets = ref([])
const selectedDataset = ref(null)
const showAddModal = ref(false)
const showDetailModal = ref(false)
const showChatRecord = ref(false)
const currentRecord = ref({})
const messages = ref([])
const newDataset = ref({
  name: '',
  messages: ''
})

// 获取数据集列表
const fetchDatasets = async () => {
  try {
    const response = await axios.get('/api/datasets')
    datasets.value = response.data
  } catch (error) {
    Message.error(error.message)
  }
}

// 添加对话记录
const handleAddChatRecord = async (chatHistory) => {
  messages.value.push(...chatHistory)
  newDataset.value.messages = ''
}

// 添加数据集
const handleAddDataset = async () => {
  try {
    // if (!newDataset.value.name) {
    //   Message.warning('数据集名称不能为空')
    //   return
    // }

    const datasetData = {
      name: sn.value,
      messages: JSON.stringify(messages.value)
    }

    const response = await axios.post('/api/datasets', datasetData)
    
    await fetchDatasets()
    showAddModal.value = false
    showChatRecord.value = false
    Message.success('数据集添加成功')
  } catch (error) {
    Message.error(error.message)
  }
}

// 查看数据集详情
const showDetail = (dataset) => {
  try {
    currentRecord.value = dataset
    messages.value = JSON.parse(dataset.messages)
    showDetailModal.value = true
  } catch (error) {
    Message.error('解析数据集消息失败: ' + error.message)
    console.error('JSON解析错误:', error)
  }
}

onMounted(() => {
  fetchDatasets()
})
</script>

<template>
        <a-space direction="vertical" style="width: 100%">
          <a-button type="primary" @click="showChatRecord = true">添加数据集</a-button>
          <a-table
            :data="datasets"
            :columns="columns"
            :pagination="false"
            style="margin-top: 16px"
          >
          <template #action="{ record }">
            <a-space>
              <a-button type="text" @click="showDetail(record)">对话记录</a-button>
            </a-space>
          </template>
        </a-table>
      </a-space>

  <!-- 添加数据集模态框 -->
  <AddChatRecord
  v-model:visible="showAddModal"
  @submit="handleAddChatRecord" 
  :new-chat-record="newDataset"
/>

  <!-- 聊天记录模态框 -->
  <a-modal
    v-model:visible="showChatRecord"
    title="对话记录"
    :footer="false"
  >
  
    <ChatRecord
      :chat-history="messages"
    >
      <template #actions>
        <a-button type="primary" @click="showAddModal = true">添加对话</a-button>
      </template>
    </ChatRecord>

    <a-space style="margin-top: 15px;">
    数据集名称：<a-input v-model="sn"></a-input>
    <a-button type="primary" @click="handleAddDataset">保存数据集</a-button>
  </a-space>
  </a-modal>
  
  <!-- 数据集详情模态框 -->
  <a-modal v-model:visible="showDetailModal" @ok="() => showDetailModal = false">
    <template #title>
      <h3 style="color: #1a73e8; margin: 0;">数据集详情 - {{currentRecord.name}}</h3>
    </template>
    <ChatRecord :chat-history="messages" />
  </a-modal>
</template>

<style scoped>
.ant-list-item {
  cursor: pointer;
  padding: 12px 16px;
  transition: background-color 0.3s;
}

.ant-list-item:hover {
  background-color: #f5f5f5;
}
</style>
