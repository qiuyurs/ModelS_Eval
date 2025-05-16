<template>
  <h2>查看模型列表</h2>
  <a-divider />
  <a-button type="primary" @click="$router.push('/addModel')" style="margin-bottom: 16px">添加模型</a-button>
  
  <a-modal v-model:visible="visible" @ok="handleOk" @cancel="handleCancel" width="800px">
    <template #title>
      模型详情 - {{currentModel.model_name}}
    </template>
    <div>
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="模型ID">{{currentModel.id}}</a-descriptions-item>
        <a-descriptions-item label="模型代码">{{currentModel.model}}</a-descriptions-item>
        <a-descriptions-item label="模型名称">{{currentModel.model_name}}</a-descriptions-item>
        <a-descriptions-item label="厂商">{{currentModel.makers}}</a-descriptions-item>
        <a-descriptions-item label="API密钥">{{currentModel.api_key}}</a-descriptions-item>
        <a-descriptions-item label="基础URL">{{currentModel.base_url}}</a-descriptions-item>
        <a-descriptions-item label="支持功能">
          <a-space>
            <a-tag v-if="currentModel.supports_image" color="blue">图片</a-tag>
            <a-tag v-if="currentModel.supports_video" color="green">视频</a-tag>
            <a-tag v-if="currentModel.supports_audio" color="orange">音频</a-tag>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag v-if="currentModel.is_active" color="green">启用</a-tag>
          <a-tag v-else color="red">禁用</a-tag>
        </a-descriptions-item>
      </a-descriptions>
    </div>
  </a-modal>
  
  <a-table :columns="columns" :data="data">
    <template #supports="{ record }">
      <a-space>
        <a-button v-if="record.supports_image" type="outline" status="primary" size="mini">图片</a-button>
        <a-button v-if="record.supports_video" type="outline" status="success" size="mini">视频</a-button>
        <a-button v-if="record.supports_audio" type="outline" status="normal" size="mini">音频</a-button>
      </a-space>
    </template>
    <template #action="{ record }">
      <a-space>
        <a-button type="text" @click="showDetail(record)">查看详情</a-button>
        <a-button type="text" status="danger" @click="handleDelete(record)">删除</a-button>
      </a-space>
    </template>
    <template #is_active="{ record }">
      <a-space>
        <a-button
          v-if="record.is_active"
          type="outline"
          status="success"
          size="mini"
        >
          开启
        </a-button>
        <a-button
          v-else
          type="outline"
          status="danger"
          size="mini"
        >
          关闭
        </a-button>
      </a-space>
    </template>
  </a-table>
</template>

<script>
import { reactive, onMounted, h,ref } from 'vue'
import { Message, Button } from '@arco-design/web-vue'
import axios from '@/utils/request'

export default {
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
    title: '厂商',
    dataIndex: 'makers',
    key: 'makers'
  },
  {
    title: '多模态',
    dataIndex: 'supports',
    key: 'supports',
    slotName: 'supports'
    
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    slotName: 'is_active'
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    slotName: 'action'
  }
]

    const data = reactive([])


    const handleDelete = async (record) => {
      try {
        const result = await axios.delete(`/api/models/${record.id}`)
        if (result.status === 'success') {
          Message.success('删除成功')
          fetchModels() // 重新获取数据
        } else {
          Message.error('删除失败：' + result.message)
        }
      } catch (error) {
        Message.error('请求失败：' + error.message)
      }
    }

    async function fetchModels() {
      try {
        const result = await axios.get('/api/models')
        if (result.status === 'success') {
          data.splice(0, data.length, ...result.data)
        } else {
          Message.error('获取模型列表失败：' + result.message)
        }
      } catch (error) {
        Message.error('请求失败：' + error.message)
      }
    }

    onMounted(() => {
      fetchModels()
    })

    const visible = ref(false);
    const currentModel = ref({});
    
    const showDetail = (record) => {
      currentModel.value = record;
      visible.value = true;
    };
    
    const handleOk = () => {
      visible.value = false;
    };
    
    const handleCancel = () => {
      visible.value = false;
    };
    
    return {
      columns,
      data,
      handleDelete,
      visible,
      currentModel,
      showDetail,
      handleOk,
      handleCancel
    }
  }
}
</script>
