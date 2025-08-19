// 原有的tab功能
document.querySelectorAll('[data-arc-tabs]').forEach(group=>{
  const tabs = group.querySelectorAll('.arc-tab');
  const panes = group.querySelectorAll('.arc-tabpane');
  tabs.forEach((tab,idx)=>{
    tab.addEventListener('click',()=>{
      tabs.forEach(t=>t.classList.remove('active'));
      panes.forEach(p=>p.classList.remove('active'));
      tab.classList.add('active');
      panes[idx].classList.add('active');
    });
  });
});

// 导航栏tab激活状态处理
document.addEventListener('DOMContentLoaded', function() {
  const currentPath = window.location.pathname;
  const navTabs = document.querySelectorAll('.nav-tab');
  
  // 移除所有active状态
  navTabs.forEach(tab => tab.classList.remove('active'));
  
  // 根据当前路径激活相应的tab
  navTabs.forEach(tab => {
    const href = tab.getAttribute('href');
    const tabType = tab.getAttribute('data-tab');
    
    // 精确匹配路径来激活对应的tab
    if (
      (tabType === 'home' && (currentPath === '/dashboard/' || currentPath === '/dashboard' || currentPath === '/')) ||
      (tabType === 'worklog' && currentPath.startsWith('/work/')) ||
      (tabType === 'reports' && currentPath.startsWith('/reports/'))
    ) {
      tab.classList.add('active');
    }
  });
});
