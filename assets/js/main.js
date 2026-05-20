/* ─── SHARED NAV & UTILITIES ─────────────────────────────────── */
;(function () {

  function reinit() {
    // Sticky nav border on scroll
    const nav = document.getElementById('nav');
    if (nav) {
      if (window._navScroll) window.removeEventListener('scroll', window._navScroll);
      const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
      window._navScroll = onScroll;
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });

      // Mobile nav toggle
      const toggle = document.getElementById('navToggle');
      if (toggle) {
        toggle.addEventListener('click', () => {
          const open = nav.classList.toggle('is-open');
          toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        document.querySelectorAll('.nav__links a').forEach(a => {
          a.addEventListener('click', () => {
            nav.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
          });
        });
      }

      // Active nav link based on current path (SPA routing)
      const currentPath = location.pathname.replace(/\/$/, '') || '/';
      document.querySelectorAll('.nav__links a:not(.nav__cta)').forEach(a => {
        const href = (a.getAttribute('href') || '').replace(/\/$/, '') || '/';
        if (href === currentPath) a.classList.add('active');
      });
    }

    // Intersection Observer for scroll reveal
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    // Animated counter
    function animateCounter(el, target, duration = 1200) {
      const start = performance.now();
      const update = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(eased * target);
        if (progress < 1) requestAnimationFrame(update);
      };
      requestAnimationFrame(update);
    }

    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          animateCounter(el, parseInt(el.dataset.target, 10));
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

    // Toast notification
    function showToast(msg, type = '') {
      let toast = document.getElementById('toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.className = 'toast' + (type ? ' ' + type : '');
      requestAnimationFrame(() => toast.classList.add('show'));
      clearTimeout(toast._timer);
      toast._timer = setTimeout(() => toast.classList.remove('show'), 2400);
    }

    // Copy to clipboard
    document.querySelectorAll('[data-copy]').forEach(btn => {
      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(btn.dataset.copy);
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          showToast('Copied to clipboard', 'success');
          setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
        } catch {
          showToast('Could not copy — try manually');
        }
      });
    });

    // Stagger-in cards on load
    function staggerCards(selector, delayStep = 60) {
      document.querySelectorAll(selector).forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';
        el.style.transition = `opacity 400ms ease ${i * delayStep}ms, transform 400ms ease ${i * delayStep}ms`;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          el.style.opacity = '1';
          el.style.transform = 'none';
        }));
      });
    }

    // Lightbox
    let lightbox = document.getElementById('__lightbox');
    if (!lightbox) {
      lightbox = document.createElement('div');
      lightbox.id = '__lightbox';
      lightbox.className = 'lightbox';
      lightbox.innerHTML =
        '<button class="lightbox__close" aria-label="Close image">&times;</button>' +
        '<img class="lightbox__img" src="" alt="" />' +
        '<span class="lightbox__caption"></span>';
      document.body.appendChild(lightbox);
    }
    const lbImg     = lightbox.querySelector('.lightbox__img');
    const lbCaption = lightbox.querySelector('.lightbox__caption');
    const lbClose   = lightbox.querySelector('.lightbox__close');

    function openLightbox(src, caption) {
      lbImg.src = src;
      lbCaption.textContent = caption || '';
      lightbox.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }
    function closeLightbox() {
      lightbox.classList.remove('is-open');
      document.body.style.overflow = '';
    }
    lbClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
    if (window._lbKey) document.removeEventListener('keydown', window._lbKey);
    window._lbKey = e => { if (e.key === 'Escape') closeLightbox(); };
    document.addEventListener('keydown', window._lbKey);

    document.querySelectorAll('.card__img[data-lightbox]').forEach(el => {
      el.addEventListener('click', () => openLightbox(el.dataset.lightbox, el.dataset.caption || ''));
    });

    // Expose to page-specific inline scripts
    window.showToast = showToast;
    window.staggerCards = staggerCards;
    window.animateCounter = animateCounter;
  }

  reinit();
  window.__reinitMain = reinit;

})();
