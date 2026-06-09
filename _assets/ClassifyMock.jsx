/* global React, SiteHeader, SubStrip, IconSparkle, IconArrow, IconCheck */

const ClassifyMock = () => (
  <div className="cls">
    <SiteHeader />
    <SubStrip active="首页" />

    <div className="cls-body">
      {/* Page header */}
      <div className="cls-head">
        <div>
          <div className="lab"><span className="dot"></span>AI 工作台 · INTELLIGENCE WORKBENCH</div>
          <h1>文本分类 <span className="vrn">BERT-CNN v2.1</span></h1>
          <div className="sub">
            把任何中文新闻文本贴进左侧,
            BERT 会在 100ms 内为你判别 10 个新闻领域之一,
            并给出置信度、Top-K 候选与可对比的模型选择。
          </div>
        </div>
        <div className="stats">
          <div className="st"><b>94.7%</b><small>BERT 准确率</small></div>
          <div className="st"><b>86<span style={{fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--ink-3)'}}>ms</span></b><small>平均耗时</small></div>
          <div className="st"><b>12,408</b><small>今日已分类</small></div>
        </div>
      </div>

      {/* Main: input + result */}
      <div className="cls-grid">
        <div className="cls-input">
          <div className="cls-input-head">
            <h3><span className="num">1</span>新闻内容</h3>
            <div className="examples">
              <small>示例:</small>
              <span className="ex-chip is-on">时政</span>
              <span className="ex-chip">科技</span>
              <span className="ex-chip">财经</span>
              <span className="ex-chip">体育</span>
              <span className="ex-chip">娱乐</span>
            </div>
          </div>
          <div className="cls-textarea">
            <span className="ghost">国务院今日召开常务会议,听取关于推进高质量发展和促进民营经济发展的工作汇报,部署进一步优化营商环境、降低企业融资成本的具体措施。会议强调要加大对中小微企业的支持力度,确保各项惠企政策落到实处。</span>
            <span className="cursor"></span>
          </div>
          <div className="cls-input-foot">
            <div className="count">
              <span><b>168</b> / 500 字</span>
              <span className="ok">长度适宜</span>
            </div>
            <div className="actions">
              <button className="cls-btn">清空</button>
              <button className="cls-btn is-primary"><IconSparkle />开始分析<span className="kbd">⌘ ↵</span></button>
            </div>
          </div>
        </div>

        <div className="cls-result">
          {/* Hero result */}
          <div className="cls-result-hero">
            <div className="lab"><span className="ck"><IconCheck /></span>分类结果 · CLASSIFICATION OUTPUT</div>
            <div className="cat-big">时政</div>
            <div className="cat-meta">
              <span>POLITICS</span>
              <span>·</span>
              <span><b>BERT-CNN</b> v2.1</span>
              <span>·</span>
              <span>78<span style={{opacity: 0.6}}>ms</span></span>
            </div>
            <div className="conf-wrap">
              <div className="conf-row">
                <span>置信度 / CONFIDENCE</span>
                <span className="num">99.4<small>%</small></span>
              </div>
              <div className="conf-track">
                <div className="fill" style={{width: '99.4%'}}></div>
                <div className="ticks">
                  {Array.from({length: 9}).map((_, i) => <i key={i}></i>)}
                </div>
              </div>
              <div className="conf-hint">
                模型对该类别非常确定。Top-2 类别 (财经) 仅为 0.4%,可放心采用本结果。
              </div>
            </div>
          </div>

          {/* Top-K */}
          <div className="cls-topk">
            <h4>Top-5 类别概率 · TOP-K PROBABILITIES</h4>
            <TopK rk="01" cls="politics" name="时政" v={99.4} pick />
            <TopK rk="02" cls="finance" name="财经" v={0.4} />
            <TopK rk="03" cls="society" name="社会" v={0.2} />
            <TopK rk="04" cls="tech" name="科技" v={0.05} />
            <TopK rk="05" cls="sports" name="体育" v={0.02} />
          </div>

          {/* Meta panel */}
          <div className="cls-meta-panel">
            <div className="mp"><small>模型</small><b>BERT-CNN</b><span className="mono">12-layer / 110M</span></div>
            <div className="mp"><small>耗时</small><b>78ms</b><span className="mono">prep 8 / inf 62 / post 8</span></div>
            <div className="mp"><small>版本</small><b>v2.1.0</b><span className="mono">2026.04.12 trained</span></div>
          </div>
        </div>
      </div>

      {/* Bottom: model picker + recent runs */}
      <div className="cls-bottom">
        <div className="cls-models">
          <h3><span className="num">2</span>选择分析模型</h3>
          <div className="model-grid">
            <Mod name="BERT" badge="基线" badgeCls="t-bert" desc="准确率最高,适合关键文本" selected />
            <Mod name="BERT-CNN" badge="推荐" badgeCls="t-bert" desc="融合 CNN,捕捉短语特征" />
            <Mod name="BERT-TextRNN" badge="长文本" badgeCls="t-bert" desc="融合 RNN,长依赖建模" />
            <Mod name="TextCNN" badge="高速" badgeCls="t-fast" desc="毫秒级响应,适合批量" />
            <Mod name="TextRNN" badge="高速" badgeCls="t-fast" desc="轻量,日常文本足够" />
            <Mod name="FastText" badge="极速" badgeCls="t-fast" desc="本地实例,无需下载" />
          </div>
        </div>

        <div className="cls-recent">
          <h3>最近分析 <span className="more">查看全部 →</span></h3>
          <div className="recent-grid">
            <Recent cls="" cat="科技" txt="新一代国产 AI 芯片正式量产,集成超过 200 亿晶体管,能效比领先国际同类产品..." time="14:25" conf={99.2} model="BERT-CNN" />
            <Recent cls="fn" cat="财经" txt="美联储维持利率不变,人民币兑美元汇率短线走强,北向资金净流入..." time="13:48" conf={98.7} model="BERT" />
            <Recent cls="sp" cat="体育" txt="男篮 95-88 战胜对手提前锁定下届世界杯入场券,主力前锋 28 分 12 篮板..." time="12:18" conf={99.8} model="BERT-CNN" />
            <Recent cls="et" cat="娱乐" txt="国产史诗大片今日全球公映,首日票房破 1.2 亿美元,创年度开画纪录..." time="11:02" conf={97.4} model="TextCNN" />
          </div>
        </div>
      </div>
    </div>
  </div>
);

const TopK = ({ rk, cls, name, v, pick }) => (
  <div className={`topk-row ${cls}${pick ? ' is-pick' : ''}`}>
    <span className="rk">{rk}</span>
    <span className="name">{name}</span>
    <span className="bar"><i style={{width: `${v}%`}}></i></span>
    <span className="val">{v.toFixed(v < 1 ? 2 : 1)}%</span>
  </div>
);

const Mod = ({ name, badge, badgeCls, desc, selected }) => (
  <div className={`model-card${selected ? ' is-selected' : ''}`}>
    <div className="row1">
      <span className="nm">{name}</span>
      <span className={`badge ${badgeCls}`}>{badge}</span>
    </div>
    <div className="desc">{desc}</div>
  </div>
);

const Recent = ({ cls, cat, txt, time, conf, model }) => (
  <div className={`recent-row ${cls}`}>
    <div className="cat-cell">
      <b>{cat}</b>
      <small>{time} · {model}</small>
    </div>
    <div className="txt">"{txt}"</div>
    <div className="conf">
      <b>{conf}%</b>
      <div className="mini-bar"><i style={{width: `${conf}%`}}></i></div>
    </div>
  </div>
);

Object.assign(window, { ClassifyMock });
