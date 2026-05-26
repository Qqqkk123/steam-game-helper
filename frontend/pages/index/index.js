Page({
  data: {
    appId: '',
    loading: false,
    gameInfo: null
  },

  // 监听输入
  onInputId(e) {
    this.setData({
      appId: e.detail.value.trim()
    });
  },

  // 发起对异步 Python 后端的网络请求
  queryGamePrice() {
    const { appId } = this.data;
    if (!appId) {
      wx.showToast({ title: '请输入AppID', icon: 'none' });
      return;
    }

    this.setData({ loading: true, gameInfo: null });

    // 关键点：真机或模拟器连本地电脑局域网 IP 或者 127.0.0.1
    // 注意：微信开发者工具里必须勾选「不校验合法域名」才能访问本地 http 后端
    wx.request({
      url: `http://127.0.0.1:8000/api/v1/games/price/${appId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ gameInfo: res.data });
          wx.showToast({ title: '获取成功', icon: 'success' });
        } else {
          // 处理 FastAPI 抛出的 404/502 等异常
          const errorMsg = res.data.detail || '游戏获取失败';
          wx.showModal({
            title: '查询提示',
            content: errorMsg,
            showCancel: false
          });
        }
      },
      fail: (err) => {
        wx.showModal({
          title: '网络连接失败',
          content: '无法连接到本地 Python 后端。请确认 FastAPI 是否已启动，且在开发者工具「详情->本地设置」中勾选了「不校验合法域名」',
          showCancel: false
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  subscribeGame() {
    wx.showToast({
      title: '功能属于 Sprint 2，敬请期待',
      icon: 'none'
    });
  }
});