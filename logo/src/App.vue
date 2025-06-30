<template>
  <div id="app" class="container mx-auto py-12 px-6 max-w-[893px]">
    <div class="text-4xl font-black p-5 my-6 text-center">
      <logo></logo>
    </div>
    <div class="text-2xl mb-6 text-center font-extrabold">
      <Description></Description>
    </div>
    <div id="nav">
      <div
        class="flex flex-col md:flex-row gap-2 md:gap-16 text-xl font-semibold items-center mb-12 justify-center relative"
      >
        <a href="javascript:window.history.back()" class="text-gray-300 hover:text-white cursor-pointer absolute left-0">
          ← 返回
        </a>
        <router-link to="/" class="pb">
          <span class="prefix">Porn</span>
          <span class="postfix">hub</span>
        </router-link>
        <router-link to="/vertical-ph" class="vph">
          <p class="prefix">Porn</p>
          <p class="postfix">hub</p>
        </router-link>
        <router-link to="/onlyfans">
          <span class="text-white">Only</span>
          <span class="text-[#00AFF0]">Fans</span>
        </router-link>
      </div>
    </div>
    <router-view />
    <footer class="text-center mt-8 text-gray-400 text-sm">
      <p>© 2025 lazytool made by 公众号@懒人搜索</p>
    </footer>
  </div>
</template>

<script setup>
import Logo from '@/components/Logo.vue';
import Description from '@/components/Description.vue';

const goBack = () => {
  window.history.back();
};
</script>
