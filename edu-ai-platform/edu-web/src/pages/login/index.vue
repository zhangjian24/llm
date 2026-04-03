<template>
  <view class="login-container">
    <view class="login-box">
      <view class="title">AI教育平台</view>
      <view class="subtitle">智能学习，从这里开始</view>
      
      <view class="form">
        <view class="form-item">
          <input 
            class="input" 
            type="text" 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
          />
        </view>
        <view class="form-item">
          <input 
            class="input" 
            type="password" 
            v-model="loginForm.password" 
            placeholder="请输入密码"
            @confirm="handleLogin"
          />
        </view>
        
        <button class="btn-login" :loading="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <view class="links">
          <text @click="goToRegister">还没有账号？立即注册</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '@/utils/api'

const loginForm = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!loginForm.value.username) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!loginForm.value.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  
  loading.value = true
  
  try {
    const res = await login(loginForm.value)
    if (res.token) {
      uni.setStorageSync('token', res.token)
      uni.setStorageSync('userInfo', res.userInfo)
      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1000)
    }
  } catch (error) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  uni.navigateTo({ url: '/pages/register/index' })
}
</script>

<style>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 320px;
  padding: 40px 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  text-align: center;
  color: #999;
  margin-bottom: 30px;
}

.form-item {
  margin-bottom: 20px;
}

.input {
  width: 100%;
  height: 44px;
  padding: 0 15px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
}

.btn-login {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  line-height: 44px;
  text-align: center;
}

.btn-login[loading] {
  opacity: 0.7;
}

.links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #667eea;
}
</style>
