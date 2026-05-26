Page({
  data: {
    watchlist: [],
    isRefreshing: false
  },

  // 每次切到这个页面时，触发自动刷新列表
  onShow() {
    this.fetchWatchlist();
  },

  fetchWatchlist() {
    wx.request({
      url: 'http://127.0.0.1:8000/api/v1/games/watchlist',
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ watchlist: res.data });
        }
      },
      fail: () => {
        wx.showToast({ title: '无法获取记录本', icon: 'none' });
      },
      complete: () => {
        this.setData({ isRefreshing: false });
      }
    });
  },

  // 下拉刷新支持
  onPullDownRefresh() {
    this.setData({ isRefreshing: true });
    this.fetchWatchlist();
  }
});