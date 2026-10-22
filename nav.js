(function(){
  const currentScript = document.currentScript;
  if (currentScript) {
    const languageScript = document.createElement('script');
    languageScript.src = new URL('language.js', currentScript.src).href;
    languageScript.onerror = () => console.error('The bilingual language switch could not be loaded.');
    document.head.appendChild(languageScript);
  }

  document.querySelectorAll('a[href]').forEach(link => {
    const target = link.getAttribute('href');
    if (target && /^(?:\.\.\/)?stories\.html(?:#.*)?$/i.test(target)) link.remove();
  });

  const translate = message => window.GI4CLanguage ? window.GI4CLanguage.translate(message) : message;

  // Mobile menu toggle
  const btn = document.querySelector('.menu-btn');
  const menu = document.querySelector('.mobile-menu');
  if(btn && menu){
    btn.addEventListener('click', () => {
      menu.classList.toggle('open');
      btn.setAttribute('aria-expanded', menu.classList.contains('open'));
    });
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }));
  }

  const contactForm = document.querySelector('[data-contact-form]');
  if (contactForm) {
    contactForm.addEventListener('submit', async event => {
      event.preventDefault();
      const message = contactForm.querySelector('[data-form-message]');
      const button = contactForm.querySelector('button[type="submit"]');
      const originalText = button.textContent;
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      button.disabled = true;
      button.textContent = translate('Sending...');
      message.textContent = '';

      try {
        const response = await fetch('/api/send-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            type: 'contact',
            name: contactForm.elements.name.value.trim(),
            email: contactForm.elements.email.value.trim(),
            subject: contactForm.elements.subject.value.trim(),
            message: contactForm.elements.message.value.trim(),
            website: contactForm.elements.website.value
          })
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.success) {
          throw new Error(result.error || translate('Your message could not be sent. Please email info@gi4c.org directly.'));
        }
        message.textContent = translate('Thank you. Your message was accepted for delivery to GI4C.');
        contactForm.reset();
      } catch (error) {
        message.textContent = error.name === 'AbortError'
          ? translate('Sending timed out. Please try again or email info@gi4c.org.')
          : (error.name === 'TypeError' ? translate('We could not reach GI4C’s email service. Please email info@gi4c.org.') : translate(error.message));
      } finally {
        clearTimeout(timeout);
        button.disabled = false;
        button.textContent = originalText;
      }
    });
  }

  // AI assistant is backed by the same-origin Node API used on the deployed site.
  const chat = document.querySelector('#ai-chat');
  const input = document.querySelector('#ai-input');
  const form = document.querySelector('#ai-form');

  if (form && chat && input) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const v = input.value.trim();
      if (!v) return;

      chat.insertAdjacentHTML('beforeend', '<div class="bubble user"></div>');
      chat.lastElementChild.textContent = v;
      input.value = '';
      const button = form.querySelector('button[type="submit"]');
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 20000);
      button.disabled = true;
      const loadingBubble = document.createElement('div');
      loadingBubble.className = 'bubble bot loading';
      loadingBubble.textContent = translate('Checking GI4C information…');
      chat.appendChild(loadingBubble);
      chat.scrollTop = chat.scrollHeight;

      try {
        const response = await fetch('/api/ai-assistant', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({ message: v, realtime: false })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok)         throw new Error(data.error || translate('The assistant could not answer right now. Please email info@gi4c.org for verified information.'));
        if (!data.answer) throw new Error(translate('The assistant returned no answer.'));
        chat.querySelector('.bubble.loading').remove();
        chat.insertAdjacentHTML('beforeend', '<div class="bubble bot"></div>');
        chat.lastElementChild.textContent = data.answer;
        if (Array.isArray(data.sources) && data.sources.length) {
          const source = document.createElement('div');
          source.className = 'bubble assistant-source';
          source.textContent = `${translate('Source:')} ${data.sources.map(item => item.title).join('; ')}`;
          chat.appendChild(source);
        }
      } catch (error) {
        const loadingBubble = chat.querySelector('.bubble.loading');
        if (loadingBubble) loadingBubble.remove();
        chat.insertAdjacentHTML('beforeend', '<div class="bubble bot assistant-error" role="alert"></div>');
        chat.lastElementChild.textContent = error.name === 'AbortError'
          ? translate('The assistant request timed out. Please contact info@gi4c.org for verified information.')
          : (error.name === 'TypeError' ? translate('The assistant could not be reached. Please contact info@gi4c.org for verified information.') : translate(error.message));
      } finally {
        clearTimeout(timeout);
        button.disabled = false;
        input.focus();
        chat.scrollTop = chat.scrollHeight;
      }
    });
  }

  // Load dashboard data from Python backend
  async function loadDashboardData() {
    try {
      const response = await fetch('/api/dashboard/kpi');
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      return null;
    }
  }

  // Load GIS data from Python backend
  async function loadGISData() {
    try {
      const response = await fetch('/api/gis/locations');
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to load GIS data:', error);
      return null;
    }
  }
})();
