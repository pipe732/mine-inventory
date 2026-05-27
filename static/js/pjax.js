(function () {
  var container = document.querySelector('main');
  var busy = false;

  function isSameOrigin(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.origin === window.location.origin;
  }

  function isPjaxLink(link) {
    if (!link || !link.href) return false;
    if (link.target && link.target !== '_self') return false;
    if (link.hasAttribute('download')) return false;
    if (link.dataset.noPjax !== undefined) return false;
    if (link.href.indexOf('#') !== -1 && link.pathname === window.location.pathname) return false;
    return isSameOrigin(link.href);
  }

  function createLoadingBar() {
    var bar = document.createElement('div');
    bar.id = 'pjax-loading-bar';
    bar.style.position = 'fixed';
    bar.style.top = '0';
    bar.style.left = '0';
    bar.style.right = '0';
    bar.style.height = '3px';
    bar.style.background = 'linear-gradient(90deg, rgba(9,77,146,0.9), rgba(196,144,10,0.9))';
    bar.style.transform = 'scaleX(0)';
    bar.style.transformOrigin = 'left';
    bar.style.transition = 'transform .25s ease';
    bar.style.zIndex = '2000';
    document.body.appendChild(bar);
    return bar;
  }

  var progressBar = createLoadingBar();

  function showProgress() {
    progressBar.style.transform = 'scaleX(0.05)';
    setTimeout(function () {
      progressBar.style.transform = 'scaleX(0.45)';
    }, 50);
  }

  function finishProgress() {
    progressBar.style.transform = 'scaleX(1)';
    setTimeout(function () {
      progressBar.style.transition = 'transform .2s ease, opacity .2s ease';
      progressBar.style.opacity = '0';
      setTimeout(function () {
        progressBar.style.transform = 'scaleX(0)';
        progressBar.style.opacity = '1';
        progressBar.style.transition = 'transform .25s ease';
      }, 220);
    }, 180);
  }

  function executeScripts(fragment) {
    var scripts = Array.from(fragment.querySelectorAll('script'));
    scripts.forEach(function (oldScript) {
      var script = document.createElement('script');
      if (oldScript.src) {
        script.src = oldScript.src;
        if (oldScript.async) script.async = true;
        if (oldScript.defer) script.defer = true;
      } else {
        script.textContent = oldScript.textContent;
      }
      Array.from(oldScript.attributes).forEach(function (attr) {
        script.setAttribute(attr.name, attr.value);
      });
      oldScript.parentNode.replaceChild(script, oldScript);
    });
  }

  function replaceContent(newDoc) {
    var newMain = newDoc.querySelector('main');
    if (!newMain || !container) {
      return false;
    }
    container.innerHTML = newMain.innerHTML;
    document.title = newDoc.title || document.title;
    window.scrollTo(0, 0);
    executeScripts(container);
    window.dispatchEvent(new CustomEvent('pjax:load', { detail: { url: window.location.href } }));
    window.dispatchEvent(new Event('DOMContentLoaded'));
    window.dispatchEvent(new Event('load'));
    return true;
  }

  function fetchPage(url, pushState) {
    if (busy) return;
    busy = true;
    showProgress();

    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-PJAX': 'true'
      },
      credentials: 'same-origin'
    })
    .then(function (response) {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.text();
    })
    .then(function (html) {
      var parser = new DOMParser();
      var newDoc = parser.parseFromString(html, 'text/html');
      if (!replaceContent(newDoc)) {
        window.location.href = url;
        return;
      }
      if (pushState) {
        window.history.pushState({ pjax: true }, '', url);
      }
    })
    .catch(function () {
      window.location.href = url;
    })
    .finally(function () {
      finishProgress();
      busy = false;
    });
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('a');
    if (!link || !isPjaxLink(link)) return;

    var url = link.href;
    if (url === window.location.href) return;

    event.preventDefault();
    fetchPage(url, true);
  });

  window.addEventListener('popstate', function (event) {
    if (event.state && event.state.pjax) {
      fetchPage(window.location.href, false);
    }
  });

  document.addEventListener('mouseover', function (event) {
    var link = event.target.closest('a');
    if (!link || !isPjaxLink(link)) return;
    if (link.dataset.prefetched) return;
    link.dataset.prefetched = 'true';
    fetch(link.href, {
      credentials: 'same-origin'
    }).catch(function () {});
  });
})();
