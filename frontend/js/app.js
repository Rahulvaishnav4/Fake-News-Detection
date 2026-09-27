/**
 * Fake News Detection System - Main Application Controller
 */

class AppController {
  constructor() {
    this.currentView = 'home';
    this.currentCategory = 'all';
    this.currentSearchQuery = '';
    this.cachedNews = [];
    this.cachedTrending = [];
    this.isVerifying = false;
    this.theme = localStorage.getItem('fnd_theme') || 'light';

    this.init();
  }

  init() {
    this.applyTheme(this.theme);
    this.bindEvents();
    this.loadInitialData();
  }

  /**
   * Theme Management (Dark/Light mode)
   */
  applyTheme(theme) {
    this.theme = theme;
    localStorage.setItem('fnd_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      const icon = document.getElementById('theme-icon');
      if (icon) icon.setAttribute('data-lucide', 'sun');
    } else {
      document.documentElement.classList.remove('dark');
      const icon = document.getElementById('theme-icon');
      if (icon) icon.setAttribute('data-lucide', 'moon');
    }
    if (window.lucide) lucide.createIcons();
  }

  toggleTheme() {
    const nextTheme = this.theme === 'dark' ? 'light' : 'dark';
    this.applyTheme(nextTheme);
  }

  /**
   * Bind DOM Events
   */
  bindEvents() {
    // Theme toggle button
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => this.toggleTheme());
    }

    // Main Search input and form
    const searchForm = document.getElementById('main-search-form');
    if (searchForm) {
      searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = document.getElementById('main-search-input');
        if (input && input.value.trim()) {
          this.handleSearch(input.value.trim());
        }
      });
    }

    // Direct Verify input form in Verify Tab
    const verifyForm = document.getElementById('verify-form');
    if (verifyForm) {
      verifyForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = document.getElementById('verify-input');
        if (input && input.value.trim()) {
          this.runVerification(input.value.trim());
        }
      });
    }
  }

  /**
   * Switch between SPA views: home, verify, search-results, how-it-works, history, about, contact
   */
  switchView(viewName) {
    this.currentView = viewName;
    const views = ['home', 'verify', 'search-results', 'how-it-works', 'history', 'about', 'contact'];
    
    views.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      if (el) {
        if (v === viewName) {
          el.classList.remove('hidden');
        } else {
          el.classList.add('hidden');
        }
      }
    });

    // Update active state in nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.getAttribute('data-view') === viewName) {
        link.classList.add('text-blue-600', 'dark:text-blue-400', 'font-bold');
        link.classList.remove('text-slate-600', 'dark:text-slate-300');
      } else {
        link.classList.remove('text-blue-600', 'dark:text-blue-400', 'font-bold');
        link.classList.add('text-slate-600', 'dark:text-slate-300');
      }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Refresh icons
    if (window.lucide) lucide.createIcons();

    // Contextual view initializers
    if (viewName === 'history') {
      this.loadHistory();
      this.loadStats();
    }
  }

  /**
   * Initial data loader: categories, latest news, trending news
   */
  async loadInitialData() {
    this.loadCategories();
    this.loadTrendingNews();
    this.loadLatestNews('all');
  }

  /**
   * Load Categories into horizontal tabs
   */
  async loadCategories() {
    try {
      const data = await NewsAPI.getCategories();
      const container = document.getElementById('categories-container');
      if (!container || !data.categories) return;

      container.innerHTML = data.categories.map(cat => `
        <button 
          onclick="window.App.switchCategory('${cat.id}')"
          class="category-tab px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
            this.currentCategory === cat.id 
              ? 'bg-blue-600 text-white shadow-sm' 
              : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-blue-400'
          }"
          data-category="${cat.id}"
        >
          <i data-lucide="${cat.icon || 'tag'}" class="w-3.5 h-3.5"></i>
          <span>${cat.label}</span>
        </button>
      `).join('');

      if (window.lucide) lucide.createIcons();
    } catch (err) {
      console.warn('Categories load error:', err);
    }
  }

  /**
   * Switch Active News Category
   */
  switchCategory(category) {
    this.currentCategory = category;
    
    // Update tab styling
    document.querySelectorAll('.category-tab').forEach(tab => {
      const catId = tab.getAttribute('data-category');
      if (catId === category) {
        tab.className = 'category-tab px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 bg-blue-600 text-white shadow-sm';
      } else {
        tab.className = 'category-tab px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-blue-400';
      }
    });

    if (this.currentView !== 'home') {
      this.switchView('home');
    }

    this.loadLatestNews(category);
  }

  /**
   * Load Latest News
   */
  async loadLatestNews(category = 'all') {
    const grid = document.getElementById('latest-news-grid');
    if (!grid) return;

    grid.innerHTML = UIComponents.renderSkeletons(6);
    if (window.lucide) lucide.createIcons();

    try {
      const data = await NewsAPI.getLatestNews(category);
      if (data.articles && data.articles.length > 0) {
        this.cachedNews = data.articles;
        grid.innerHTML = data.articles.map((art, idx) => UIComponents.renderNewsCard(art, idx)).join('');
      } else {
        grid.innerHTML = UIComponents.renderEmptyState('No articles found', `No live news currently available in category "${category}".`);
      }
      if (window.lucide) lucide.createIcons();
    } catch (err) {
      grid.innerHTML = `
        <div class="col-span-full bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 p-6 rounded-xl text-center">
          <p class="font-bold mb-2">Unable to load live news</p>
          <p class="text-xs mb-4">${err.message}</p>
          <button onclick="window.App.loadLatestNews('${category}')" class="px-4 py-1.5 bg-rose-600 text-white text-xs font-semibold rounded-lg hover:bg-rose-700 transition">
            Try Again
          </button>
        </div>
      `;
    }
  }

  /**
   * Load Trending Headlines for Ticker / Sidebar
   */
  async loadTrendingNews() {
    const container = document.getElementById('trending-news-list');
    if (!container) return;

    try {
      const data = await NewsAPI.getTrendingNews();
      if (data.trending && data.trending.length > 0) {
        this.cachedTrending = data.trending;
        container.innerHTML = data.trending.slice(0, 5).map((item, idx) => `
          <div class="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/40 transition border border-transparent hover:border-slate-100 dark:hover:border-slate-700">
            <span class="font-black text-blue-600 dark:text-blue-400 text-base leading-none">#${idx + 1}</span>
            <div class="space-y-1">
              <h4 class="text-xs font-bold text-slate-900 dark:text-white line-clamp-2 hover:text-blue-600 transition">
                <a href="${item.link}" target="_blank" rel="noopener noreferrer">${UIComponents.escapeHtml(item.title)}</a>
              </h4>
              <div class="flex items-center gap-2 text-[10px] text-slate-400">
                <span>${UIComponents.escapeHtml(item.source)}</span>
                <span>•</span>
                <span>${UIComponents.formatTimeAgo(item.published_at)}</span>
              </div>
            </div>
          </div>
        `).join('');

        if (window.lucide) lucide.createIcons();
      }
    } catch (err) {
      console.warn('Trending news error:', err);
    }
  }

  /**
   * Search Handler
   */
  async handleSearch(query) {
    if (!query) return;
    this.currentSearchQuery = query;

    // If query looks like a specific claim to verify or starts with http, prompt verification
    this.switchView('search-results');

    const heading = document.getElementById('search-results-heading');
    const container = document.getElementById('search-results-grid');
    if (heading) heading.textContent = `Search results for: "${query}"`;
    if (container) container.innerHTML = UIComponents.renderSkeletons(6);

    try {
      const data = await NewsAPI.searchNews(query);
      if (data.results && data.results.length > 0) {
        container.innerHTML = data.results.map((art, idx) => UIComponents.renderNewsCard(art, idx)).join('');
      } else {
        container.innerHTML = UIComponents.renderEmptyState('No news articles matched', `No live news stories found for "${query}". You can also test verifying this claim directly.`);
      }
      if (window.lucide) lucide.createIcons();
    } catch (err) {
      if (container) {
        container.innerHTML = `
          <div class="col-span-full bg-rose-50 dark:bg-rose-950/30 p-6 rounded-xl text-center text-rose-700">
            <p class="font-bold">Search request failed</p>
            <p class="text-xs mt-1">${err.message}</p>
          </div>
        `;
      }
    }
  }

  /**
   * Filter Search Results (Latest vs Most Relevant)
   */
  sortSearchResults(filter) {
    const container = document.getElementById('search-results-grid');
    if (!container) return;
    
    // Sort cached or existing articles
    const cards = Array.from(container.children);
    if (filter === 'latest') {
      cards.reverse();
    }
    cards.forEach(card => container.appendChild(card));
  }

  /**
   * One-click trigger verification from any News Card
   */
  triggerVerification(claimText) {
    this.switchView('verify');
    const input = document.getElementById('verify-input');
    if (input) {
      input.value = claimText;
    }
    this.runVerification(claimText);
  }

  /**
   * Deep Verification Pipeline Execution
   */
  async runVerification(query) {
    if (!query || this.isVerifying) return;
    this.isVerifying = true;

    // Show Progress State
    const progressContainer = document.getElementById('verification-progress');
    const resultContainer = document.getElementById('verification-result-container');
    const verifyBtn = document.getElementById('verify-submit-btn');

    if (verifyBtn) {
      verifyBtn.disabled = true;
      verifyBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Analyzing...`;
    }

    if (progressContainer) progressContainer.classList.remove('hidden');
    if (resultContainer) resultContainer.classList.add('hidden');
    if (window.lucide) lucide.createIcons();

    // Step-by-step progress simulation
    const steps = [
      "Extracting core claim propositions & linguistic patterns...",
      "Searching live Google News & online publication index...",
      "Cross-referencing 1000+ domain credibility registries...",
      "Evaluating independent multi-source corroborations...",
      "Checking international fact-checking databases for debunkings...",
      "Synthesizing multi-signal assessment & confidence score..."
    ];
    let stepIndex = 0;
    const stepLabel = document.getElementById('verification-step-label');

    const progressTimer = setInterval(() => {
      stepIndex = (stepIndex + 1) % steps.length;
      if (stepLabel) stepLabel.textContent = steps[stepIndex];
    }, 450);

    try {
      const result = await NewsAPI.verifyNews(query);
      clearInterval(progressTimer);

      if (progressContainer) progressContainer.classList.add('hidden');
      if (resultContainer) {
        resultContainer.classList.remove('hidden');
        resultContainer.innerHTML = UIComponents.renderVerificationDashboard(result);
      }
      if (window.lucide) lucide.createIcons();

      // Scroll smoothly to results
      resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      clearInterval(progressTimer);
      if (progressContainer) progressContainer.classList.add('hidden');
      if (resultContainer) {
        resultContainer.classList.remove('hidden');
        resultContainer.innerHTML = `
          <div class="rounded-xl border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/30 p-6 text-center text-rose-800 dark:text-rose-300">
            <h4 class="font-bold text-base mb-1">Verification Processing Failed</h4>
            <p class="text-xs mb-4">${err.message}</p>
            <button onclick="window.App.runVerification('${query}')" class="px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 transition">
              Retry Verification
            </button>
          </div>
        `;
      }
    } finally {
      this.isVerifying = false;
      if (verifyBtn) {
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = `<i data-lucide="shield-check" class="w-4 h-4"></i> Run Deep Verification`;
      }
      if (window.lucide) lucide.createIcons();
    }
  }

  /**
   * Handle user feedback (Was this helpful: Yes/No)
   */
  async handleFeedback(verificationId, isHelpful) {
    try {
      await NewsAPI.submitFeedback(verificationId, isHelpful);
      const section = document.getElementById(`feedback-section-${verificationId || 'current'}`);
      if (section) {
        section.innerHTML = `
          <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
            <i data-lucide="check" class="w-4 h-4"></i> Thank you for your feedback!
          </span>
        `;
        if (window.lucide) lucide.createIcons();
      }
    } catch (err) {
      console.error('Feedback submission error:', err);
    }
  }

  /**
   * Load Verification History
   */
  async loadHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;

    list.innerHTML = '<div class="text-center py-8 text-slate-400">Loading verification records...</div>';

    try {
      const data = await NewsAPI.getHistory(20);
      if (data.history && data.history.length > 0) {
        list.innerHTML = data.history.map(item => {
          const isReal = item.status.includes('REAL');
          const isFake = item.status.includes('FAKE');
          const badgeClass = isReal 
            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300' 
            : (isFake ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-300');

          return `
            <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="border px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">
                    ${item.status}
                  </span>
                  <span class="text-xs text-slate-400 font-semibold">${item.confidence}% Confidence</span>
                  <span class="text-xs text-slate-400">• ${UIComponents.formatTimeAgo(item.created_at)}</span>
                </div>
                <h4 class="text-sm font-semibold text-slate-900 dark:text-white line-clamp-1">
                  "${UIComponents.escapeHtml(item.claim)}"
                </h4>
              </div>

              <button 
                onclick="window.App.loadHistoryDetail(${item.id})"
                class="shrink-0 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
              >
                View Full Report <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          `;
        }).join('');
        if (window.lucide) lucide.createIcons();
      } else {
        list.innerHTML = '<div class="text-center py-8 text-slate-400 italic">No verifications recorded yet. Run your first check in the Verify tab!</div>';
      }
    } catch (err) {
      list.innerHTML = `<div class="text-center py-4 text-rose-500">Failed to load history: ${err.message}</div>`;
    }
  }

  /**
   * Load System Statistics
   */
  async loadStats() {
    try {
      const stats = await NewsAPI.getStats();
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setVal('stat-total-verifications', stats.total_verifications || 0);
      setVal('stat-real-pct', `${stats.real_percentage || 0}%`);
      setVal('stat-fake-pct', `${stats.fake_percentage || 0}%`);
      setVal('stat-uncertain-pct', `${stats.uncertain_percentage || 0}%`);
    } catch (err) {
      console.warn('Stats load error:', err);
    }
  }

  /**
   * Load and render specific verification report by ID
   */
  async loadHistoryDetail(id) {
    this.switchView('verify');
    const resultContainer = document.getElementById('verification-result-container');
    if (!resultContainer) return;

    resultContainer.innerHTML = '<div class="text-center py-12 text-slate-400">Loading stored verification report...</div>';
    resultContainer.classList.remove('hidden');

    try {
      const report = await NewsAPI.getVerificationById(id);
      resultContainer.innerHTML = UIComponents.renderVerificationDashboard(report);
      if (window.lucide) lucide.createIcons();
      resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      resultContainer.innerHTML = `<div class="text-center py-6 text-rose-500">Error loading report: ${err.message}</div>`;
    }
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.App = new AppController();
});
