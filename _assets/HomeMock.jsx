/* global React, SiteHeader, SubStrip, IconArrow, IconSparkle */

const HomeMock = () => (
  <div className="home">
    <SiteHeader />
    <SubStrip active="首页" />

    <div className="home-body">
      {/* Masthead kicker */}
      <div className="home-kicker">
        <div className="issue">
          <b>第 1,247 期</b>
          MON-FRI · 24 HR UPDATES
        </div>
        <div className="weather">
          北京 <b>21°</b> 多云转晴 · 空气优 · 黄历: 宜读书
        </div>
        <div className="reads-num">
          今日访问<b>284,512</b>
        </div>
        <div className="ai-status">
          <b>BERT-CNN v2.1 ONLINE</b>
          AVG 86ms · 12,408 CLASSIFIED TODAY
        </div>
      </div>

      {/* Hero — lead + ranked side */}
      <div className="home-hero">
        <div className="home-hero-lead">
          <div className="eyebrow">
            头版头条 · LEAD STORY
            <span className="ai-chip"><span className="dot"></span>AI 分类: 时政 · 99.4%</span>
          </div>
          <h1>国务院召开常务会议,部署优化营商环境十项新举措</h1>
          <p className="lead">
            <span className="lead-drop">国</span>务院今日下午召开常务会议,听取关于推进高质量发展和促进民营经济发展的工作汇报,部署进一步优化营商环境、降低中小微企业融资成本的十项具体措施。会议强调要把惠企政策真正落到实处。
          </p>
          <div className="ph is-photo-red" data-label="hero photo"></div>
          <div className="byline">
            <span>新华社 · 张文 报道 · 2026.05.18 14:32</span>
            <span className="reads">12,847 reads · 412 comments</span>
          </div>
        </div>

        <div className="home-hero-side">
          <div className="side-title">
            正在发生 · LIVE
            <span className="live">3 LIVE</span>
          </div>
          <div className="side-item is-top">
            <div className="num">01</div>
            <div>
              <div className="ttl">沪指收涨 1.32% 报 3,340 点,北向资金净流入 80 亿</div>
              <div className="met"><span className="cat-chip finance">财经</span><span>14:30</span><span>8.4k</span></div>
            </div>
          </div>
          <div className="side-item">
            <div className="num">02</div>
            <div>
              <div className="ttl">国产 AI 芯片量产突破,性能较上一代提升 60%</div>
              <div className="met"><span className="cat-chip tech">科技</span><span>13:55</span><span>5.2k</span></div>
            </div>
          </div>
          <div className="side-item">
            <div className="num">03</div>
            <div>
              <div className="ttl">男篮 95-88 战胜对手提前锁定世界杯门票</div>
              <div className="met"><span className="cat-chip sports">体育</span><span>12:18</span><span>4.7k</span></div>
            </div>
          </div>
          <div className="side-item">
            <div className="num">04</div>
            <div>
              <div className="ttl">国产史诗大片首日全球票房破 1.2 亿美元</div>
              <div className="met"><span className="cat-chip ent">娱乐</span><span>11:02</span><span>3.1k</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* AI feature row */}
      <div className="home-ai-row">
        <div className="home-ai-card">
          <div className="ai-eyebrow"><span className="dot"></span>POWERED BY BERT</div>
          <h3>把任何中文文本,在 86ms 内分类到 10 个新闻领域</h3>
          <p>支持 BERT、BERT-CNN、BERT-TextRNN、TextCNN、TextRNN 五种模型,
            可对比、可批量、可追溯。</p>
          <div className="stats">
            <div><b>94.7%</b><small>BERT 准确率</small></div>
            <div><b>86ms</b><small>平均耗时</small></div>
            <div><b>5</b><small>可用模型</small></div>
          </div>
          <div className="cta">立即体验智能分类 <IconArrow /></div>
        </div>

        <div className="home-stat-card">
          <div className="eb">今日类别分布</div>
          <h4>哪些主题在被阅读?</h4>
          <div>
            <BreakRow cls="tech" lbl="科技" v={28} />
            <BreakRow cls="finance" lbl="财经" v={22} />
            <BreakRow cls="politics" lbl="时政" v={18} />
            <BreakRow cls="sports" lbl="体育" v={14} />
            <BreakRow cls="ent" lbl="娱乐" v={10} />
            <BreakRow cls="society" lbl="社会" v={8} />
          </div>
        </div>

        <div className="home-stat-card">
          <div className="eb">为你推荐</div>
          <h4>基于你的阅读偏好</h4>
          <div style={{display: 'flex', flexDirection: 'column', gap: 14, marginTop: 4}}>
            <RecRow cls="tech" ttl="量子计算新突破,北航团队论文登《Nature》" met="20 min · 推荐 92%" />
            <RecRow cls="finance" ttl="A 股市值十大公司排行新洗牌" met="1h · 推荐 87%" />
            <RecRow cls="edu" ttl="高考改革新方案:外语将不再统考?" met="2h · 推荐 81%" />
          </div>
        </div>
      </div>

      {/* Latest news */}
      <div className="home-section">
        <div className="home-section-head">
          <h2>最新新闻</h2>
          <span className="rule"></span>
          <span className="more">查看全部 NEWS</span>
        </div>
        <div className="home-card-grid">
          <Card cat="tech" catName="科技" img="is-photo-blue"
            ttl="新一代国产 AI 芯片正式量产,集成 200 亿晶体管"
            sum="据新华社报道,我国科研团队最新研发的人工智能芯片性能较上一代提升约 60%,能效比领先国际同类产品。"
            time="14:25" reads="2,847" ai="99.2%" />
          <Card cat="finance" catName="财经" img="is-photo-warm"
            ttl="美联储维持利率不变,人民币汇率短线走强"
            sum="联邦公开市场委员会今晨结束议息会议,决定维持当前联邦基金目标利率区间不变,人民币兑美元中间价上调。"
            time="13:48" reads="1,932" ai="98.7%" />
          <Card cat="sports" catName="体育" img="is-photo-green"
            ttl="国家队大胜对手,提前一轮锁定下届世界杯入场券"
            sum="比赛中主力前锋全场拿下 28 分 12 篮板,多次在关键时刻命中三分球,赛后被评为全场 MVP。"
            time="12:18" reads="3,421" ai="99.8%" />
        </div>
      </div>

      {/* Featured section */}
      <div className="home-section">
        <div className="home-section-head">
          <h2>科技专区</h2>
          <span className="rule"></span>
          <span className="more">订阅栏目 SUBSCRIBE</span>
        </div>
        <div className="home-card-grid">
          <Card cat="tech" catName="科技" img="is-photo-blue"
            ttl="北航团队量子计算论文登《Nature》,验证量子优越性"
            sum="北京航空航天大学量子信息团队最新研究成果证明,量子计算在特定问题上的运算能力已经突破经典极限。"
            time="今天" reads="5,128" ai="99.6%" />
          <Card cat="tech" catName="科技" img="is-photo"
            ttl="国产大模型开源生态进一步完善,周下载量破百万"
            sum="多家国内厂商联合发布开源大语言模型生态白皮书,公布最新评测结果及未来路线图。"
            time="昨天" reads="3,612" ai="97.4%" />
          <Card cat="tech" catName="科技" img="is-photo-warm"
            ttl="新能源汽车销量连续 11 个月同比增长,渗透率突破 45%"
            sum="中国汽车工业协会发布最新数据,新能源汽车市场渗透率持续走高,出口量也创下历史新高。"
            time="昨天" reads="2,789" ai="98.1%" />
        </div>
      </div>
    </div>
  </div>
);

const BreakRow = ({ cls, lbl, v }) => (
  <div className={`breakdown-row ${cls}`}>
    <span className="lbl">{lbl}</span>
    <span className="bar"><i style={{width: `${v * 3}%`}}></i></span>
    <span className="num">{v}%</span>
  </div>
);

const RecRow = ({ cls, ttl, met }) => (
  <div style={{display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 10, alignItems: 'baseline', paddingBottom: 12, borderBottom: '1px dotted var(--border-2)'}}>
    <span className={`cat-chip ${cls}`} style={{width: 'auto'}}></span>
    <div>
      <div style={{fontFamily: 'var(--serif)', fontWeight: 600, fontSize: 13.5, color: 'var(--ink)', lineHeight: 1.4, marginBottom: 4}}>{ttl}</div>
      <div style={{fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-4)', letterSpacing: '0.04em'}}>{met}</div>
    </div>
  </div>
);

const Card = ({ cat, catName, img, ttl, sum, time, reads, ai }) => (
  <div className="home-card">
    <div className={`ph ${img}`} data-label="photo"></div>
    <div className="meta">
      <span className={`cat-chip ${cat}`}>{catName}</span>
      <span style={{fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-4)'}}>{time}</span>
    </div>
    <h3>{ttl}</h3>
    <p>{sum}</p>
    <div className="footer">
      <span>{reads} reads</span>
      <span className="ai-mini">AI {ai}</span>
    </div>
  </div>
);

Object.assign(window, { HomeMock });
