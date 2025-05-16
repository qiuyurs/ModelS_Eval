<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
</script>

<template>
  <a-row class="grid-demo">
    <a-col :span="4">
      <a-menu
        :style="{ height: '100%', width: '100%' }"
        :default-open-keys="['0']"
        :default-selected-keys="['0_2']"
        breakpoint="md"
      >
        <a-sub-menu key="0">
          <template #title>
            <icon-computer />
            评测
          </template>
          <a-menu-item key="0_0" @click="$router.push('/ModelComparison2')">
            <icon-computer />
            模型评测
          </a-menu-item>
          <a-menu-item key="0_1" @click="$router.push('/ModelComparison')">
            <icon-branch />
            多模型评测
          </a-menu-item>
        </a-sub-menu>
        <a-sub-menu key="1">
          <template #title>
            <icon-settings />
            设置</template>
          <!-- <a-menu-item key="1_0" @click="$router.push('/addModel')">
            <icon-plus />
            添加模型
          </a-menu-item> -->
          <a-menu-item key="2_0" @click="$router.push('/ModelList')">
            <icon-list />
            模型列表
          </a-menu-item>
          <a-menu-item key="2_1" @click="$router.push('/ModelHistory')">
            <icon-list />
            请求记录
          </a-menu-item>
          <a-menu-item key="2_2" @click="$router.push('/DatasetList')">
            <icon-list />
            测试数据集

          </a-menu-item>
        </a-sub-menu>
      </a-menu>
      <div style="padding: 16px; color: var(--color-text-3); font-size: 12px;">
        <a href="#" style="color: var(--color-text-3);">技术支持微信：qrecyc</a><br>
        <a href="mailto:qiuyurs@163.com" style="color: var(--color-text-3);">技术支持邮箱：qiuyurs@163.com</a><br>
        <a href="https://github.com/qiuyurs/ModelS_Eval" target="_blank" style="color: var(--color-text-3);">GitHub</a>
        <a href="https://gwl1554ppni.feishu.cn/wiki/Z3t1w1514ix81AkeQirceTp6nww" target="_blank" style="color: var(--color-text-3);">帮助文档</a>
      </div>
    </a-col>
    <a-col :span="1">
    </a-col>
    <a-col :span="18" style="background-color: #fff; padding:1.5%;">
      <RouterView />
    </a-col>
  </a-row>
</template>

<script>
export default {
  computed: {
  },
  watch: {
    '$route' (to) {
      document.title = to.meta?.title + ' - ModelCompareX 大模型评测' || 'ModelCompareX 大模型评测'
    }
  }
};
</script>

<style scoped>
.grid-demo {
  min-height: 100vh;
  
}

.menu-demo {
  box-sizing: border-box;
  width: 100%;
  /* height: 600px; */
  padding: 40px;
  background-color: var(--color-neutral-2);
}
</style>
