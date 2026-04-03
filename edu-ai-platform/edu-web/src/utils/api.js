const BASE_URL = '/api'

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
          reject(new Error(res.data.message))
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
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
