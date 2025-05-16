<template>
  <h2>添加模型</h2>
  <a-divider />
  <a-form :model="form" :style="{ width: '800px' }" @submit="handleSubmit">
    <!-- 厂商选择 -->
    <a-form-item field="makers" label="厂商选择" required>
      <a-select 
        v-model="form.makers" 
        placeholder="请选择厂商"
        @change="handleVendorChange"
      >
        <a-option value="OpenAI">OpenAI</a-option>
        <a-option value="DeepSeek">DeepSeek</a-option>
        <a-option value="Qwen">阿里云百炼</a-option>
        <a-option value="智谱清言">智谱清言</a-option>
        <a-option value="火山方舟">火山方舟</a-option>
        <a-option value="腾讯混元">腾讯混元</a-option>
        <a-option value="OpenAI兼容">OpenAI兼容</a-option>
      </a-select>
    </a-form-item>

    <!-- 模型代码 -->
    <a-form-item field="model" label="模型代码" required>
      <a-space direction="vertical" fill>
        <a-input
          v-model="form.model"
          placeholder="请输入模型代码"
          allow-clear
          @input="handleModelInput"
        />
        <a-alert v-if="showCustomModelAlert" type="info" show-icon>
          请确保输入的模型代码正确
        </a-alert>
      </a-space>
    </a-form-item>

    <!-- 模型名称 -->
    <a-form-item field="model_name" label="模型名称" required>
      <a-input 
        v-model="form.model_name" 
        placeholder="请输入模型名称"
      />
    </a-form-item>

    <!-- API密钥 -->
    <a-form-item field="api_key" label="API密钥" required>
      <a-input-password v-model="form.api_key" placeholder="请输入API密钥" />
    </a-form-item>
    
    <a-form-item field="base_url" label="基础URL" required>
      <a-input v-model="form.base_url" placeholder="将根据厂商自动填充" :readonly="form.makers !== 'OpenAI兼容'" />
    </a-form-item>
    
    <a-form-item field="supports" label="支持功能">
      <a-checkbox-group v-model="supports">
        <a-checkbox value="image">图片</a-checkbox>
        <a-checkbox value="video">视频</a-checkbox>
        <a-checkbox value="audio">音频</a-checkbox>
      </a-checkbox-group>
    </a-form-item>
    
    <a-form-item field="is_active" label="启用模型">
      <a-switch v-model="form.is_active" :default-checked="true" />
    </a-form-item>
    
    <a-form-item>
      <a-space>
        <a-button 
          type="primary" 
          html-type="submit" 
          size="large"
          :style="{ width: '120px', height: '40px' }"
        >
          提交
        </a-button>
        <a-button 
          @click="resetForm" 
          size="large"
          :style="{ width: '120px', height: '40px' }"
        >
          重置
        </a-button>
      </a-space>
    </a-form-item>
  </a-form>
</template>

<script>
import { reactive, computed, ref } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

axios.defaults.baseURL = 'http://127.0.0.1:26000';

const vendorMap = {
  'OpenAI': { url: 'https://api.openai.com/v1', id: 1 },
  'DeepSeek': { url: 'https://api.deepseek.com/v1', id: 2 },
  'Qwen': { url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', id: 3 },
  '智谱清言': { url: 'https://open.bigmodel.cn/api/paas/v4/', id: 4 },
  '火山方舟': { url: 'https://ark.cn-beijing.volces.com/api/v3', id: 5 },
  '腾讯混元': { url: 'https://api.hunyuan.cloud.tencent.com/v1', id: 6 },
  'OpenAI兼容': { url: '', id: 7 }
};


export default {
  setup() {
    const router = useRouter();
    const form = reactive({
      model: '',
      model_name: '',
      api_key: '',
      base_url: '',
      makers: '',
      makers_id: 0,
      supports_image: false,
      supports_video: false,
      supports_audio: false,
      is_active: true
    });
    const showCustomModelAlert = ref(false);
    
    const supports = computed({
      get() {
        return [
          form.supports_image ? 'image' : null,
          form.supports_video ? 'video' : null,
          form.supports_audio ? 'audio' : null
        ].filter(Boolean);
      },
      set(values) {
        form.supports_image = values.includes('image');
        form.supports_video = values.includes('video');
        form.supports_audio = values.includes('audio');
      }
    });

    const handleModelSearch = (inputValue) => {
      if (inputValue) {
        const isPredefined = modelOptions.some(opt => 
          opt.children.some(child => child.value === inputValue)
        );
        showCustomModelAlert.value = !isPredefined || form.model === 'custom';
        if (!isPredefined || form.model === 'custom') {
          form.model = inputValue;
          form.model_name = inputValue;
        }
      }
    };

    const handleSubmit = async () => {
      try {
        const response = await service.post('/api/models', {
          model: form.model,
          model_name: form.model_name,
          api_key: form.api_key,
          base_url: form.base_url,
          makers: form.makers,
          makers_id: form.makers_id,
          supports_image: form.supports_image,
          supports_video: form.supports_video,
          supports_audio: form.supports_audio,
          is_active: form.is_active
        });
        
        if (!response || !response.data) {
          Message.error('添加失败: 服务器未返回有效响应');
          return;
        }
        
        if (response.data.status === 'success') {
          Message.success(response.data.message);
          resetForm();
          router.push('/ModelList');
        } else {
          Message.error(response.data.message || '添加失败');
        }
      } catch (error) {
        Message.error('添加失败: ' + (error.response?.data?.message || error.message));
      }
    };

    const handleVendorChange = (value) => {
      if (value && vendorMap[value]) {
        form.base_url = vendorMap[value].url;
        form.makers_id = vendorMap[value].id; // 保留后台赋值逻辑
      }
    };

    const resetForm = () => {
      Object.keys(form).forEach(key => {
        if (key === 'is_active') {
          form[key] = true;
        } else if (key === 'makers_id') {
          form[key] = 0;
        } else {
          form[key] = '';
        }
      });
      supports.value = [];
    };

    const handleModelInput = (value) => {
      form.model = value;
      showCustomModelAlert.value = !!value;
    };

    return {
      showCustomModelAlert,
      form,
      supports, // 确保返回supports
      handleModelSearch,
      handleSubmit, // 确保返回handleSubmit
      handleVendorChange,
      resetForm
    };
  }
};
</script>

<style scoped>
.a-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.a-form-item {
  margin-bottom: 20px;
}

.a-button {
  font-weight: 500;
  letter-spacing: 0.5px;
}
</style>