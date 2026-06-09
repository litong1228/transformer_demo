/* global React, SiteHeader, SubStrip, IconBookmark, IconShare, IconCheck */

const DetailMock = () => (
  <div className="det">
    <SiteHeader />
    <SubStrip active="时政" />
    <div className="det-progress"></div>

    <div className="det-wrap">
      <article className="det-article">
        <div className="det-rail">
          <div className="item">分享<IconShare /></div>
          <div className="item">收藏<IconBookmark /></div>
          <div className="item"><b>A</b>字号</div>
          <div className="item"><b>412</b>评论</div>
        </div>

        <div className="det-meta">
          <span className="cat-chip politics">时政 · POLITICS</span>
          <span className="tag-red-out">头条</span>
          <span className="pub">2026.05.18 · 14:32 · 新华社 · 张文 报道</span>
          <span className="pub" style={{color: 'var(--ink-3)'}}>阅读 5 分钟</span>
        </div>

        <h1 className="det-title">国务院召开常务会议,部署优化营商环境十项新举措,中小微企业融资成本将进一步下降</h1>

        <p className="det-lead">
          会议听取关于推进高质量发展和促进民营经济发展的工作汇报,部署进一步优化营商环境、降低企业融资成本的具体措施,要求各项惠企政策真正落到实处。
        </p>

        <div className="det-byline">
          <div className="avatar">张</div>
          <div className="who">
            <b>张文</b>
            新华社记者 · 北京报道
          </div>
          <div className="actions">
            <button className="det-act"><IconShare />分享</button>
            <button className="det-act is-on"><IconCheck />已关注</button>
            <button className="det-act"><IconBookmark />收藏</button>
          </div>
        </div>

        <div className="det-ai-banner">
          <div className="ai-icon">AI</div>
          <div className="ai-text">
            <b>智能分类: 时政</b>
            BERT-CNN v2.1 在 78ms 内完成全文分类 ·
            <small>另判别为 时政 (99.4%) · 财经 (0.4%) · 社会 (0.2%) ,
              可在右侧栏运行其他模型进行交叉验证</small>
          </div>
          <div className="ai-conf">
            <b>99.4%</b>
            CONFIDENCE
          </div>
        </div>

        <div className="det-hero-img ph is-photo-red" data-label="hero photo"></div>
        <div className="det-img-cap">国务院常务会议现场。会议重点讨论优化营商环境与降低企业融资成本两项议题。/ 新华社记者 摄</div>

        <div className="det-content">
          <p className="has-drop">
            国务院今日下午召开常务会议,听取关于推进高质量发展和促进民营经济发展的工作汇报,部署进一步优化营商环境、降低中小微企业融资成本的具体措施。会议强调,要把各项惠企政策真正落到实处,确保政策红利能够直达基层、直达企业。
          </p>
          <p>
            会议指出,过去一年中小微企业平均融资成本同比下降 0.4 个百分点,但部分领域仍然存在融资难、融资贵的情况。下一步将通过定向降准、再贷款额度扩大、政策性银行专项支持等多种工具,进一步压降融资成本。
          </p>

          <div className="det-pullquote">
            要把惠企政策真正落到实处,让中小微企业切实感受到政策红利,而不是停留在文件里。
          </div>

          <p>
            会议还研究部署了高标准建设国家技术创新中心、加快培育新质生产力等议题,提出要支持企业牵头组建创新联合体,推动产学研深度融合,在人工智能、生物医药、新能源等关键领域形成一批可复制、可推广的创新成果。
          </p>
          <p>
            此外,会议听取了关于推进新型城镇化建设的工作汇报,要求加快农业转移人口市民化,推动公共服务均等化,完善城市更新和保障性住房建设的政策框架,让发展成果更多更公平地惠及全体人民。
          </p>
        </div>
      </article>

      <div className="det-related">
        <h4>相关阅读 · RELATED COVERAGE</h4>
        <div className="det-related-grid">
          <div className="det-rel">
            <div className="ph is-photo-warm" data-label="img"></div>
            <div>
              <h5>财政部:今年新增专项债额度同比增长 14%,重点支持基建</h5>
              <div className="met">财经 · 2 小时前 · 1.2k reads</div>
            </div>
          </div>
          <div className="det-rel">
            <div className="ph is-photo" data-label="img"></div>
            <div>
              <h5>央行:四季度将持续推动综合融资成本稳中有降</h5>
              <div className="met">财经 · 4 小时前 · 894 reads</div>
            </div>
          </div>
          <div className="det-rel">
            <div className="ph is-photo-green" data-label="img"></div>
            <div>
              <h5>国务院国资委:深化国企改革三年行动收官在即</h5>
              <div className="met">时政 · 昨天 · 2.4k reads</div>
            </div>
          </div>
          <div className="det-rel">
            <div className="ph is-photo-blue" data-label="img"></div>
            <div>
              <h5>解读: 新一轮营商环境改革,有哪些具体看点?</h5>
              <div className="met">深度 · 昨天 · 3.1k reads</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

Object.assign(window, { DetailMock });
