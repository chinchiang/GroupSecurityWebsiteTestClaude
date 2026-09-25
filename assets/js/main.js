// 行動版導覽開關 + 目前頁面高亮 + 程式碼區塊複製按鈕
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? '關閉選單' : '開啟選單');
    };
    toggle.addEventListener('click', function () {
      setOpen(!nav.classList.contains('open'));
    });
    // Esc 關閉選單並把焦點還給按鈕；點選連結後自動收合
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        setOpen(false);
        toggle.focus();
      }
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
  }

  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.site-nav a').forEach(function (a) {
    if (a.getAttribute('href') === here) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
  });

  // 附錄 F 的 Prompt／範本與文字架構圖：加上「複製」按鈕
  if (!navigator.clipboard) return;
  document.querySelectorAll('pre.ascii').forEach(function (pre) {
    var wrap = document.createElement('div');
    wrap.className = 'code-wrap';
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn';
    btn.textContent = '複製';
    btn.setAttribute('aria-label', '複製此區塊內容');
    wrap.appendChild(btn);

    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(pre.textContent).then(function () {
        btn.textContent = '已複製';
      }, function () {
        btn.textContent = '複製失敗';
      }).then(function () {
        setTimeout(function () { btn.textContent = '複製'; }, 2000);
      });
    });
  });
})();
