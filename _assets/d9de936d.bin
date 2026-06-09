/* global React */

/* ============ Design system overview artboard ============ */
const SystemBoard = () => (
  <div className="sys-board">
    <div className="sys-head">
      <div className="sys-head-mark">环</div>
      <div>
        <h1>编辑部 × 智能</h1>
        <div className="sub">
          重新定义环球新闻 ——
          <span className="red"> 以中文报刊编辑的严谨 </span>
          为骨,
          <span className="navy"> 以 BERT 智能分析的精度 </span>
          为引擎。
        </div>
      </div>
      <div className="sys-head-stamp">
        UI PROPOSAL<br />
        2026 · 05 · 18<br />
        <span className="v">v1.0</span>
      </div>
    </div>

    {/* Direction quote */}
    <section className="sys-statement">
      <div className="sys-quote">
        新闻不该被千篇一律的卡片淹没。
        我们让每一条头条像
        <span className="em">报刊头版</span>
        一样被精心排版,
        每一次智能分析像
        <span className="ai-em">实验室仪表</span>
        一样可被验证。
      </div>
      <div className="sys-side">
        <h4>核心原则</h4>
        <ul>
          <li><b>编辑感</b><span>采用衬线大字号标题、首字下沉、引文、双划线分隔等报刊版式语言,告别通用 CMS 卡片。</span></li>
          <li><b>智能感</b><span>所有 AI 相关元素采用「藏青 + 等宽字 + 数据轨道」,与新闻内容视觉上明确分层。</span></li>
          <li><b>纸质感</b><span>米白底色 #FAF7F2 替代纯白,接近报纸质感,减少长时间阅读疲劳。</span></li>
          <li><b>克制感</b><span>红色只用于头条 / 强调 / AI 之外的品牌色;90% 内容是黑白与灰度。</span></li>
        </ul>
      </div>
    </section>

    {/* Colors */}
    <div className="sys-sec-head">
      <span className="idx">01 / 04</span>
      <h2>色彩系统</h2>
      <span className="desc">墨色 + 米白为主,品牌红与 AI 藏青双轨。
        每一种颜色都标注语义,避免临时取色。</span>
    </div>
    <div className="swatch-grid">
      <div className="sw-group-label">底色 & 墨色</div>
      <Swatch name="Paper" code="#FAF7F2" hex="#FAF7F2" desc="页面底色 · 纸感" />
      <Swatch name="Paper 2" code="#F2EDE2" hex="#F2EDE2" desc="次级表面" />
      <Swatch name="Surface" code="#FFFFFF" hex="#FFFFFF" desc="卡片背景" />
      <Swatch name="Ink" code="#0F1419" hex="#0F1419" desc="主文 · 顶栏" textOnDark />
      <Swatch name="Ink 3" code="#5C5650" hex="#5C5650" desc="正文备用 · 元信息" textOnDark />
      <Swatch name="Border" code="#D5CDBA" hex="#D5CDBA" desc="分隔线 · 线条" />

      <div className="sw-group-label">品牌红 (头条 / 强调)</div>
      <Swatch name="Red" code="#C8201E" hex="#C8201E" desc="主品牌色" textOnDark />
      <Swatch name="Red Deep" code="#8B0F0D" hex="#8B0F0D" desc="hover / 渐变深处" textOnDark />
      <Swatch name="Red Soft" code="#FBEDEC" hex="#FBEDEC" desc="背景柔色" />

      <div className="sw-group-label">AI 藏青 (智能模块)</div>
      <Swatch name="AI Navy" code="#1F3A5F" hex="#1F3A5F" desc="AI 主色" textOnDark />
      <Swatch name="AI Blue" code="#2C5491" hex="#2C5491" desc="渐变中段" textOnDark />
      <Swatch name="AI Glow" code="#5C8BD9" hex="#5C8BD9" desc="高亮 · 数据" textOnDark />

      <div className="sw-group-label">类别色 (新闻分类语义)</div>
      <Swatch name="科技" code="#2C5491" hex="#2C5491" desc="Technology" textOnDark />
      <Swatch name="体育" code="#1F7A50" hex="#1F7A50" desc="Sports" textOnDark />
      <Swatch name="财经" code="#8B5A1E" hex="#8B5A1E" desc="Finance" textOnDark />
      <Swatch name="娱乐" code="#B0367A" hex="#B0367A" desc="Entertainment" textOnDark />
      <Swatch name="时政" code="#C8201E" hex="#C8201E" desc="Politics" textOnDark />
      <Swatch name="教育" code="#6B4FA8" hex="#6B4FA8" desc="Education" textOnDark />
    </div>

    {/* Type */}
    <div className="sys-sec-head">
      <span className="idx">02 / 04</span>
      <h2>字体系统</h2>
      <span className="desc">思源宋体 Noto Serif SC 用于标题与正文 (报刊感) ·
        Inter 用于界面元素 · JetBrains Mono 用于数据。</span>
    </div>
    <div className="type-spec">
      <TypeRow meta={["Display XL", "Serif 700 / 56px / -2.5%"]}>
        <div className="t-display-xl">头条标题</div>
      </TypeRow>
      <TypeRow meta={["Display L", "Serif 700 / 36px / -1.5%"]}>
        <div className="t-display-l">栏目标题与文章标题</div>
      </TypeRow>
      <TypeRow meta={["Display M", "Serif 700 / 22px / -1%"]}>
        <div className="t-display-m">卡片标题、侧栏标题</div>
      </TypeRow>
      <TypeRow meta={["Lead", "Serif Italic / 18px"]}>
        <div className="t-lead">导语与摘要采用衬线斜体,营造编辑笔触</div>
      </TypeRow>
      <TypeRow meta={["Body", "Inter 400 / 15px / 1.65"]}>
        <div className="t-body">界面正文、按钮文字与说明,使用无衬线以保证可读性与现代感。</div>
      </TypeRow>
      <TypeRow meta={["Eyebrow", "Inter 700 / 11px / +22%"]}>
        <div className="t-eyebrow">栏目导眼 · BREAKING</div>
      </TypeRow>
      <TypeRow meta={["Meta", "Mono / 12px"]}>
        <div className="t-meta">2026.05.18 · 14:32 · 1,284 reads · BERT-CNN v2.1</div>
      </TypeRow>
    </div>

    {/* Components */}
    <div className="sys-sec-head">
      <span className="idx">03 / 04</span>
      <h2>组件原子</h2>
      <span className="desc">按钮、标签、徽章、分类点、置信度可视化 —— 全部统一节奏。</span>
    </div>
    <div className="comp-grid">
      <div className="comp-card">
        <h5>按钮</h5>
        <div className="comp-card-body">
          <button className="btn-red">订阅栏目</button>
          <button className="btn-ink">查看全部</button>
          <button className="btn-ghost">取消</button>
          <button className="btn-ai"><IconSparkle />AI 智能分类</button>
        </div>
      </div>
      <div className="comp-card">
        <h5>分类标签</h5>
        <div className="comp-card-body" style={{flexDirection: 'row', flexWrap: 'wrap', gap: '12px'}}>
          <span className="cat-chip tech">科技 · TECH</span>
          <span className="cat-chip sports">体育 · SPORTS</span>
          <span className="cat-chip finance">财经 · FINANCE</span>
          <span className="cat-chip ent">娱乐 · ENT</span>
          <span className="cat-chip politics">时政 · POL</span>
          <span className="cat-chip edu">教育 · EDU</span>
        </div>
      </div>
      <div className="comp-card">
        <h5>AI 标记 & 置信度</h5>
        <div className="comp-card-body" style={{gap: '14px'}}>
          <span className="ai-chip"><span className="dot"></span>AI 分类 BERT-CNN</span>
          <span className="tag-red-out">头条</span>
          <span className="tag-ink">独家</span>
          <div className="conf-mini">
            <div className="lbl"><span>分类置信度</span><b>94.2%</b></div>
            <div className="bar"><i style={{width: '94%'}}></i></div>
          </div>
        </div>
      </div>
    </div>

    {/* Principles */}
    <div className="sys-sec-head">
      <span className="idx">04 / 04</span>
      <h2>设计原则</h2>
      <span className="desc">每一个版面决策回归这四条。</span>
    </div>
    <div className="principle-grid">
      <div className="principle">
        <div className="num">PRINCIPLE 01</div>
        <h4>排版即权威</h4>
        <p>用大字号衬线标题、双划线、首字下沉,让新闻读起来像报纸,而不是 feed 流。</p>
      </div>
      <div className="principle">
        <div className="num">PRINCIPLE 02</div>
        <h4>智能可被验证</h4>
        <p>每个 AI 输出都附带置信度、模型版本、耗时,
          让用户理解「这是模型说的」,而非凭空给结果。</p>
      </div>
      <div className="principle">
        <div className="num">PRINCIPLE 03</div>
        <h4>克制用色</h4>
        <p>90% 的内容是黑白米色,
          红色与藏青只用于真正需要强调的瞬间。</p>
      </div>
      <div className="principle">
        <div className="num">PRINCIPLE 04</div>
        <h4>密度有节奏</h4>
        <p>头条要宽松呼吸,列表要紧凑高效,
          AI 工作台要专业精密 —— 同一系统,不同密度。</p>
      </div>
    </div>
  </div>
);

const Swatch = ({ name, code, hex, desc, textOnDark }) => (
  <div className="swatch">
    <div className="sw-color" style={{ background: hex }}>
      {/* optional preview */}
    </div>
    <div className="sw-label">
      <b>{name}</b>
      <code>{code}</code>
      <div style={{marginTop: 2, color: 'var(--ink-4)', fontSize: 10}}>{desc}</div>
    </div>
  </div>
);

const TypeRow = ({ meta, children }) => (
  <div className="type-row">
    <div className="meta">
      <b>{meta[0]}</b>
      {meta[1]}
    </div>
    <div>{children}</div>
  </div>
);

Object.assign(window, { SystemBoard });
