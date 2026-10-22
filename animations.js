if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}

const translate = message => window.GI4CLanguage ? window.GI4CLanguage.translate(message) : message;

window.addEventListener('DOMContentLoaded', () => {
  window.scrollTo(0, 0);
});

window.addEventListener('load', () => {
  window.scrollTo(0, 0);
});

// Scroll-triggered animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      
      // Trigger counter animation if element has counters
      const counters = entry.target.querySelectorAll('.counter');
      counters.forEach(counter => animateCounter(counter));
    }
  });
}, observerOptions);

// Observe all animated elements
document.addEventListener('DOMContentLoaded', () => {
  const animatedElements = document.querySelectorAll('.fade-in, .slide-up, .slide-left, .slide-right, .scale-in');
  animatedElements.forEach(el => observer.observe(el));
});

// Animated counters
function animateCounter(element) {
  const target = parseInt(element.getAttribute('data-target'));
  if (!Number.isFinite(target) || element.dataset.animated === 'true') return;
  element.dataset.animated = 'true';
  const suffix = element.getAttribute('data-suffix') ?? '+';
  const duration = 2000;
  const step = target / (duration / 16);
  let current = 0;

  const updateCounter = () => {
    current += step;
    if (current < target) {
      element.textContent = Math.floor(current).toLocaleString() + suffix;
      requestAnimationFrame(updateCounter);
    } else {
      element.textContent = target.toLocaleString() + suffix;
    }
  };

  updateCounter();
}

// Sticky navigation with transparent-to-solid transition
const siteNav = document.getElementById('site-nav');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 100) {
    siteNav.classList.add('scrolled');
  } else {
    siteNav.classList.remove('scrolled');
  }

  lastScroll = currentScroll;
});

// Search functionality
const searchToggle = document.getElementById('search-toggle');
const searchModal = document.getElementById('search-modal');
const searchModalClose = document.getElementById('search-modal-close');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

if (searchToggle) {
  searchToggle.addEventListener('click', () => {
    searchModal.classList.add('active');
    searchInput.focus();
  });
}

if (searchModalClose) {
  searchModalClose.addEventListener('click', () => {
    searchModal.classList.remove('active');
  });
}

searchModal.addEventListener('click', (e) => {
  if (e.target === searchModal) {
    searchModal.classList.remove('active');
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && searchModal.classList.contains('active')) {
    searchModal.classList.remove('active');
  }
});

// Search content
const searchableContent = [
  { title: 'Home', titleFr: 'Accueil', url: 'index.html', description: 'GI4C homepage', descriptionFr: 'Page d’accueil de GI4C' },
  { title: 'About Us', titleFr: 'À propos de GI4C', url: 'mission.html', description: 'Learn about our mission and vision', descriptionFr: 'Découvrez notre mission et notre vision' },
  { title: 'Our Work', titleFr: 'Nos actions', url: 'programs.html', description: 'Explore our programs and initiatives', descriptionFr: 'Découvrez nos programmes et initiatives' },
  { title: 'Impact', titleFr: 'Impact', url: 'impact.html', description: 'See our impact and results', descriptionFr: 'Découvrez notre impact et nos résultats' },
  { title: 'Team', titleFr: 'Équipe', url: 'team.html', description: 'Meet our leadership team', descriptionFr: 'Découvrez notre équipe dirigeante' },
  { title: 'Project profiles', titleFr: 'Profils de projets', url: 'programs.html', description: 'Read detailed project profiles', descriptionFr: 'Consultez les profils détaillés des projets' },
  { title: 'Dashboard', titleFr: 'Tableau de bord', url: 'dashboard.html', description: 'View our data dashboard', descriptionFr: 'Consultez notre tableau de bord' },
  { title: 'AI Assistant', titleFr: 'Assistant IA', url: 'ai-assistant.html', description: 'Chat with our AI assistant', descriptionFr: 'Échangez avec notre assistant IA' },
  { title: 'Contact', titleFr: 'Contact', url: 'contact.html', description: 'Get in touch with us', descriptionFr: 'Contactez-nous' },
  { title: 'Donate', titleFr: 'Faire un don', url: 'donate.html', description: 'Support our work', descriptionFr: 'Soutenez nos actions' }
];

if (searchInput) {
  window.addEventListener('gi4c-language-change', () => {
    if (searchInput.value.trim().length >= 2) {
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    searchResults.innerHTML = '';

    if (query.length < 2) return;

    const french = window.GI4CLanguage && window.GI4CLanguage.get() === 'fr';
    const filtered = searchableContent.filter(item =>
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.titleFr.toLowerCase().includes(query) ||
      item.descriptionFr.toLowerCase().includes(query)
    );

    filtered.forEach(item => {
      const resultItem = document.createElement('div');
      resultItem.className = 'search-result-item';
      const title = document.createElement('h4');
      title.textContent = french ? item.titleFr : item.title;
      const description = document.createElement('p');
      description.textContent = french ? item.descriptionFr : item.description;
      resultItem.append(title, description);
      resultItem.addEventListener('click', () => {
        window.location.href = item.url;
      });
      searchResults.appendChild(resultItem);
    });

    if (filtered.length === 0) {
      const resultItem = document.createElement('div');
      resultItem.className = 'search-result-item';
      const message = document.createElement('p');
      message.textContent = french ? 'Aucun résultat trouvé' : 'No results found';
      resultItem.appendChild(message);
      searchResults.appendChild(resultItem);
    }
  });
}

const newsletterForm = document.getElementById('newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', async event => {
    event.preventDefault();
    const button = newsletterForm.querySelector('button[type="submit"]');
    const message = newsletterForm.querySelector('.newsletter-message');
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
          type: 'newsletter',
          email: newsletterForm.elements.email.value.trim()
        })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.success) {
        throw new Error(result.error || translate('Your request could not be sent. Please email info@gi4c.org directly.'));
      }
      message.textContent = translate('Thank you. Your request was accepted for delivery to GI4C. Our team must add your address to the mailing list.');
      newsletterForm.reset();
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

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Add stagger animation to cards
const cards = document.querySelectorAll('.card, .pillar, .data-card');
cards.forEach((card, index) => {
  card.style.animationDelay = `${index * 0.1}s`;
  card.classList.add('fade-in');
});

// Parallax effect for hero section (optional)
window.addEventListener('scroll', () => {
  const scrolled = window.pageYOffset;
  const hero = document.querySelector('.hero');
  if (hero && scrolled < window.innerHeight) {
    hero.style.transform = `translateY(${scrolled * 0.3}px)`;
  }
});

// Lazy loading for images
if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        observer.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
}

// Performance: Debounce resize events
let resizeTimeout;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    // Handle resize
  }, 250);
});
