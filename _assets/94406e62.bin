/* global React */
/* ============ Shared UI primitives & site chrome ============ */

const IconSearch = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
  </svg>
);
const IconBookmark = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
  </svg>
);
const IconBell = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
  </svg>
);
const IconSparkle = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 14} height={p.size || 14} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2 2M16.4 16.4l2 2M16.4 5.6l2-2M5.6 18.4l2-2" />
  </svg>
);
const IconArrow = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 14} height={p.size || 14} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);
const IconShare = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
    <path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4" />
  </svg>
);
const IconList = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" x2="21" y1="6" y2="6" /><line x1="8" x2="21" y1="12" y2="12" /><line x1="8" x2="21" y1="18" y2="18" />
    <line x1="3" x2="3.01" y1="6" y2="6" /><line x1="3" x2="3.01" y1="12" y2="12" /><line x1="3" x2="3.01" y1="18" y2="18" />
  </svg>
);
const IconGrid = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 16} height={p.size || 16} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
    <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
  </svg>
);
const IconChev = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 14} height={p.size || 14} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
);
const IconCheck = (p) => (
  <svg viewBox="0 0 24 24" width={p.size || 14} height={p.size || 14} fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

// Site header bar (used at top of every page mock)
const SiteHeader = ({ user = "李" }) => (
  <header className="site-header">
    <a className="site-logo">
      <span className="site-logo-mark">环</span>
      <span className="site-logo-text">
        <b>环球新闻</b>
        <small>HUANQIU · BERT</small>
      </span>
    </a>
    <div className="site-search">
      <IconSearch />
      <input placeholder="搜索新闻关键词、话题或类别..." />
      <kbd>⌘ K</kbd>
    </div>
    <div className="site-header-actions">
      <span className="header-pill is-ai">
        <span className="dot"></span>AI 分类
      </span>
      <span className="header-icon"><IconBell /><span className="badge"></span></span>
      <span className="header-icon"><IconBookmark /></span>
      <span className="header-avatar">{user}</span>
    </div>
  </header>
);

// Category strip below header
const SubStrip = ({ active = "首页" }) => {
  const cats = ["首页", "时政", "财经", "科技", "体育", "娱乐", "社会", "教育", "健康", "房产", "游戏"];
  return (
    <div className="site-substrip">
      <span className="date">星期四 · 2026 年 5 月 18 日</span>
      {cats.map((c) => (
        <a key={c} className={c === active ? "is-active" : ""}>{c}</a>
      ))}
    </div>
  );
};

Object.assign(window, {
  IconSearch, IconBookmark, IconBell, IconSparkle, IconArrow, IconShare,
  IconList, IconGrid, IconChev, IconCheck,
  SiteHeader, SubStrip,
});
