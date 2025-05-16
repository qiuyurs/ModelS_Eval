<template>
    <a-row>
        <h2>多模型评测</h2>
        <a-divider />

        <a-col :span="12">
            <a-space>
                评测模型A
                <a-select v-model="selectedModelA" :style="{ width: '100%' }" placeholder="请选择需要评测的模型" allow-search
                    @change="handleModelChange('A')">
                    <a-option v-for="model in models" :key="model.id" :value="model.id">
                        {{ model.model_name }}
                    </a-option>
                </a-select>
            </a-space>
            <ChatRecord :chatHistory="messagesA" style="margin-top: 12px;" />
        </a-col>
        <a-col :span="12">
            <a-space>
                评测模型A
                <a-select v-model="selectedModelB" :style="{ width: '100%' }" placeholder="请选择需要评测的模型" allow-search
                    @change="handleModelChange('B')">
                    <a-option v-for="model in models" :key="model.id" :value="model.id">
                        {{ model.model_name }}
                    </a-option>
                </a-select>
            </a-space>
            <ChatRecord :chatHistory="messagesB" style="margin-top: 12px;" />
        </a-col>
        <a-col :span="24" style="margin-top: 30px; display: flex; justify-content: center;">
            <a-input-group style="width: 80%;">
                <a-select v-model="messageRole" :style="{ width: '120px', height: '45px' }" placeholder="角色">
                    <a-option value="system">系统</a-option>
                    <a-option value="user">用户</a-option>
                </a-select>
                <a-input-search v-model="userMessage" placeholder="请输入要发送的消息" button-text="发送" search-button
                    @search="handleSendMessage" @press-enter="handleSendMessage" :style="{ flex: 1, height: '45px' }" />
            </a-input-group>
        </a-col>
    </a-row>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import ChatRecord from '../../components/ChatRecord.vue';
import axios from '@/utils/request';

export default {
    components: { ChatRecord },
    setup() {
        const messagesA = ref([]);
        const messagesB = ref([]);
        const models = ref([]);
        const selectedModelA = ref(null);
        const selectedModelB = ref(null);
        const messageRole = ref('user');
        const userMessage = ref('');
        const loadingA = ref(false);
        const loadingB = ref(false);




        async function fetchModels() {
            try {
                const response = await axios.get('/api/models');
                models.value = response.data;
            } catch (error) {
                Message.error('请求失败：' + (error.response?.data?.message || error.message));
            }
        }

        const handleModelChange = (type) => {
            if (type === 'A') {
                console.log('Selected Model A:', selectedModelA.value);
            } else {
                console.log('Selected Model B:', selectedModelB.value);
            }
        };

        async function sendMessageToModel(type) {
            const loading = type === 'A' ? loadingA : loadingB;
            const messages = type === 'A' ? messagesA : messagesB;
            const modelId = type === 'A' ? selectedModelA.value : selectedModelB.value;

            if (!modelId) return;

            loading.value = true;
            try {
                const response = await fetch('/api/models/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        model_ids: [modelId],
                        chatHistory: messages.value,
                        stream: true
                    })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let aiResponse = { role: 'assistant', content: '' };

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
                                if (data.response) {
                                    aiResponse.content += data.response;
                                    // 强制触发响应式更新
                                    const temp = [...messages.value];
                                    if (temp.length > 0 &&
                                        temp[temp.length - 1].role === 'assistant') {
                                        temp[temp.length - 1].content = aiResponse.content;
                                    } else {
                                        temp.push({ ...aiResponse });
                                    }
                                    messages.value = temp;
                                }
                            } catch (e) {
                                console.error('解析SSE数据出错:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                if (error instanceof TypeError) {
                    Message.error('网络请求失败：请检查网络连接');
                } else if (error.response) {
                    Message.error(`API请求失败：${error.response.data.message || '未知错误'}`);
                } else if (error.message) {
                    Message.error(`请求失败：${error.message}`);
                } else {
                    Message.error('请求失败：未知错误');
                }
            } finally {
                loading.value = false;
            }
        }

        const handleSendMessage = () => {
            if (!userMessage.value.trim()) return;

            // 检查是否选择了模型
            if (messageRole.value === 'user' && !selectedModelA.value && !selectedModelB.value) {
                Message.error('请至少选择一个评测模型');
                return;
            }

            const msg = { role: messageRole.value, content: userMessage.value };
            messagesA.value.push(msg);
            messagesB.value.push(msg);
            userMessage.value = '';

            // 只有用户消息才触发模型请求
            if (messageRole.value === 'user') {
                if (selectedModelA.value) sendMessageToModel('A');
                if (selectedModelB.value) sendMessageToModel('B');
            }

            // 发送后自动切换回用户角色并禁用系统角色
            if (messageRole.value === 'system') {
                messageRole.value = 'user';
                document.querySelector('.system-option').style.display = 'none';
            }


        };

        onMounted(() => {
            fetchModels();
        });

        return {
            messagesA,
            messagesB,
            models,
            selectedModelA,
            selectedModelB,
            userMessage,
            loadingA,
            loadingB,
            handleModelChange,
            handleSendMessage,
            messageRole
        };
    }
};
</script>