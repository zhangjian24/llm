# uni-app + TailwindCSS + uView Plus 环境搭建与登录注册实现

> 本文为 AI 教育平台系列博客第七/八篇，讲解 uni-app 前端环境搭建与 JWT 鉴权实现
> 
> 仓库地址：https://github.com/anomalyco/edu-ai-platform

---

## 一、背景

uni-app 是一个使用 Vue.js 开发跨平台应用的前端框架，本文详细介绍环境搭建与登录注册功能实现。

---

## 二、技术选型

### 2.1 核心框架

| 框架 | 版本 | 说明 |
|------|------|------|
| uni-app | 3.x | 跨端框架 |
| Vue | 3.4+ | 响应式框架 |
| Vite | 5.x | 构建工具 |
| TailwindCSS | 3.4+ | 原子化CSS |

### 2.2 项目结构

```
edu-web/
├── src/
│   ├── pages/
│   │   ├── index/           # 首页
│   │   ├── login/           # 登录页
│   │   └── register/        # 注册页
│   ├── components/          # 组件
│   ├── utils/
│   │   ├── api.js           # API封装
│   │   └── auth.js          # 鉴权工具
│   ├── App.vue              # 根组件
│   ├── main.js              # 入口
│   └── pages.json           # 页面配置
├── public/                  # 静态资源
├── vite.config.js           # Vite配置
├── tailwind.config.js       # TailwindCSS配置
└── package.json
```

---

## 三、环境配置

### 3.1 package.json

```json
{
  "name": "edu-web",
  "version": "0.1.0",
  "dependencies": {
    "@dcloudio/uni-app": "^3.0.0",
    "@dcloudio/uni-components": "^3.0.0",
    "@dcloudio/uni-h5": "^3.0.0",
    "vue": "^3.4.21"
  },
  "devDependencies": {
    "@dcloudio/vite-plugin-uni": "^3.0.0",
    "tailwindcss": "^3.4.3",
    "sass": "^1.77.0",
    "vite": "^5.2.11"
  }
}
```

### 3.2 vite.config.js

```javascript
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

### 3.3 tailwind.config.js

```javascript
module.exports = {
  content: ['./src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2'
      }
    }
  },
  plugins: []
}
```

---

## 四、页面配置

### 4.1 pages.json

```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        "navigationStyle": "custom"
      }
    },
    {
      "path": "pages/login/index",
      "style": {
        "navigationBarTitleText": "登录",
        "navigationStyle": "custom"
      }
    },
    {
      "path": "pages/register/index",
      "style": {
        "navigationBarTitleText": "注册",
        "navigationStyle": "custom"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarBackgroundColor": "#F8F8F8"
  }
}
```

---

## 五、API 封装

### 5.1 请求封装

```javascript
// src/utils/api.js
const BASE_URL = '/api'

const getAuthHeader = () => {
  return {
    'Authorization': `Bearer ${uni.getStorageSync('token')}`
  }
}

export const login = (data) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/user/login`,
      method: 'POST',
      data,
      success: (res) => {
        if (res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message))
        }
      },
      fail: (err) => reject(err)
    })
  })
}

export const register = (data) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/user/register`,
      method: 'POST',
      data,
      success: (res) => {
        if (res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message))
        }
      },
      fail: (err) => reject(err)
    })
  })
}

export const getUserInfo = () => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/user/info`,
      method: 'GET',
      header: getAuthHeader(),
      success: (res) => {
        if (res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message))
        }
      },
      fail: (err) => reject(err)
    })
  })
}

export const logout = () => {
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
}
```

---

## 六、鉴权工具

### 6.1 路由守卫

```javascript
// src/utils/auth.js
const WHITE_LIST = ['/pages/login/index', '/pages/register/index']

export const authGuard = (to) => {
  const token = uni.getStorageSync('token')
  
  if (!token && !WHITE_LIST.includes(to)) {
    uni.redirectTo({ url: '/pages/login/index' })
    return false
  }
  
  if (token && (to === '/pages/login/index' || to === '/pages/register/index')) {
    uni.switchTab({ url: '/pages/index/index' })
    return false
  }
  
  return true
}

export const checkAuth = () => {
  return !!uni.getStorageSync('token')
}

export const getToken = () => {
  return uni.getStorageSync('token')
}
```

---

## 七、登录页面实现

### 7.1 登录页结构

```vue
<template>
  <view class="login-container">
    <view class="login-box">
      <view class="title">AI教育平台</view>
      <view class="form">
        <input v-model="loginForm.username" placeholder="用户名" />
        <input v-model="loginForm.password" type="password" placeholder="密码" />
        <button @click="handleLogin">登录</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '@/utils/api'

const loginForm = ref({ username: '', password: '' })

const handleLogin = async () => {
  try {
    const res = await login(loginForm.value)
    uni.setStorageSync('token', res.token)
    uni.setStorageSync('userInfo', res.userInfo)
    uni.switchTab({ url: '/pages/index/index' })
  } catch (error) {
    uni.showToast({ title: error.message, icon: 'none' })
  }
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
}
</style>
```

---

## 八、注册页面实现

### 8.1 注册页结构

```vue
<template>
  <view class="register-container">
    <view class="register-box">
      <view class="title">注册账号</view>
      <view class="form">
        <input v-model="registerForm.username" placeholder="用户名" />
        <input v-model="registerForm.email" placeholder="邮箱" />
        <input v-model="registerForm.password" type="password" placeholder="密码" />
        <input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" />
        <button @click="handleRegister">注册</button>
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

const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return
  }
  
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
    uni.showToast({ title: error.message, icon: 'none' })
  }
}
</script>
```

---

## 九、Token 存储策略

### 9.1 安全考虑

- Token 存储在 uni.setStorageSync()（本地存储）
- 生产环境建议加密存储
- 退出登录时清除 Token

### 9.2 Token 刷新机制

```javascript
// Token 刷新示例
const refreshToken = async () => {
  const refreshToken = uni.getStorageSync('refreshToken')
  const res = await uni.request({
    url: '/api/user/refresh',
    method: 'POST',
    data: { refreshToken }
  })
  uni.setStorageSync('token', res.data.token)
}
```

---

## 十、项目代码

完整代码见：
- [edu-web](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-web)
- [登录页面](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-web/src/pages/login)
- [API封装](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-web/src/utils/api.js)

---

## 十一、总结

uni-app 登录注册核心：
1. **API封装**：统一请求封装，Token管理
2. **路由守卫**：页面跳转鉴权控制
3. **Token存储**：本地存储与安全策略
4. **跨端兼容**：一套代码多端运行

---

**Sprint-01 总结**：v0.1 基础架构版已完成！

| 博客 | 状态 |
|------|------|
| 1. Spring Boot 3.x自动装配原理 | ✅ |
| 2. Nacos注册中心核心原理 | ✅ |
| 3. 教育平台Maven多模块设计 | ✅ |
| 4. Spring Boot + Nacos服务注册 | ✅ |
| 5. Spring Cloud Gateway核心原理 | ✅ |
| 6. Gateway + Nacos深度集成 | ✅ |
| 7. uni-app + TailwindCSS环境搭建 | ✅ |
| 8. uni-app登录注册与JWT鉴权 | ✅ |

---

**参考**：
- uni-app 3.x 官方文档
- Vite 5.x 构建工具
- TailwindCSS 3.4+
