<template>
  <view class="index-container">
    <view class="loading">Loading...</view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app'

onLoad(() => {
  const token = uni.getStorageSync('token')
  if (token) {
    uni.switchTab({
      url: '/pages/index/index'
    })
  } else {
    uni.redirectTo({
      url: '/pages/login/index'
    })
  }
})
</script>

<style>
.index-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.loading {
  font-size: 16px;
  color: #666;
}
</style>
