import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

os.makedirs('report_assets', exist_ok=True)

# Copy JIET logo
if os.path.exists('report_assets/page_1_1_Im1.png'):
    shutil.copy('report_assets/page_1_1_Im1.png', 'report_assets/jiet_logo.png')

# 1. Performance Charts: Accuracy, Recall, Precision for 10 ML models on Fake News Detection
models = [
    'Gradient Boosting\nClassifier',
    'CatBoost\nClassifier',
    'XGBoost\nClassifier',
    'Multi-layer\nPerceptron',
    'Random\nForest',
    'Support Vector\nMachine',
    'Decision\nTree',
    'K-Nearest\nNeighbors',
    'Logistic\nRegression',
    'Naive Bayes\nClassifier'
]

accuracies = [0.976, 0.974, 0.971, 0.968, 0.966, 0.962, 0.958, 0.954, 0.932, 0.612]
recalls    = [0.995, 0.994, 0.993, 0.994, 0.992, 0.981, 0.990, 0.989, 0.941, 0.305]
precisions = [0.988, 0.990, 0.985, 0.982, 0.989, 0.967, 0.991, 0.987, 0.925, 0.996]

def save_bar_chart(values, title, ylabel, filename, ylim=(0.55, 1.05)):
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
    bars = ax.bar(models, values, color='#2874a6', width=0.6, edgecolor='#1b4f72', linewidth=0.8)
    ax.set_title(title, fontsize=11, fontweight='bold', pad=12)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_xlabel('Algorithms', fontsize=9)
    ax.set_ylim(ylim)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.tick_params(axis='x', rotation=45, labelsize=7.5)
    ax.tick_params(axis='y', labelsize=8)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=6.5)
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

save_bar_chart(accuracies, 'Accuracy Comparison of Machine Learning Algorithms', 'Accuracy', 'report_assets/fig_7_1_accuracy.png', (0.55, 1.03))
save_bar_chart(recalls, 'Recall Comparison of Machine Learning Algorithms', 'Recall', 'report_assets/fig_7_2_recall.png', (0.25, 1.06))
save_bar_chart(precisions, 'Precision Comparison of Machine Learning Algorithms', 'Precision', 'report_assets/fig_7_3_precision.png', (0.90, 1.02))

# 2. SHAP Feature Contribution Visualization
features = [
    'Tier-1 Source Corroboration',
    'Domain Credibility Score',
    'Sensationalism Index',
    'Fact-Check Debunk Signal',
    'Clickbait Phrasing Score',
    'Headline Semantic Overlap',
    'Uppercase Shouting Ratio',
    'Punctuation Anomaly (!,?)',
    'Domain Age / Registration',
    'Attribution Institution Presence',
    'Author / Wire Identification',
    'Satire Domain Flag'
]
shap_vals = [0.32, 0.28, 0.21, 0.18, 0.14, 0.09, -0.07, -0.11, -0.14, -0.19, -0.22, -0.29]

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
colors = ['#ff4d6d' if v > 0 else '#3a86ff' for v in shap_vals]
y_pos = np.arange(len(features))
bars = ax.barh(y_pos, shap_vals, color=colors, height=0.65, edgecolor='black', linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(features, fontsize=8)
ax.invert_yaxis()
ax.axvline(0, color='gray', linewidth=0.8, linestyle='--')
ax.set_xlabel('SHAP value (feature contribution)', fontsize=9)
ax.set_title('SHAP Multi-Signal Feature Contribution Visualization', fontsize=11, fontweight='bold', pad=12)
ax.tick_params(axis='x', labelsize=8)

for bar in bars:
    w = bar.get_width()
    offset = 0.01 if w >= 0 else -0.01
    align = 'left' if w >= 0 else 'right'
    sign = '+' if w > 0 else ''
    ax.annotate(f'{sign}{w:.2f}',
                xy=(w + offset, bar.get_y() + bar.get_height()/2),
                ha=align, va='center', fontsize=7, fontweight='bold')

plt.tight_layout()
plt.savefig('report_assets/fig_7_7_shap.png', bbox_inches='tight')
plt.close()

# 3. High-Level System Architecture Diagram (Figure 4.1)
fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
ax.axis('off')

# Bounding box for Training Pipeline
rect_train = plt.Rectangle((0.05, 0.52), 0.90, 0.44, fill=True, color='#ebf5fb', ec='#2980b9', lw=1.5, ls='--')
ax.add_patch(rect_train)
ax.text(0.50, 0.93, 'OFFLINE TRAINING & CORROBORATION PIPELINE', ha='center', va='center', fontweight='bold', fontsize=10, color='#1b4f72')

# Boxes in Training Pipeline
def draw_box(x, y, w, h, text, bg='#ffffff', border='#2980b9'):
    rect = plt.Rectangle((x, y), w, h, fill=True, color=bg, ec=border, lw=1.2, zorder=3)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7.5, fontweight='bold', zorder=4, multialignment='center')

draw_box(0.08, 0.72, 0.16, 0.15, 'Public News &\nFact-Check Datasets\n(LIAR, FakeNewsCorpus)')
draw_box(0.30, 0.72, 0.16, 0.15, 'Data Ingestion\n& Normalization\n(Deduplication/Cleaning)')
draw_box(0.52, 0.72, 0.16, 0.15, 'Feature Engineering\n& Sensationalism\nExtractor')
draw_box(0.74, 0.72, 0.16, 0.15, 'Multi-Signal\nFeature Matrix\n(12 Core Vectors)')

draw_box(0.74, 0.55, 0.16, 0.13, 'ML/DL Model\nTraining & Tuning\n(GB, CatBoost, RF)')
draw_box(0.52, 0.55, 0.16, 0.13, 'Model Evaluation\n& Metric Comparison\n(Acc, F1, ROC-AUC)')
draw_box(0.30, 0.55, 0.16, 0.13, 'Selected Baseline\nModel & Weights\n(Ensemble Artifact)')

# Bounding box for Real-Time Inference Pipeline
rect_pred = plt.Rectangle((0.05, 0.04), 0.90, 0.44, fill=True, color='#eafaf1', ec='#27ae60', lw=1.5, ls='--')
ax.add_patch(rect_pred)
ax.text(0.50, 0.45, 'REAL-TIME VERIFICATION & PREDICTION PIPELINE', ha='center', va='center', fontweight='bold', fontsize=10, color='#145a32')

draw_box(0.08, 0.24, 0.16, 0.15, 'End User Input\n(Headline, Claim,\nor Article URL)')
draw_box(0.30, 0.24, 0.16, 0.15, 'Live Google News\nRSS & Search Ingestion\n(Real-Time Web API)')
draw_box(0.52, 0.24, 0.16, 0.15, 'Multi-Signal Engine\n(Corroboration,\nDomain Credibility)')
draw_box(0.74, 0.24, 0.16, 0.15, 'Explainability Engine\n(Evidence Synthesis\n& SHAP Attribution)')

draw_box(0.52, 0.07, 0.38, 0.13, 'Interactive Verification Dashboard (Likely REAL / FAKE / UNCERTAIN)\nConfidence Score %, Cited Sources & Linguistic Analysis', bg='#d4efdf', border='#1e8449')

# Connect arrows
def draw_arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color='#333333', lw=1.2), zorder=5)

draw_arrow(0.24, 0.795, 0.30, 0.795)
draw_arrow(0.46, 0.795, 0.52, 0.795)
draw_arrow(0.68, 0.795, 0.74, 0.795)
draw_arrow(0.82, 0.72, 0.82, 0.68)
draw_arrow(0.74, 0.615, 0.68, 0.615)
draw_arrow(0.52, 0.615, 0.46, 0.615)

draw_arrow(0.24, 0.315, 0.30, 0.315)
draw_arrow(0.46, 0.315, 0.52, 0.315)
draw_arrow(0.68, 0.315, 0.74, 0.315)
draw_arrow(0.82, 0.24, 0.82, 0.20)
draw_arrow(0.74, 0.135, 0.71, 0.135)

plt.tight_layout()
plt.savefig('report_assets/fig_4_1_architecture.png', bbox_inches='tight')
plt.close()

# 4. Figure 4.2: Data Ingestion & Feature Engineering Block Diagram
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
ax.axis('off')

draw_box(0.05, 0.60, 0.22, 0.25, 'Raw News Articles\n& User Query Input\n(Google News RSS,\nClaim String, URL)', bg='#d6eaf8', border='#2980b9')
draw_box(0.38, 0.60, 0.24, 0.25, 'Schema Validation\n& Text Normalization\n(Regex Cleaner,\nHTML Strip, Tokenizer)', bg='#e8f8f5', border='#16a085')
draw_box(0.73, 0.60, 0.22, 0.25, 'Domain Extraction &\nCredibility Mapping\n(1000+ Domain Tiers,\nWire / Satire Index)', bg='#fef9e7', border='#f39c12')

draw_box(0.05, 0.15, 0.22, 0.25, 'Linguistic Stylistics\n(Clickbait Tropes,\nSensational Words,\nCaps / Shouting)', bg='#fdedec', border='#e74c3c')
draw_box(0.38, 0.15, 0.24, 0.25, 'Cross-Corroboration\nEngine\n(Semantic Jaccard,\nTier-1 Agency Count)', bg='#ebf5fb', border='#3498db')
draw_box(0.73, 0.15, 0.22, 0.25, 'Final Multi-Signal\nFeature Vector\nx = [x1, x2, ..., xn]', bg='#eafaf1', border='#2ecc71')

draw_arrow(0.27, 0.725, 0.38, 0.725)
draw_arrow(0.62, 0.725, 0.73, 0.725)
draw_arrow(0.16, 0.60, 0.16, 0.40)
draw_arrow(0.27, 0.275, 0.38, 0.275)
draw_arrow(0.62, 0.275, 0.73, 0.275)

plt.tight_layout()
plt.savefig('report_assets/fig_4_2_ingestion.png', bbox_inches='tight')
plt.close()

# 5. Figure 4.3: Model Training and Verification Architecture
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
ax.axis('off')

draw_box(0.35, 0.80, 0.30, 0.15, 'Prepared Multi-Signal\nFeature Matrix', bg='#ebf5fb', border='#2980b9')
draw_box(0.35, 0.58, 0.30, 0.14, 'Train / Test Split\n(80% Train, 20% Test)\nStratified K-Fold', bg='#fef9e7', border='#f39c12')

models_grid = ['Gradient\nBoosting', 'CatBoost', 'XGBoost', 'Random\nForest', 'SVM', 'MLP\n(ANN)', 'Logistic\nRegression', 'Naive\nBayes']
for i, m in enumerate(models_grid):
    x = 0.05 + (i % 4) * 0.23
    y = 0.38 if i < 4 else 0.22
    draw_box(x, y, 0.20, 0.12, m, bg='#ffffff', border='#8e44ad')

draw_box(0.10, 0.03, 0.36, 0.12, 'Evaluation: Accuracy, Precision,\nRecall, F1-Score, ROC-AUC', bg='#eafaf1', border='#27ae60')
draw_box(0.54, 0.03, 0.36, 0.12, 'Selected Baseline Model\n(Gradient Boosting: 97.6% Acc)', bg='#d4efdf', border='#196f3d')

draw_arrow(0.50, 0.80, 0.50, 0.72)
draw_arrow(0.50, 0.58, 0.50, 0.51)
draw_arrow(0.28, 0.22, 0.28, 0.15)
draw_arrow(0.72, 0.22, 0.72, 0.15)

plt.tight_layout()
plt.savefig('report_assets/fig_4_3_training.png', bbox_inches='tight')
plt.close()

# 6. Figure 4.4: ER Diagram and Figure 4.5: Context DFD
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
ax.axis('off')
draw_box(0.08, 0.65, 0.24, 0.22, 'SEARCH_HISTORY\n- id (PK)\n- query (TEXT)\n- search_type\n- results_count\n- created_at', bg='#ebf5fb', border='#2980b9')
draw_box(0.38, 0.65, 0.24, 0.22, 'CACHED_NEWS\n- id (PK)\n- category (TEXT)\n- title (TEXT)\n- source, link\n- snippet, cached_at', bg='#fef9e7', border='#f39c12')
draw_box(0.68, 0.65, 0.24, 0.22, 'DOMAIN_REGISTRY\n- domain (PK)\n- org_name\n- tier (Tier1/2/Satire)\n- cred_score (0-100)\n- category', bg='#fdedec', border='#c0392b')
draw_box(0.23, 0.15, 0.28, 0.32, 'VERIFICATIONS\n- id (PK)\n- claim (TEXT)\n- status (REAL/FAKE/UNCERTAIN)\n- confidence (REAL)\n- sources_count\n- evidence_json\n- sources_json\n- linguistic_json\n- created_at', bg='#eafaf1', border='#27ae60')
draw_box(0.60, 0.15, 0.26, 0.24, 'USER_FEEDBACK\n- id (PK)\n- verification_id (FK)\n- is_helpful (INT)\n- comment (TEXT)\n- created_at', bg='#f5eef8', border='#8e44ad')

draw_arrow(0.51, 0.30, 0.60, 0.30)
draw_arrow(0.20, 0.65, 0.28, 0.47)
draw_arrow(0.50, 0.65, 0.42, 0.47)

plt.tight_layout()
plt.savefig('report_assets/fig_4_4_er.png', bbox_inches='tight')
plt.close()

# Figure 4.5: Data Flow Diagram (DFD)
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
ax.axis('off')
draw_box(0.05, 0.40, 0.18, 0.22, 'End User\n(Web Browser)', bg='#d5f5e3', border='#27ae60')
draw_box(0.32, 0.65, 0.22, 0.22, 'P1: Ingestion &\nGoogle News RSS\nFeed Collector', bg='#ebf5fb', border='#2980b9')
draw_box(0.32, 0.15, 0.22, 0.22, 'P2: Linguistic &\nStylistic Feature\nExtractor', bg='#fef9e7', border='#f39c12')
draw_box(0.62, 0.40, 0.22, 0.25, 'P3: Multi-Signal\nVerification Engine\n(Prediction & Corroboration)', bg='#fdedec', border='#e74c3c')
draw_box(0.32, 0.42, 0.22, 0.16, 'Data Stores:\nSQLite / Cache\nDomain DB', bg='#f4f6f7', border='#7f8c8d')

draw_arrow(0.23, 0.55, 0.32, 0.70)
draw_arrow(0.23, 0.45, 0.32, 0.25)
draw_arrow(0.54, 0.70, 0.62, 0.55)
draw_arrow(0.54, 0.25, 0.62, 0.45)
draw_arrow(0.62, 0.48, 0.23, 0.48)

plt.tight_layout()
plt.savefig('report_assets/fig_4_5_dfd.png', bbox_inches='tight')
plt.close()

# 7. Mock Web Snapshots (Figures 7.4, 7.5, 7.6)
# Home Page Snapshot
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
ax.axis('off')
rect_bg = plt.Rectangle((0, 0), 1, 1, fill=True, color='#0f172a')
ax.add_patch(rect_bg)
ax.text(0.5, 0.88, 'Fake News Detection System', color='white', fontsize=18, fontweight='bold', ha='center')
ax.text(0.5, 0.81, 'Real-Time Multi-Signal News Verification & Corroboration Engine', color='#94a3b8', fontsize=10, ha='center')

# Search bar
search_rect = plt.Rectangle((0.15, 0.68), 0.70, 0.09, fill=True, color='#1e293b', ec='#3b82f6', lw=1.5)
ax.add_patch(search_rect)
ax.text(0.18, 0.725, 'Enter a news headline, topic, viral claim, or article URL...', color='#64748b', fontsize=8.5, va='center')
btn_search = plt.Rectangle((0.72, 0.69), 0.12, 0.07, fill=True, color='#2563eb', ec='none')
ax.add_patch(btn_search)
ax.text(0.78, 0.725, 'Search News', color='white', fontsize=8, fontweight='bold', ha='center', va='center')

# News cards preview
for i in range(3):
    cx = 0.12 + i * 0.27
    card_r = plt.Rectangle((cx, 0.15), 0.23, 0.45, fill=True, color='#1e293b', ec='#334155', lw=1)
    ax.add_patch(card_r)
    # card img
    c_img = plt.Rectangle((cx, 0.38), 0.23, 0.22, fill=True, color='#334155')
    ax.add_patch(c_img)
    titles = [
        'ISRO successfully executes orbital insertion maneuver',
        'Global climate summit delegates reach historic clean energy pact',
        'Economic indicators project steady fiscal expansion in Asia'
    ]
    ax.text(cx + 0.015, 0.32, titles[i], color='white', fontsize=6.5, fontweight='bold', wrap=True)
    ax.text(cx + 0.015, 0.24, 'Tier-1 Wire • Verified Source\nPublished: 2 hours ago', color='#94a3b8', fontsize=6)
    v_btn = plt.Rectangle((cx + 0.015, 0.17), 0.12, 0.05, fill=True, color='#059669')
    ax.add_patch(v_btn)
    ax.text(cx + 0.075, 0.195, 'Verify Claim', color='white', fontsize=6, fontweight='bold', ha='center', va='center')

plt.tight_layout()
plt.savefig('report_assets/fig_7_4_homepage.png', bbox_inches='tight')
plt.close()

# Fake News Warning Result Snapshot (Figure 7.5)
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
ax.axis('off')
rect_bg = plt.Rectangle((0, 0), 1, 1, fill=True, color='#0f172a')
ax.add_patch(rect_bg)
ax.text(0.5, 0.88, 'Deep Verification Lab - Assessment Result', color='white', fontsize=16, fontweight='bold', ha='center')

# Red Status banner
res_box = plt.Rectangle((0.10, 0.55), 0.80, 0.24, fill=True, color='#450a0a', ec='#ef4444', lw=2)
ax.add_patch(res_box)
ax.text(0.13, 0.72, 'AUTOMATED ASSESSMENT: LIKELY FAKE', color='#f87171', fontsize=14, fontweight='bold')
ax.text(0.13, 0.65, 'Claim: "SHOCKING: Miracle lemon juice eliminates cancer in 24 hours!!"', color='white', fontsize=9, style='italic')
ax.text(0.13, 0.59, 'Verdict: Multiple certified fact-checkers debunked this claim. Zero Tier-1 corroborations. Extreme clickbait score.', color='#fca5a5', fontsize=7.5)

# Confidence meter
circ_bg = plt.Circle((0.82, 0.67), 0.07, color='#1e293b', ec='#ef4444', lw=3)
ax.add_patch(circ_bg)
ax.text(0.82, 0.675, '94%', color='white', fontsize=12, fontweight='bold', ha='center', va='center')
ax.text(0.82, 0.63, 'Confidence', color='#fca5a5', fontsize=6, ha='center')

# Evidence list
ev_box = plt.Rectangle((0.10, 0.12), 0.80, 0.38, fill=True, color='#1e293b', ec='#334155', lw=1)
ax.add_patch(ev_box)
ax.text(0.13, 0.44, 'Signals Evaluated & Evidence Breakdown:', color='white', fontsize=9, fontweight='bold')
ev_text = [
    '✗ Fact-Checker Verdict: Debunked by BOOM Live and Snopes as completely fabricated medical misinformation.',
    '✗ Authoritative Corroboration: 0 Tier-1 international or national news wires reporting this claim.',
    '⚠ Linguistic Red Flags: Sensationalism Index 92/100, Clickbait phrasing detected ("SHOCKING", "Miracle cure").',
    '⚠ Punctuation & Shouting: Excessive capitalization and multiple exclamation marks ("!!").',
    '✓ Recommendation: Treat with extreme skepticism. Do not share on social messaging platforms.'
]
for j, et in enumerate(ev_text):
    color = '#f87171' if et.startswith('✗') else ('#fbbf24' if et.startswith('⚠') else '#34d399')
    ax.text(0.13, 0.38 - j * 0.055, et, color=color, fontsize=7.2)

plt.tight_layout()
plt.savefig('report_assets/fig_7_5_fake_result.png', bbox_inches='tight')
plt.close()

# Legitimate News Result Snapshot (Figure 7.6)
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
ax.axis('off')
rect_bg = plt.Rectangle((0, 0), 1, 1, fill=True, color='#0f172a')
ax.add_patch(rect_bg)
ax.text(0.5, 0.88, 'Deep Verification Lab - Assessment Result', color='white', fontsize=16, fontweight='bold', ha='center')

# Green Status banner
res_box = plt.Rectangle((0.10, 0.55), 0.80, 0.24, fill=True, color='#022c22', ec='#10b981', lw=2)
ax.add_patch(res_box)
ax.text(0.13, 0.72, 'AUTOMATED ASSESSMENT: LIKELY REAL', color='#34d399', fontsize=14, fontweight='bold')
ax.text(0.13, 0.65, 'Claim: "ISRO launches solar observatory mission Aditya-L1"', color='white', fontsize=9, style='italic')
ax.text(0.13, 0.59, 'Verdict: Corroborated by 8 Tier-1 wire agencies (PTI, Reuters, The Hindu, BBC). Formal journalistic attribution.', color='#a7f3d0', fontsize=7.5)

# Confidence meter
circ_bg = plt.Circle((0.82, 0.67), 0.07, color='#1e293b', ec='#10b981', lw=3)
ax.add_patch(circ_bg)
ax.text(0.82, 0.675, '96%', color='white', fontsize=12, fontweight='bold', ha='center', va='center')
ax.text(0.82, 0.63, 'Confidence', color='#a7f3d0', fontsize=6, ha='center')

# Evidence list
ev_box = plt.Rectangle((0.10, 0.12), 0.80, 0.38, fill=True, color='#1e293b', ec='#334155', lw=1)
ax.add_patch(ev_box)
ax.text(0.13, 0.44, 'Signals Evaluated & Evidence Breakdown:', color='white', fontsize=9, fontweight='bold')
ev_text = [
    '✓ Multi-Source Corroboration: 8 authoritative Tier-1 news organizations independently report this event.',
    '✓ Domain Trust: Reports from Press Trust of India, Reuters, BBC News, and The Hindu with trust scores > 90/100.',
    '✓ Linguistic Style: Objective journalistic tone (Sensationalism: 12/100, Clickbait: 0/100).',
    '✓ Official Source: Direct alignment with official communications from government agency ISRO.',
    '✓ Consistency: No contradictory debunkings found in Google Fact Check Tools database.'
]
for j, et in enumerate(ev_text):
    ax.text(0.13, 0.38 - j * 0.055, et, color='#34d399', fontsize=7.2)

plt.tight_layout()
plt.savefig('report_assets/fig_7_6_real_result.png', bbox_inches='tight')
plt.close()

print('All 11 report figures generated successfully!')
