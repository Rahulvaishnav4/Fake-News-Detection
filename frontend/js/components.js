/**
 * Fake News Detection System - UI Components
 * Renderers for cards, badges, gauges, and evidence dashboards
 */

const UIComponents = {
  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  /**
   * Humanize publication timestamps (e.g., "2 hours ago")
   */
  formatTimeAgo(dateStr) {
    if (!dateStr) return 'Recently';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr.split('GMT')[0].trim();
      const seconds = Math.floor((new Date() - date) / 1000);
      if (seconds < 60) return 'Just now';
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      if (days < 30) return `${days}d ago`;
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (_) {
      return dateStr;
    }
  },

  /**
   * Returns Tailwind badge style classes according to source credibility tier
   */
  getCpuBadge(tier, score) {
    if (tier === 'tier_1') {
      return {
        bg: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
        label: 'Tier-1 Authoritative'
      };
    } else if (tier === 'fact_checker') {
      return {
        bg: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-300 dark:border-blue-800',
        label: 'Certified Fact-Checker'
      };
    } else if (tier === 'tier_2') {
      return {
        bg: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800',
        label: 'Mainstream News'
      };
    } else if (tier === 'satire') {
      return {
        bg: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-300 dark:border-purple-800',
        label: 'Satire / Parody'
      };
    } else if (tier === 'unreliable') {
      return {
        bg: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300 border-red-300 dark:border-red-800',
        label: 'Low Credibility'
      };
    }
    return {
      bg: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300 dark:border-slate-700',
      label: 'Independent Web'
    };
  },

  /**
   * Render individual News Card
   */
  renderNewsCard(article, index = 0) {
    const title = this.escapeHtml(article.title || 'Untitled News');
    const source = this.escapeHtml(article.source || 'Online Source');
    const snippet = this.escapeHtml(article.snippet || '');
    const link = article.link || '#';
    const category = this.escapeHtml(article.category || 'News');
    const timeAgo = this.formatTimeAgo(article.published_at);
    const imageUrl = article.image_url || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&auto=format&fit=crop&q=80';
    const cred = article.credibility || { tier: 'unverified', score: 50 };
    const badge = this.getCpuBadge(cred.tier, cred.score);

    // Escape for inline onclick
    const cleanTitleForAttr = title.replace(/'/g, "\\'").replace(/"/g, '&quot;');

    return `
      <div class="news-card bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col justify-between shadow-sm hover:shadow-md transition">
        <div>
          <!-- Thumbnail Image -->
          <div class="relative w-full h-48 overflow-hidden bg-slate-100 dark:bg-slate-900">
            <img 
              src="${imageUrl}" 
              alt="${title}"
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              onerror="this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&auto=format&fit=crop&q=80'"
            />
            <span class="absolute top-3 left-3 bg-blue-600/90 text-white text-xs font-semibold px-2.5 py-1 rounded-full backdrop-blur-sm shadow-sm">
              ${category}
            </span>
          </div>

          <!-- Body Content -->
          <div class="p-5">
            <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
              <span class="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1.5 truncate max-w-[60%]">
                <i data-lucide="newspaper" class="w-3.5 h-3.5 text-blue-500 shrink-0"></i>
                <span class="truncate">${source}</span>
              </span>
              <span class="shrink-0 flex items-center gap-1">
                <i data-lucide="clock" class="w-3 h-3"></i>
                ${timeAgo}
              </span>
            </div>

            <h3 class="text-base font-bold text-slate-900 dark:text-white line-clamp-2 leading-snug mb-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              <a href="${link}" target="_blank" rel="noopener noreferrer">${title}</a>
            </h3>

            <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 leading-relaxed mb-4">
              ${snippet}
            </p>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="p-5 pt-0 border-t border-slate-100 dark:border-slate-700/60 mt-auto">
          <div class="flex items-center justify-between pt-3">
            <span class="text-[11px] font-medium border px-2 py-0.5 rounded-md ${badge.bg}">
              ${badge.label}
            </span>

            <div class="flex items-center gap-2">
              <button 
                onclick="window.App.triggerVerification('${cleanTitleForAttr}')"
                class="inline-flex items-center gap-1.5 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition"
                title="Run full fake news analysis on this claim"
              >
                <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
                Verify Claim
              </button>

              <a 
                href="${link}" 
                target="_blank" 
                rel="noopener noreferrer" 
                class="inline-flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                title="Open original article"
              >
                <i data-lucide="external-link" class="w-4 h-4"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Render Full Detailed Verification Dashboard
   */
  renderVerificationDashboard(v) {
    const claim = this.escapeHtml(v.claim);
    const originalQuery = this.escapeHtml(v.original_query);
    const status = v.status || 'UNCERTAIN / NEEDS VERIFICATION';
    const statusCode = v.status_code || 'uncertain';
    const confidence = v.confidence || 50;
    const recommendation = this.escapeHtml(v.recommendation || '');
    const linguistic = v.linguistic_analysis || {};
    const sources = v.sources || [];
    const evidence = v.evidence || { supporting: [], warnings: [], contradicting: [] };

    // Status-specific theme values
    let statusClass = 'border-amber-500 bg-amber-50 dark:bg-amber-950/20 text-amber-900 dark:text-amber-200';
    let statusBadge = 'bg-amber-500 text-white';
    let statusIcon = 'alert-triangle';
    let gaugeColor = '#f59e0b';
    let glowClass = 'status-uncertain-glow';

    if (statusCode === 'real') {
      statusClass = 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-900 dark:text-emerald-200';
      statusBadge = 'bg-emerald-600 text-white';
      statusIcon = 'check-circle-2';
      gaugeColor = '#10b981';
      glowClass = 'status-real-glow';
    } else if (statusCode === 'fake') {
      statusClass = 'border-rose-500 bg-rose-50 dark:bg-rose-950/20 text-rose-900 dark:text-rose-200';
      statusBadge = 'bg-rose-600 text-white';
      statusIcon = 'x-circle';
      gaugeColor = '#ef4444';
      glowClass = 'status-fake-glow';
    }

    // Gauge circumference math (r=45, circum=282.7)
    const strokeDashoffset = 282.7 - (282.7 * (confidence / 100));

    return `
      <div class="space-y-6">
        <!-- Top Status Banner -->
        <div class="rounded-2xl border-2 p-6 md:p-8 ${statusClass} ${glowClass} transition-all">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div class="space-y-2 max-w-2xl">
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${statusBadge}">
                <i data-lucide="${statusIcon}" class="w-4 h-4"></i>
                <span>Automated Verification Assessment</span>
              </div>
              <h2 class="text-2xl md:text-3xl font-extrabold tracking-tight">
                ${status}
              </h2>
              <p class="text-sm font-medium opacity-90 leading-relaxed">
                ${recommendation}
              </p>
            </div>

            <!-- Circular Confidence Gauge -->
            <div class="flex items-center gap-4 bg-white/70 dark:bg-slate-900/60 backdrop-blur-md px-5 py-4 rounded-2xl border border-black/5 dark:border-white/10 shrink-0">
              <div class="relative w-24 h-24 flex items-center justify-center">
                <svg class="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="8" class="text-slate-200 dark:text-slate-700" fill="transparent" />
                  <circle cx="50" cy="50" r="45" stroke="${gaugeColor}" stroke-width="8" stroke-dasharray="282.7" stroke-dashoffset="${strokeDashoffset}" stroke-linecap="round" fill="transparent" class="gauge-circle" />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span class="text-xl font-black text-slate-900 dark:text-white leading-none">${confidence}%</span>
                  <span class="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 mt-0.5">Confidence</span>
                </div>
              </div>
              <div class="text-xs space-y-1">
                <div class="font-semibold text-slate-800 dark:text-slate-200">Signals Evaluated:</div>
                <div class="text-slate-600 dark:text-slate-400">Sources checked: <strong>${v.total_sources_found}</strong></div>
                <div class="text-slate-600 dark:text-slate-400">Authoritative tier: <strong>${v.matching_reliable_sources}</strong></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Verified Claim Quote -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
          <div class="text-xs font-semibold uppercase text-slate-400 dark:text-slate-500 mb-1 flex items-center gap-1.5">
            <i data-lucide="quote" class="w-3.5 h-3.5"></i>
            Analyzed Claim / Headline
          </div>
          <blockquote class="text-lg font-semibold text-slate-900 dark:text-white italic pl-3 border-l-4 border-blue-500">
            "${claim}"
          </blockquote>
          ${v.query_type === 'url' ? `<div class="mt-2 text-xs text-blue-500 truncate flex items-center gap-1"><i data-lucide="link" class="w-3 h-3"></i> ${originalQuery}</div>` : ''}
        </div>

        <!-- 3-Column Evidence & Signal Breakdown -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <!-- Column 1: Supporting Evidence -->
          <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 flex flex-col">
            <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm mb-3">
              <i data-lucide="check-circle" class="w-4 h-4"></i>
              Supporting Corroboration (${evidence.supporting ? evidence.supporting.length : 0})
            </div>
            <ul class="space-y-2 text-xs text-slate-700 dark:text-slate-300 flex-1">
              ${evidence.supporting && evidence.supporting.length > 0
                ? evidence.supporting.map(item => `
                    <li class="flex items-start gap-2 bg-emerald-50/50 dark:bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-100 dark:border-emerald-900/30">
                      <span class="text-emerald-500 font-bold mt-0.5">✓</span>
                      <span>${this.escapeHtml(item)}</span>
                    </li>
                  `).join('')
                : '<li class="text-slate-400 italic p-2">No definitive corroborating tier-1 evidence found.</li>'
              }
            </ul>
          </div>

          <!-- Column 2: Warnings & Information Gaps -->
          <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 flex flex-col">
            <div class="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm mb-3">
              <i data-lucide="alert-circle" class="w-4 h-4"></i>
              Signal Warnings & Gaps (${evidence.warnings ? evidence.warnings.length : 0})
            </div>
            <ul class="space-y-2 text-xs text-slate-700 dark:text-slate-300 flex-1">
              ${evidence.warnings && evidence.warnings.length > 0
                ? evidence.warnings.map(item => `
                    <li class="flex items-start gap-2 bg-amber-50/50 dark:bg-amber-950/20 p-2.5 rounded-lg border border-amber-100 dark:border-amber-900/30">
                      <span class="text-amber-500 font-bold mt-0.5">⚠</span>
                      <span>${this.escapeHtml(item)}</span>
                    </li>
                  `).join('')
                : '<li class="text-slate-400 italic p-2">No red flags or missing attribution detected.</li>'
              }
            </ul>
          </div>

          <!-- Column 3: Contradictions & Debunkings -->
          <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 flex flex-col">
            <div class="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm mb-3">
              <i data-lucide="x-octagon" class="w-4 h-4"></i>
              Contradictions & Fact-Checks (${evidence.contradicting ? evidence.contradicting.length : 0})
            </div>
            <ul class="space-y-2 text-xs text-slate-700 dark:text-slate-300 flex-1">
              ${evidence.contradicting && evidence.contradicting.length > 0
                ? evidence.contradicting.map(item => `
                    <li class="flex items-start gap-2 bg-rose-50/50 dark:bg-rose-950/20 p-2.5 rounded-lg border border-rose-100 dark:border-rose-900/30">
                      <span class="text-rose-500 font-bold mt-0.5">✗</span>
                      <span>${this.escapeHtml(item)}</span>
                    </li>
                  `).join('')
                : '<li class="text-slate-400 italic p-2">No debunking records or direct contradictory reports discovered.</li>'
              }
            </ul>
          </div>
        </div>

        <!-- Linguistic & Stylistic Analysis Card -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="file-text" class="w-4 h-4 text-blue-500"></i>
              Linguistic & Tone Analysis
            </h3>
            <span class="text-xs px-2.5 py-1 rounded-full font-semibold ${
              linguistic.overall_linguistic_risk === 'High' 
                ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300' 
                : linguistic.overall_linguistic_risk === 'Moderate'
                  ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                  : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
            }">
              Risk: ${linguistic.overall_linguistic_risk || 'Low'}
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div class="bg-slate-50 dark:bg-slate-900/50 p-3.5 rounded-lg border border-slate-100 dark:border-slate-700/60">
              <div class="text-[11px] text-slate-500 uppercase font-semibold">Sensationalism Index</div>
              <div class="text-lg font-bold text-slate-900 dark:text-white mt-1">${linguistic.sensationalism_score || 0} / 100</div>
              <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
                <div class="bg-amber-500 h-full rounded-full" style="width: ${linguistic.sensationalism_score || 0}%"></div>
              </div>
            </div>

            <div class="bg-slate-50 dark:bg-slate-900/50 p-3.5 rounded-lg border border-slate-100 dark:border-slate-700/60">
              <div class="text-[11px] text-slate-500 uppercase font-semibold">Clickbait Score</div>
              <div class="text-lg font-bold text-slate-900 dark:text-white mt-1">${linguistic.clickbait_score || 0} / 100</div>
              <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
                <div class="bg-rose-500 h-full rounded-full" style="width: ${linguistic.clickbait_score || 0}%"></div>
              </div>
            </div>

            <div class="bg-slate-50 dark:bg-slate-900/50 p-3.5 rounded-lg border border-slate-100 dark:border-slate-700/60">
              <div class="text-[11px] text-slate-500 uppercase font-semibold">Detected Tone</div>
              <div class="text-sm font-bold text-slate-900 dark:text-white mt-1 truncate">${linguistic.tone || 'Neutral'}</div>
              <div class="text-[11px] text-slate-400 mt-2">
                ${linguistic.shouting_detected ? '⚠️ Shouting detected' : '✓ Normal capitalization'}
              </div>
            </div>
          </div>
        </div>

        <!-- Sources Checked Table / List -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="database" class="w-4 h-4 text-blue-500"></i>
              Online Sources Evaluated (${sources.length})
            </h3>
            <span class="text-xs text-slate-400">Live via Google News & Search Index</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="py-3 px-4">Source & Domain</th>
                  <th class="py-3 px-4">Credibility Tier</th>
                  <th class="py-3 px-4">Headline / Story Title</th>
                  <th class="py-3 px-4">Published Date</th>
                  <th class="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
                ${sources.length > 0 ? sources.map(s => {
                  const sBadge = this.getCpuBadge(s.credibility_tier, s.credibility_score);
                  return `
                    <tr class="hover:bg-slate-50/70 dark:hover:bg-slate-700/30 transition">
                      <td class="py-3 px-4">
                        <div class="font-bold text-slate-900 dark:text-white">${this.escapeHtml(s.source)}</div>
                        <div class="text-[11px] text-slate-400 font-mono">${this.escapeHtml(s.domain)}</div>
                      </td>
                      <td class="py-3 px-4">
                        <span class="inline-block border px-2 py-0.5 rounded text-[10px] font-semibold ${sBadge.bg}">
                          ${sBadge.label} (${s.credibility_score}/100)
                        </span>
                      </td>
                      <td class="py-3 px-4 font-medium text-slate-800 dark:text-slate-200 max-w-xs md:max-w-md">
                        <div class="line-clamp-2">${this.escapeHtml(s.title)}</div>
                      </td>
                      <td class="py-3 px-4 text-slate-500 whitespace-nowrap">
                        ${this.formatTimeAgo(s.published_at)}
                      </td>
                      <td class="py-3 px-4 text-right whitespace-nowrap">
                        <a 
                          href="${s.url}" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          class="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                        >
                          Visit <i data-lucide="external-link" class="w-3 h-3"></i>
                        </a>
                      </td>
                    </tr>
                  `;
                }).join('') : `
                  <tr>
                    <td colspan="5" class="py-6 text-center text-slate-400 italic">
                      No matching online news sources indexed for this query.
                    </td>
                  </tr>
                `}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Verification Disclaimer & User Feedback -->
        <div class="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-5 border border-slate-200 dark:border-slate-700 flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2 max-w-xl">
            <i data-lucide="info" class="w-4 h-4 text-blue-500 shrink-0 mt-0.5"></i>
            <span>
              <strong>Assistive Verification Notice:</strong> This assessment is generated via algorithmic multi-signal synthesis of real-time search results, domain credibility metrics, and linguistic patterns. It is intended to assist your critical evaluation, not replace professional investigation.
            </span>
          </div>

          <div class="flex items-center gap-3 shrink-0" id="feedback-section-${v.id || 'current'}">
            <span class="text-xs font-medium text-slate-600 dark:text-slate-300">Was this helpful?</span>
            <button 
              onclick="window.App.handleFeedback(${v.id || 'null'}, true)"
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-emerald-50 hover:text-emerald-700 dark:hover:bg-emerald-950/40 dark:hover:text-emerald-400 transition"
            >
              <i data-lucide="thumbs-up" class="w-3.5 h-3.5"></i> Yes
            </button>
            <button 
              onclick="window.App.handleFeedback(${v.id || 'null'}, false)"
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-rose-50 hover:text-rose-700 dark:hover:bg-rose-950/40 dark:hover:text-rose-400 transition"
            >
              <i data-lucide="thumbs-down" class="w-3.5 h-3.5"></i> No
            </button>
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Render Loading Skeletons
   */
  renderSkeletons(count = 6) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += `
        <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 space-y-4">
          <div class="skeleton h-44 rounded-lg w-full"></div>
          <div class="space-y-2">
            <div class="skeleton h-4 rounded w-3/4"></div>
            <div class="skeleton h-4 rounded w-full"></div>
            <div class="skeleton h-4 rounded w-1/2"></div>
          </div>
          <div class="flex justify-between items-center pt-2">
            <div class="skeleton h-5 rounded w-20"></div>
            <div class="skeleton h-8 rounded w-24"></div>
          </div>
        </div>
      `;
    }
    return html;
  },

  /**
   * Render Empty Results State
   */
  renderEmptyState(title = 'No Results Found', subtitle = 'Try adjusting your search keywords or topic.') {
    return `
      <div class="col-span-full text-center py-16 px-4">
        <div class="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
          <i data-lucide="search-x" class="w-8 h-8"></i>
        </div>
        <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-1">${title}</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">${subtitle}</p>
        <button 
          onclick="window.App.switchCategory('all')" 
          class="inline-flex items-center gap-2 bg-blue-600 text-white text-xs font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <i data-lucide="newspaper" class="w-4 h-4"></i> Back to Top Stories
        </button>
      </div>
    `;
  }
};

window.UIComponents = UIComponents;
