const WHITE_LIST = ['/pages/login/index', '/pages/register/index']

export const authGuard = (to) => {
  const token = uni.getStorageSync('token')
  
  if (!token && !WHITE_LIST.includes(to)) {
    uni.redirectTo({
      url: '/pages/login/index'
    })
    return false
  }
  
  if (token && (to === '/pages/login/index' || to === '/pages/register/index')) {
    uni.switchTab({
      url: '/pages/index/index'
    })
    return false
  }
  
  return true
}

export const checkAuth = () => {
  const token = uni.getStorageSync('token')
  return !!token
}

export const getToken = () => {
  return uni.getStorageSync('token')
}

export const getUserInfo = () => {
  return uni.getStorageSync('userInfo')
}
