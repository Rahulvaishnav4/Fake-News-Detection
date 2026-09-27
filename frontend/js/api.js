/**
 * Fake News Detection System - API Client
 * Centralized HTTP service for interacting with the backend API
 */

const API_BASE = (window.location.protocol === 'file:') 
  ? 'http://127.0.0.1:8000' 
  : window.location.origin;

class NewsAPI {
  /**
   * Universal fetch helper with timeout and error wrapping
   */
  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errorMsg = `Server error: ${response.status} ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData.detail) errorMsg = errData.detail;
          if (errData.error) errorMsg = errData.error;
        } catch (_) {}
        throw new Error(errorMsg);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err);
      throw err;
    }
  }

  // Get categories list
  static async getCategories() {
    return this.request('/api/categories');
  }

  // Fetch latest real-time news by category
  static async getLatestNews(category = 'all') {
    return this.request(`/api/news/latest?category=${encodeURIComponent(category)}`);
  }

  // Fetch trending breaking stories
  static async getTrendingNews() {
    return this.request('/api/news/trending');
  }

  // Search live news articles
  static async searchNews(query, category = 'all') {
    return this.request(`/api/news/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`);
  }

  // Deep multi-signal claim verification
  static async verifyNews(query) {
    return this.request('/api/verify', {
      method: 'POST',
      body: JSON.stringify({ query: query.trim() })
    });
  }

  // Retrieve verification history
  static async getHistory(limit = 15) {
    return this.request(`/api/verifications/history?limit=${limit}`);
  }

  // Retrieve full report by ID
  static async getVerificationById(id) {
    return this.request(`/api/verifications/${id}`);
  }

  // Get platform aggregate analytics
  static async getStats() {
    return this.request('/api/stats');
  }

  // Submit reader verification rating/feedback
  static async submitFeedback(verificationId, isHelpful, comment = '') {
    return this.request('/api/feedback', {
      method: 'POST',
      body: JSON.stringify({
        verification_id: verificationId,
        is_helpful: isHelpful,
        comment: comment
      })
    });
  }
}

window.NewsAPI = NewsAPI;
