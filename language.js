(function () {
  const navScript = document.querySelector('script[src$="nav.js"]');
  if (!navScript) return;

  const baseUrl = new URL('.', navScript.src);
  const bundleFiles = [
    'translations-core.js',
    'translations-programs.js',
    'translations-services.js'
  ];

  function loadBundle(file) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = new URL(file, baseUrl).href;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Could not load ${file}`));
      document.head.appendChild(script);
    });
  }

  Promise.all(bundleFiles.map(loadBundle))
    .then(initializeLanguage)
    .catch(error => console.error('Language resources could not be loaded:', error));

  function initializeLanguage() {
    const translations = window.GI4C_TRANSLATIONS || {};
    const pageName = decodeURIComponent(window.location.pathname.split('/').pop() || 'index.html');
    const pageTranslations = translations.pages && translations.pages[pageName] || {};
    const reversePageTranslations = translations.reversePages && translations.reversePages[pageName] || {};
    const dictionary = Object.assign({}, translations.common || {}, pageTranslations);
    const originalText = new WeakMap();
    const originalAttributes = new WeakMap();
    let currentLanguage = 'en';
    const dynamicTranslations = Object.assign({
      'Sending...': 'Envoi en cours…',
      'Your message could not be sent. Please email info@gi4c.org directly.': 'Votre message n’a pas pu être envoyé. Veuillez écrire directement à info@gi4c.org.',
      'Thank you. Your message was accepted for delivery to GI4C.': 'Merci. Votre message a été transmis à GI4C pour traitement.',
      'Sending timed out. Please try again or email info@gi4c.org.': 'Le délai d’envoi a expiré. Veuillez réessayer ou écrire à info@gi4c.org.',
      'We could not reach GI4C’s email service. Please email info@gi4c.org.': 'Le service de messagerie de GI4C est inaccessible. Veuillez écrire à info@gi4c.org.',
      'Your request could not be sent. Please email info@gi4c.org directly.': 'Votre demande n’a pas pu être envoyée. Veuillez écrire directement à info@gi4c.org.',
      'Thank you. Your request was accepted for delivery to GI4C. Our team must add your address to the mailing list.': 'Merci. Votre demande a été transmise à GI4C. Notre équipe doit ajouter votre adresse à la liste de diffusion.',
      'Checking GI4C information…': 'Vérification des informations de GI4C…',
      'The assistant could not answer right now. Please email info@gi4c.org for verified information.': 'L’assistant ne peut pas répondre pour le moment. Pour obtenir des informations vérifiées, écrivez à info@gi4c.org.',
      'The assistant returned no answer.': 'L’assistant n’a fourni aucune réponse.',
      'Source:': 'Source :',
      'The assistant request timed out. Please contact info@gi4c.org for verified information.': 'Le délai de réponse de l’assistant a expiré. Pour obtenir des informations vérifiées, contactez info@gi4c.org.',
      'The assistant could not be reached. Please contact info@gi4c.org for verified information.': 'L’assistant est inaccessible. Pour obtenir des informations vérifiées, contactez info@gi4c.org.',
      'The GI4C assistant is not configured yet. Please contact info@gi4c.org for verified information.': 'L’assistant de GI4C n’est pas encore configuré. Pour obtenir des informations vérifiées, contactez info@gi4c.org.',
      'The assistant is temporarily unavailable. Please try again or contact info@gi4c.org.': 'L’assistant est temporairement indisponible. Veuillez réessayer ou contacter info@gi4c.org.',
      'AI provider error': 'Erreur du fournisseur d’IA',
      'Email delivery is not configured yet. Please email info@gi4c.org directly.': 'Le service d’envoi des courriels n’est pas encore configuré. Veuillez écrire directement à info@gi4c.org.',
      'Request could not be accepted.': 'La demande n’a pas pu être acceptée.',
      'Enter a valid email address of no more than 254 characters.': 'Saisissez une adresse e-mail valide de 254 caractères maximum.',
      'Complete all required contact fields.': 'Veuillez remplir tous les champs obligatoires du formulaire de contact.',
      'One or more fields exceed their permitted length.': 'Un ou plusieurs champs dépassent la longueur autorisée.',
      'Unsupported email request.': 'Ce type de demande par e-mail n’est pas pris en charge.',
      'GI4C could not accept the message for delivery. Please try again or email info@gi4c.org directly.': 'GI4C n’a pas pu accepter le message pour envoi. Veuillez réessayer ou écrire directement à info@gi4c.org.',
      'GI4C could not send the message. Please try again or email info@gi4c.org directly.': 'GI4C n’a pas pu envoyer le message. Veuillez réessayer ou écrire directement à info@gi4c.org.'
    }, translations.dynamic || {});
    Object.assign(dictionary, dynamicTranslations);
    const reverseDynamicTranslations = Object.fromEntries(
      Object.entries(dynamicTranslations).map(([english, french]) => [french, english])
    );
    const englishDictionary = Object.assign({}, reversePageTranslations, reverseDynamicTranslations);

    try {
      currentLanguage = localStorage.getItem('gi4c-language') === 'fr' ? 'fr' : 'en';
    } catch (error) {
      console.warn('The saved language preference could not be read:', error);
    }
    const initialLanguage = currentLanguage;

    function readLanguage() {
      return currentLanguage;
    }

    function saveLanguage(language) {
      currentLanguage = language;
      try {
        localStorage.setItem('gi4c-language', language);
      } catch (error) {
        console.warn('Language preference could not be saved:', error);
      }
    }

    function translateText(text, language) {
      const activeDictionary = language === 'fr' ? dictionary : englishDictionary;
      if (activeDictionary[text]) return activeDictionary[text];
      const prefix = Object.keys(activeDictionary).find(key => key.endsWith(':') && text.startsWith(key) && text.length > key.length);
      return prefix ? `${activeDictionary[prefix]}${text.slice(prefix.length)}` : null;
    }

    function addLanguageButton(parent, mobile) {
      if (!parent || parent.querySelector(mobile ? '.language-toggle-mobile' : '.language-toggle')) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = mobile ? 'language-toggle language-toggle-mobile' : 'language-toggle';
      button.addEventListener('click', () => setLanguage(readLanguage() === 'fr' ? 'en' : 'fr'));
      parent.appendChild(button);
    }

    const navActions = document.querySelector('.nav-actions');
    const mobileMenu = document.querySelector('.mobile-menu');
    addLanguageButton(navActions, false);
    addLanguageButton(mobileMenu, true);
    if (!navActions && !mobileMenu) {
      const standaloneButton = document.createElement('button');
      standaloneButton.type = 'button';
      standaloneButton.className = 'language-toggle language-toggle-standalone';
      standaloneButton.addEventListener('click', () => setLanguage(readLanguage() === 'fr' ? 'en' : 'fr'));
      document.body.appendChild(standaloneButton);
    }

    function translateAttributes(language) {
      const providedAttributes = translations.attributes || {};
      const globalAttributes = Object.fromEntries(
        Object.entries(providedAttributes).filter(([, value]) => typeof value === 'string')
      );
      const attributeTranslations = Object.assign({
        'Search': 'Rechercher',
        'Open menu': 'Ouvrir le menu',
        'Search our site...': 'Rechercher sur le site…',
        'Your name': 'Votre nom',
        'you@example.com': 'vous@exemple.com',
        'How can we help?': 'Comment pouvons-nous vous aider ?',
        'Write your message...': 'Écrivez votre message…',
        'Leave this field blank': 'Laissez ce champ vide',
        'Your email address': 'Votre adresse e-mail'
      }, globalAttributes, providedAttributes.common || {});
      document.querySelectorAll('[placeholder], [title], [aria-label], [alt], [value], meta[name="description"]').forEach(element => {
        if (!originalAttributes.has(element)) {
          originalAttributes.set(element, {});
          for (const attribute of ['placeholder', 'title', 'aria-label', 'alt', 'value', 'content']) {
            originalAttributes.get(element)[attribute] = element.getAttribute(attribute);
          }
        }
        const originals = originalAttributes.get(element);
        for (const attribute of Object.keys(originals)) {
          const original = originals[attribute];
          if (original === null) continue;
          const translated = attributeTranslations[original] || providedAttributes[pageName] &&
            providedAttributes[pageName][getSelector(element)] &&
            providedAttributes[pageName][getSelector(element)][attribute];
          element.setAttribute(attribute, language === 'fr' && translated ? translated : original);
        }
      });

      const pageAttributes = providedAttributes[pageName] || {};
      Object.keys(pageAttributes).forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
          const attributes = pageAttributes[selector];
          if (!originalAttributes.has(element)) originalAttributes.set(element, {});
          const originals = originalAttributes.get(element);
          Object.keys(attributes).forEach(attribute => {
            if (!(attribute in originals)) originals[attribute] = element.getAttribute(attribute);
            const original = originals[attribute];
            if (original !== null) element.setAttribute(attribute, language === 'fr' ? attributes[attribute] : original);
          });
        });
      });
    }

    function getSelector(element) {
      if (element.id) return `#${element.id}`;
      return element.tagName.toLowerCase();
    }

    function applyLanguage(language) {
      document.documentElement.lang = language;
      const walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (!originalText.has(node)) originalText.set(node, node.nodeValue);
        const original = originalText.get(node);
        const trimmed = original.trim();
        if (!trimmed) continue;
        const translated = translateText(trimmed, language);
        if (translated) {
          const leading = original.match(/^\s*/)[0];
          const trailing = original.match(/\s*$/)[0];
          node.nodeValue = `${leading}${translated}${trailing}`;
        } else {
          node.nodeValue = original;
        }
      }

      translateAttributes(language);
      document.querySelectorAll('.language-toggle').forEach(button => {
        const label = language === 'fr' ? 'English' : 'Français';
        if (button.textContent !== label) button.textContent = label;
        button.setAttribute('aria-label', language === 'fr' ? 'Passer en anglais' : 'Switch to French');
        button.setAttribute('aria-pressed', language === 'fr' ? 'true' : 'false');
      });
      const menuButton = document.querySelector('.menu-btn');
      if (menuButton) menuButton.setAttribute('aria-label', language === 'fr' ? 'Ouvrir le menu' : 'Open menu');
    }

    function setLanguage(language) {
      saveLanguage(language);
      applyLanguage(language);
      window.dispatchEvent(new CustomEvent('gi4c-language-change', { detail: { language } }));
    }

    window.GI4CLanguage = {
      get: readLanguage,
      set: setLanguage,
      translate: message => readLanguage() === 'fr' && dynamicTranslations[message]
        ? dynamicTranslations[message]
        : message
    };

    applyLanguage(initialLanguage);
    const mutationObserver = new MutationObserver(records => {
      if (records.some(record => record.type === 'childList' && record.addedNodes.length)) {
        applyLanguage(readLanguage());
      }
    });
    mutationObserver.observe(document.body, { childList: true, subtree: true });
  }
})();
