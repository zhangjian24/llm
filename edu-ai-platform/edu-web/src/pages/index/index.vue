<template>
  <view class="index-container">
    <view class="header">
      <view class="user-info">
        <image class="avatar" :src="userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
        <view class="info">
          <text class="nickname">{{ userInfo.nickname || userInfo.username || '用户' }}</text>
          <text class="username">@{{ userInfo.username }}</text>
        </view>
      </view>
      <view class="logout" @click="handleLogout">
        <text>退出</text>
      </view>
    </view>
    
    <view class="content">
      <view class="welcome">
        <text class="title">欢迎来到 AI 教育平台</text>
        <text class="desc">智能学习，从这里开始</text>
      </view>
      
      <view class="features">
        <view class="feature-item">
          <text class="icon">📚</text>
          <text class="label">课程学习</text>
        </view>
        <view class="feature-item">
          <text class="icon">📝</text>
          <text class="label">作业管理</text>
        </view>
        <view class="feature-item">
          <text class="icon">🤖</text>
          <text class="label">AI 助手</text>
        </view>
        <view class="feature-item">
          <text class="icon">📊</text>
          <text class="label">学习报告</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onShow } from 'vue'
import { getUserInfo, logout } from '@/utils/api'

const userInfo = ref({})

onShow(() => {
  const info = uni.getStorageSync('userInfo')
  if (info) {
    userInfo.value = info
  } else {
    loadUserInfo()
  }
})

const loadUserInfo = async () => {
  try {
    const info = await getUserInfo()
    userInfo.value = info
    uni.setStorageSync('userInfo', info)
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        logout()
      }
    }
  })
}
</script>

<style>
.index-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 60px 20px 20px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 30px;
  background-color: #fff;
}

.info {
  margin-left: 15px;
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
}

.username {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}

.logout {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
}

.logout text {
  color: #fff;
  font-size: 14px;
}

.content {
  padding: 40px 20px;
}

.welcome {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 20px;
}

.welcome .title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10px;
}

.welcome .desc {
  font-size: 14px;
  color: #666;
}

.features {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.feature-item {
  width: 48%;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.feature-item .icon {
  font-size: 30px;
  margin-right: 15px;
}

.feature-item .label {
  font-size: 16px;
  color: #333;
}
</style>
