<template>
  <h2>大模型请求记录</h2>
  <a-divider />
  
    <a-modal v-model:visible="visible" @ok="handleOk" @cancel="handleCancel">
      <template #title>
        <h3 style="color: #1a73e8; margin: 0;">对话记录 - {{currentRecord.model_name}}</h3>
      </template>
      <ChatRecord :chatHistory="messages" />
    </a-modal>
  
  <a-table :columns="columns" :data="data">
    <template #action="{ record }">
      <a-space>
        <a-button type="text" @click="showDetail(record)">对话记录</a-button>
      </a-space>
    </template>
  </a-table>
</template>

<script>
import { reactive, onMounted, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import ChatRecord from '../../components/ChatRecord.vue'
import axios from '@/utils/request'

export default {
  components: {
    ChatRecord
  },
  setup() {
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 80
      },
      {
        title: '模型名称',
        dataIndex: 'model_name',
        key: 'model_name'
      },
      {
        title: '请求Token',
        dataIndex: 'prompt_tokens',
        key: 'prompt_tokens'
      },
      {
        title: '生成Token',
        dataIndex: 'completion_tokens',
        key: 'completion_tokens'
      },
      {
        title: '首字耗时(s)',
        dataIndex: 'first_token_time',
        key: 'first_token_time'
      },
      {
        title: '总耗时(s)',
        dataIndex: 'total_time',
        key: 'total_time'
      },
      {
        title: '操作',
        key: 'action',
        width: 100,
        slotName: 'action'
      }
    ]

    const data = reactive([])
    const visible = ref(false)
    const currentRecord = ref({})
    const messages = ref([])


    async function fetchHistory() {
      try {
        const response = await axios.get('/api/history')
        if (response.data.length > 0) {
          data.splice(0, data.length, ...response.data)
        } else {
          Message.warning('暂无请求记录')
        }
      } catch (error) {
        Message.error('获取请求记录失败：' + error.message)
      }
    }

    const showDetail = (record) => {
      currentRecord.value = record
      messages.value = record.messages
      visible.value = true
    }

    const handleOk = () => {
      visible.value = false
    }

    const handleCancel = () => {
      visible.value = false
    }

    onMounted(() => {
      fetchHistory()
    })

    return {
      columns,
      data,
      visible,
      currentRecord,
      messages,
      showDetail,
      handleOk,
      handleCancel,
    }
  }
}
</script>

<style scoped>

</style>
