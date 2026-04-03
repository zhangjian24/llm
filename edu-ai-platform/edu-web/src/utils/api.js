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
          reject(new Error(res.data.message || '登录失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
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
          reject(new Error(res.data.message || '注册失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
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
          reject(new Error(res.data.message || '获取用户信息失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export const logout = () => {
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
  uni.switchTab({
    url: '/pages/login/index'
  })
}
