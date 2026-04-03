<template>
  <view class="app">
    <slot />
  </view>
</template>

<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style>
.app {
  min-height: 100vh;
}
page {
  background-color: #f5f5f5;
}
</style>