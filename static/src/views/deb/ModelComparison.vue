<script setup>
import { reactive, ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue';
// 配置颜色主题
const chartColors = [
    '#D4B8FF',  
    '#FFB8E2', 
    '#89C7FF', 
    '#FFF78A',  
    '#FFCBA8', 
    '#8BFFD1',  
    '#7AE8D9', 
    '#FF9AA2', 
    '#A8D8FF',  
]
import axios from 'axios';
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);

let chartLoading = ref(false); // 加载状态

onMounted(() => {
  fetchModels();
});
import ChatRecord from '../../components/ChatRecord.vue'; // 修改导入路径
import AddChatRecord from '../../components/AddChatRecord.vue'; // 修改导入路径

const systemPrompt = ref('');
const userPrompt = ref('');
const add_visible = ref(false);
const showDatasetModal = ref(false);
const datasets = ref([]);
const selectedDataset = ref(null);
const chatHistory = reactive([]);
const newChatRecord = reactive({
  content: '',
  Role: ''
});
const temperature = ref(1);
const top_p = ref(0.7);
const max_tokens = ref(4096);
const models = ref([]);
const selectedModels = ref([]);
const results = ref([]);

const updateChatHistory = () => {
  // 清空并重建聊天记录
  chatHistory.splice(0, chatHistory.length);

  // 添加系统提示词（如果有）
  if (systemPrompt.value) {
    chatHistory.push({
      role: 'system',
      content: systemPrompt.value
    });
  }

  // 添加手动添加的记录（过滤掉系统/用户记录）
  const manualRecords = chatHistory.filter(item =>
    item.role === 'assistant' || item.role === 'user'
  );
  chatHistory.push(...manualRecords);

  // 添加用户提示词（如果有）始终在最后
  if (userPrompt.value) {
    // 先移除可能已存在的用户提示词记录
    const userPromptIndex = chatHistory.findIndex(item =>
      item.role === 'user' && item.content === userPrompt.value
    );
    if (userPromptIndex > -1) {
      chatHistory.splice(userPromptIndex, 1);
    }
    chatHistory.push({
      role: 'user',
      content: userPrompt.value
    });
  }
};

const fetchModels = async () => {
  try {
    const response = await axios.get('/api/models');
    if (response.data.status === 'success') {
      models.value = response.data.data;
    }
  } catch (error) {
    console.error('获取模型列表失败:', error);
  }
};

const fetchDatasets = async () => {
  try {
    const response = await axios.get('/api/datasets');
    datasets.value = response.data;
  } catch (error) {
    console.error('获取数据集失败:', error);
  }
};

const loadDataset = (dataset) => {
  try {
    const messages = JSON.parse(dataset.messages);
    chatHistory.splice(0, chatHistory.length, ...messages);
    showDatasetModal.value = false;
  } catch (error) {
    console.error('加载数据集失败:', error);
  }
};

const startTest = async () => {
  try {
    chartLoading.value = true; // 开启加载状态
    console.log('开始测试，选中的模型:', selectedModels.value);
    // 清空之前的结果
    results.value = selectedModels.value.map(modelId => ({
      model_id: modelId,
      model_name: models.value.find(m => m.id === modelId)?.model_name || '',
      response: '',
      first_token_time: 0,
      total_time: 0,
      prompt_tokens: 0,
      completion_tokens: 0
    }));

    await Promise.all(selectedModels.value.map(async (modelId) => {
      console.log(`开始请求模型 ${modelId}`);
      const response = await fetch('/api/models/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model_ids: [modelId],
          chatHistory: chatHistory.map(item => ({
            role: item.role,
            content: item.content
          })),
          temperature: temperature.value,
          top_p: top_p.value,
          max_tokens: max_tokens.value,
          stream: true
        })
      });

      if (!response.ok) {
        console.error(`模型 ${modelId} 请求失败`, response.status);
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              console.log('收到SSE数据:', data);
              const resultIndex = results.value.findIndex(r => r.model_id === data.model_id);
              if (resultIndex !== -1) {
                if (data.response) {
                  results.value[resultIndex].response =
                    (results.value[resultIndex].response || '') + data.response;
                }
                if (data.first_token_time) {
                  results.value[resultIndex].first_token_time = data.first_token_time;
                }
                if (data.total_time) {
                  results.value[resultIndex].total_time = data.total_time;
                }
                if (data.prompt_tokens !== undefined) {
                  results.value[resultIndex].prompt_tokens = data.prompt_tokens;
                }
                if (data.completion_tokens !== undefined) {
                  results.value[resultIndex].completion_tokens = data.completion_tokens;
                }
              }
            } catch (e) {
              console.error('解析SSE数据出错:', e);
            }
          }
        }
      }
    }));
  } catch (error) {
    console.error('测试请求失败:', error);
  } finally {
    chartLoading.value = false; // 关闭加载状态
  }
};

onMounted(() => {
  fetchModels();
  fetchDatasets();
});

const chartInstance = ref(null);

const showResults = ref(false);
const showAnalysis = ref(false);

// 修改watch监听results变化
watch(results, (newVal) => {
  if (newVal.length > 0 && newVal.every(r => r.response)) {
    showResults.value = true;
    showAnalysis.value = true;
    // 使用nextTick确保DOM更新后再渲染图表
    nextTick(() => {
      renderCharts();
    });
  }
}, { deep: true });

const renderCharts = () => {
  nextTick(() => {
    if (!document.getElementById('firstTokenChart')) {
      console.error('图表容器未找到');
      return;
    }

    // 准备数据
    const validResults = results.value.filter(r => r.model_name);
    const modelNames = validResults.map(r => r.model_name);
    const firstTokenTimes = validResults.map(r => [parseFloat(r.first_token_time.toFixed(2))]);
    const totalTimes = validResults.map(r => [parseFloat(r.total_time.toFixed(2))]);
    const completionTokens = validResults.map(r => [r.completion_tokens]);
    const outputSpeeds = validResults.map(r => [parseFloat((r.completion_tokens / r.total_time).toFixed(2))]);

    // 销毁旧图表
    if (chartInstance.value) {
      chartInstance.value.forEach(chart => chart.dispose());
    }
    chartInstance.value = [];

    // 创建图表容器
    const chartContainers = [
      { id: 'firstTokenChart', title: '首字耗时对比(秒)', data: firstTokenTimes, yAxisName: '时间(秒)', max: Math.max(...firstTokenTimes.map(v => v[0])) * 1.3 },
      { id: 'totalTimeChart', title: '总耗时对比(秒)', data: totalTimes, yAxisName: '时间(秒)', max: Math.max(...totalTimes.map(v => v[0])) * 1.3 },
      { id: 'tokenChart', title: '生成Token数对比', data: completionTokens, yAxisName: 'Token数', max: Math.max(...completionTokens.map(v => v[0])) * 1.3 },
      { id: 'speedChart', title: '输出速度对比(tokens/s)', data: outputSpeeds, yAxisName: '输出速度(tokens/s)', max: Math.max(...outputSpeeds.map(v => v[0])) * 1.3 }
    ];

    // 创建并渲染每个图表
    chartContainers.forEach((container, chartIndex) => {
      const chartDom = document.getElementById(container.id);
      if (!chartDom) return;

      const chart = echarts.init(chartDom);
      chartInstance.value.push(chart);

      // 系列配置
    const seriesConfig = [{
      type: 'bar',
      barWidth: '30%',
      itemStyle: { 
        borderRadius: [4, 4, 0, 0],
        color: function(params) {
          return chartColors[params.dataIndex % chartColors.length];
        }
      },
      data: container.data.map(d => d[0])
    },
    {
      type: 'line',
      symbol: 'circle',
      symbolSize: 10,
      lineStyle: {
        width: 3,
        color: '#8ec1ff'
      },
      label: {
        show: true,
        position: 'top',
        formatter: ({ value }) => parseFloat(value).toFixed(2),
        color: '#333',
        fontSize: 12,
        fontWeight: 'bold'
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          color: '#8ec1ff'
        }
      },
      data: container.data.map(d => d[0]),
      showSymbol: true,
      itemStyle: {
        color: '#8ec1ff',
        borderColor: '#fff',
        borderWidth: 2
      }
    }];

      const option = {
        backgroundColor: '#f8fafc',
        title: {
          text: container.title,
          left: 'center',
          textStyle: { color: '#5b8ff9' },
          
          subtextStyle: {
            color: '#666',
            fontSize: 12,
            padding: [10, 0, 0, 0]
          }
        },
        tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'none' },
        formatter: function(params) {
          if (params && params[1] && params[1].value !== undefined) {
            return `${container.title}: ${params[1].value}`;
          }
          return '';
        }
      },
        legend: { show: false },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: { interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: container.yAxisName,
          min: 0,
          max: Math.max(...container.data.map(d => d[0])) * 1.3,
          axisLine: { show: true },
          axisLabel: {
            formatter: function (value) {
              return parseFloat(value).toFixed(2);
            }
          }
        },
        series: seriesConfig
      };

      // 打印调试信息
      console.log(`图表 ${container.id} 的完整配置：`, option);
      chart.setOption(option);
    });

    // 响应式调整
    window.addEventListener('resize', () => {
      nextTick(() => {
        chartInstance.value.forEach(chart => {
          if (!chart.isDisposed()) chart.resize();
        });
      });
    });
  });
};

// 图表容器初始化
const initCharts = () => {
  if (!document.getElementById('firstTokenChart')) {
    console.error('图表容器未找到');
    return;
  }

  console.log('开始初始化图表，检查ECharts:', echarts);

  // 销毁旧图表
  if (chartInstance.value) {
    console.log('销毁旧图表实例');
    chartInstance.value.forEach(chart => chart.dispose());
  }

  console.log('准备重新渲染图表');
  renderCharts();
};

// 监听results变化刷新图表
watch(results, (newVal, oldVal) => {
  if (newVal.length > 0 && newVal.every(r => r.response)) {
    showResults.value = true;
    showAnalysis.value = true;

    // 数据稳定后停止刷新
    const isDataStable = oldVal &&
      newVal.length === oldVal.length &&
      newVal.every((r, i) =>
        r.response === oldVal[i]?.response &&
        r.first_token_time === oldVal[i]?.first_token_time &&
        r.total_time === oldVal[i]?.total_time
      );

    if (!isDataStable) setTimeout(initCharts, 2000);
  }
}, { deep: true });

// 响应式调整
window.addEventListener('resize', () => {
  if (chartInstance.value?.length) {
    nextTick(() => {
      chartInstance.value.forEach(chart => chart.resize());
    });
  }
});

// 组件卸载时清理图表
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.forEach(chart => chart.dispose());
  }
});
</script>

<template>
  <!-- 添加聊天记录对话框 -->
  <a-modal v-model:visible="add_visible" title="添加聊天记录" @cancel="add_visible = false">
    <AddChatRecord :visible="add_visible" :chatHistory="chatHistory" :newChatRecord="newChatRecord"
      @update:visible="val => add_visible = val" @submit="updatedChatHistory => {
        chatHistory.splice(0, chatHistory.length, ...updatedChatHistory);
        add_visible = false;
      }" />
  </a-modal>

  <!-- 加载数据集对话框 -->
  <a-modal v-model:visible="showDatasetModal" title="加载数据集" @cancel="showDatasetModal = false" @ok="() => loadDataset(selectedDataset)">
    <a-select
      v-model="selectedDataset"
      placeholder="请选择数据集"
      allow-search
      :filter-option="false"
      @search="fetchDatasets"
      style="width: 100%"
    >
      <a-option v-for="dataset in datasets" :key="dataset.id" :value="dataset">
        {{ dataset.name }}
      </a-option>
    </a-select>
  </a-modal>

  <!-- 主界面 -->
  <h2>大模型能力测试</h2>
  <a-divider />
  <a-row>
    <a-col :span="15">
      <ChatRecord :chatHistory="chatHistory">
        <template #actions>
          <a-button type="primary" @click="showDatasetModal = true" style="margin-left: 10px;">加载数据集</a-button>
          <a-button type="primary" @click="add_visible = true">添加对话</a-button>
          <AddChatRecord :visible="add_visible" :chatHistory="chatHistory" :newChatRecord="newChatRecord"
            @update:visible="val => add_visible = val" @submit="updatedChatHistory => {
              chatHistory.splice(0, chatHistory.length, ...updatedChatHistory);
              chatHistory.push(); // 强制更新
              newChatRecord.content = '';
              newChatRecord.Role = 'assistant';
              add_visible = false;
            }" />
        </template>
      </ChatRecord>
    </a-col>
    <a-col :span="1"></a-col>
    <!-- 右侧测试设置 -->
    <a-col :span="8">
      
      <div>生成随机性 - temperature</div>
      <a-slider v-model="temperature" :min="0" :max="2" :step="0.1" />
      <div style="margin-top: 10px;">温度 - top_p</div>
      <a-slider v-model="top_p" :min="0" :max="1" :step="0.1" />
      <div style="margin-top: 10px;">最多回复Token - max_tokens</div>
      <a-input-number v-model="max_tokens" :min="1" :max="12800" style="margin-top: 10px;" />
      <div style="margin-top: 10px;"><h3>参与测试的大模型：</h3></div>
      <a-space direction="vertical" size="large" style="margin-top: 10px;">
        <a-checkbox-group v-model="selectedModels">
          <a-checkbox v-for="model in models" :key="model.id" :value="model.id">
            {{ model.model_name }}
          </a-checkbox>
        </a-checkbox-group>
      </a-space>
      <a-button style="margin-top: 10px;" type="primary" :long="true" @click="startTest" :loading="chartLoading">开始测试</a-button>
    </a-col>

    <a-col :span="24" style="margin-bottom: 5%;"></a-col>
  </a-row>

  <!-- 结果展示 -->
  <template v-if="showResults">
    <h2>大模型返回信息：</h2>
    <a-divider />
    <a-row :gutter="[16, 16]">
      <template v-for="(result, index) in results" :key="index">
        <a-col :span="12">
          <a-card :title="result.model_name" style="margin-bottom: 16px;">
            <a-row>
              <a-col :span="24" style="min-height: 100px;">
                <pre style="white-space: pre-wrap">{{ result.response }}</pre>
              </a-col>
              <a-col :span="24">
                <a-divider style="margin: 6px 0;" />
                <a-row :gutter="[8, 8]">
                  <!-- 降低监控信息字体大小和存在感 -->
                  <a-col :span="12" style="padding: 0;"><small>首字耗时: <strong>{{ result.first_token_time.toFixed(2) }}</strong> 秒</small></a-col>
                  <a-col :span="12" style="padding: 0;"><small>总耗时: <strong>{{ result.total_time.toFixed(2) }}</strong> 秒</small></a-col>
                  <a-col :span="12" style="padding: 0;"><small>请求Token: <strong>{{ result.prompt_tokens }}</strong></small></a-col>
                  <a-col :span="12" style="padding: 0;"><small>生成Token: <strong>{{ result.completion_tokens }}</strong></small></a-col>
                </a-row>
              </a-col>
            </a-row>
          </a-card>
        </a-col>
      </template>
    </a-row>

    <!-- 图表分析 -->
    <template v-if="showAnalysis">
      <h2>大模型数据监控：</h2>
      <a-divider />
      <a-row :gutter="[16, 16]">
        <a-col :span="12">
          <div id="firstTokenChart" :style="{ width: '100%', height: '400px' }"></div>
        </a-col>
        <a-col :span="12">
          <div id="totalTimeChart" :style="{ width: '100%', height: '400px' }"></div>
        </a-col>
        <a-col :span="12">
          <div id="tokenChart" :style="{ width: '100%', height: '400px' }"></div>
        </a-col>
        <a-col :span="12">
          <div id="speedChart" :style="{ width: '100%', height: '400px' }"></div>
        </a-col>
      </a-row>
    </template>
  </template>

  <!-- 加载动画 -->
  <a-spin v-if="chartLoading" dot tip="正在发起请求..." style="width: 100%;" />
</template>

<style scoped>
.markdown-container {
  line-height: 1.6;

  h1,
  h2,
  h3 {
    margin: 1em 0 0.5em;
    color: #1a73e8;
  }

  pre {
    margin: 1em 0;
    background: #f6f8fa;
    padding: 1em;
    border-radius: 4px;
    overflow-x: auto;
  }
}

/* 图表容器 */
.echarts {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}

small {
  font-size: 12px;
  color: #666;
}
</style>
