<template>
  <view class="register-container">
    <view class="register-box">
      <view class="title">注册账号</view>
      <view class="subtitle">开启您的智能学习之旅</view>
      
      <view class="form">
        <view class="form-item">
          <input 
            class="input" 
            type="text" 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
          />
        </view>
        <view class="form-item">
          <input 
            class="input" 
            type="email" 
            v-model="registerForm.email" 
            placeholder="请输入邮箱"
          />
        </view>
        <view class="form-item">
          <input 
            class="input" 
            type="password" 
            v-model="registerForm.password" 
            placeholder="请输入密码"
          />
        </view>
        <view class="form-item">
          <input 
            class="input" 
            type="password" 
            v-model="registerForm.confirmPassword" 
            placeholder="请确认密码"
            @confirm="handleRegister"
          />
        </view>
        
        <button class="btn-register" :loading="loading" @click="handleRegister">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <view class="links">
          <text @click="goToLogin">已有账号？立即登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { register } from '@/utils/api'

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)

const handleRegister = async () => {
  if (!registerForm.value.username) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!registerForm.value.email) {
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }
  if (!registerForm.value.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return
  }
  if (registerForm.value.password.length < 6) {
    uni.showToast({ title: '密码长度至少6位', icon: 'none' })
    return
  }
  
  loading.value = true
  
  try {
    await register({
      username: registerForm.value.username,
      password: registerForm.value.password,
      email: registerForm.value.email
    })
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/login/index' })
    }, 1000)
  } catch (error) {
    uni.showToast({ title: error.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  uni.navigateBack()
}
</script>

<style>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
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
  margin-bottom: 16px;
}

.input {
  width: 100%;
  height: 44px;
  padding: 0 15px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
}

.btn-register {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  line-height: 44px;
  text-align: center;
  margin-top: 10px;
}

.btn-register[loading] {
  opacity: 0.7;
}

.links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #667eea;
}
</style>
