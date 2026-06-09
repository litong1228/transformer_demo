/* global React, SiteHeader, SubStrip, IconList, IconGrid, IconChev, IconBookmark, IconSparkle */

const ListMock = () => (
  <div className="list">
    <SiteHeader />
    <SubStrip active="科技" />

    <div className="list-body">
      <div className="list-page-head">
        <div>
          <div className="crumb">环球新闻 / <b>科技</b></div>
          <h1>科技<span className="count">/ 共 1,284 篇报道 · 今日 28 篇新增</span></h1>
        </div>
        <div className="ctrl">
          <div className="sort">最新发布 <IconChev /></div>
          <div className="toggle">
            <button className="is-on"><IconList /></button>
            <button><IconGrid /></button>
          </div>
        </div>
      </div>

      <div className="list-cats">
        <a className="list-cat is-active">全部<span className="n">1284</span></a>
        <a className="list-cat">人工智能<span className="n">312</span></a>
        <a className="list-cat">半导体<span className="n">248</span></a>
        <a className="list-cat">互联网<span className="n">198</span></a>
        <a className="list-cat">新能源<span className="n">156</span></a>
        <a className="list-cat">航天航空<span className="n">94</span></a>
        <a className="list-cat">量子计算<span className="n">62</span></a>
        <a className="list-cat">生物科技<span className="n">58</span></a>
      </div>

      <div className="list-items">
        <Row n="01" featured img="is-photo-blue"
          cat="tech" catName="科技"
          ttl="新一代国产 AI 芯片正式量产,集成超过 200 亿晶体管"
          sum="据新华社报道,我国科研团队最新研发出新一代人工智能芯片,性能较上一代提升约 60%,能效比领先国际同类产品。该芯片采用先进的 7 纳米工艺。"
          time="14:25" reads="5,128" comments="89" ai="99.2%" />
        <Row n="02" img="is-photo"
          cat="tech" catName="人工智能"
          ttl="国产大模型开源生态白皮书发布,周下载量首次突破百万"
          sum="多家国内厂商联合发布开源大语言模型生态白皮书,公布最新评测结果及未来路线图,生态参与企业数量较去年同期翻倍。"
          time="13:42" reads="3,612" comments="124" ai="97.4%" />
        <Row n="03" img="is-photo-warm"
          cat="finance" catName="新能源"
          ttl="新能源汽车销量连续 11 个月同比增长,渗透率突破 45% 创历史新高"
          sum="中国汽车工业协会发布最新数据,新能源汽车市场渗透率持续走高,出口量也创下历史新高,海外市场拓展显著加速。"
          time="12:18" reads="2,789" comments="67" ai="98.1%" />
        <Row n="04" img="is-photo-green"
          cat="tech" catName="量子计算"
          ttl="北航团队量子计算论文登《Nature》,验证 76 量子比特优越性"
          sum="北京航空航天大学量子信息团队最新研究成果证明,量子计算在特定问题上的运算能力已经突破经典极限,引发国际关注。"
          time="11:05" reads="4,201" comments="158" ai="99.6%" />
        <Row n="05" img="is-photo-red"
          cat="tech" catName="半导体"
          ttl="存储芯片国产化率突破 35%,三大厂商联合推出新一代 DDR5 产品"
          sum="国内主要存储芯片厂商联合发布会上展示了基于全国产工艺的新一代 DDR5 内存产品,性能与国际主流产品看齐。"
          time="10:38" reads="1,932" comments="42" ai="96.8%" />
      </div>
    </div>

    <aside className="list-side">
      <div className="side-mod is-ai">
        <div className="side-mod-head">
          <h4>智能分类助手</h4>
          <span className="tag">BERT-CNN</span>
        </div>
        <p className="desc">把一段你想分类的中文文本贴进来,我用 BERT 给你定位到 10 个领域之一。</p>
        <div className="mini-input">"国务院今日召开常务会议,听取关于推进高质量发展和促进民营经济发展的工作汇报..."</div>
        <div className="ai-result">
          <div>
            <small style={{display: 'block', fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4}}>分类结果</small>
            <b>时政</b>
          </div>
          <span className="conf">置信 99.4% · 78ms</span>
        </div>
      </div>

      <div className="side-mod">
        <div className="side-mod-head">
          <h4>热门追踪</h4>
          <span className="tag">TRENDING</span>
        </div>
        <div className="trend-list">
          <div className="trend-item">
            <div className="rk">01</div>
            <div>
              <div className="ti">国产 AI 芯片量产突破</div>
              <div className="tm">科技 · 5,128 reads · 持续上升</div>
            </div>
          </div>
          <div className="trend-item">
            <div className="rk">02</div>
            <div>
              <div className="ti">量子计算论文登《Nature》</div>
              <div className="tm">科技 · 4,201 reads</div>
            </div>
          </div>
          <div className="trend-item">
            <div className="rk">03</div>
            <div>
              <div className="ti">大模型开源生态白皮书</div>
              <div className="tm">科技 · 3,612 reads</div>
            </div>
          </div>
          <div className="trend-item">
            <div className="rk">04</div>
            <div>
              <div className="ti">新能源车渗透率破 45%</div>
              <div className="tm">科技 · 2,789 reads</div>
            </div>
          </div>
        </div>
      </div>

      <div className="side-mod">
        <div className="side-mod-head">
          <h4>跳转栏目</h4>
          <span className="tag">JUMP</span>
        </div>
        <div className="cat-btns">
          <span className="cb">科技</span>
          <span className="cb s">体育</span>
          <span className="cb f">财经</span>
          <span className="cb e">娱乐</span>
          <span className="cb p">时政</span>
          <span className="cb h">健康</span>
          <span className="cb ed">教育</span>
          <span className="cb so">社会</span>
          <span className="cb g">游戏</span>
          <span className="cb pr">房产</span>
        </div>
      </div>
    </aside>
  </div>
);

const Row = ({ n, featured, img, cat, catName, ttl, sum, time, reads, comments, ai }) => (
  <div className={`list-row${featured ? ' is-featured' : ''}`}>
    <div className="idx">{n}</div>
    <div className={`ph ${img}`} data-label="photo"></div>
    <div>
      <div className="meta">
        <span className={`cat-chip ${cat}`}>{catName}</span>
        <span style={{fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-4)'}}>{time}</span>
        {featured && <span className="tag-red-out">头条</span>}
      </div>
      <h3>{ttl}</h3>
      <p>{sum}</p>
      <div className="row-foot">
        <span>{reads} reads</span>
        <span>{comments} comments</span>
        <span className="ai-mini">BERT-CNN · {ai}</span>
      </div>
    </div>
    <span className="bookmark"><IconBookmark /></span>
  </div>
);

Object.assign(window, { ListMock });
