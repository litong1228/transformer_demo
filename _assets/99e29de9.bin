/* global React */

/* Eye icon for password */
const IconEye = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
  </svg>
);
const IconUser = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
  </svg>
);
const IconLock = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);
const IconMail = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
  </svg>
);

/* ============ V1 LOGIN ============ */
const V1LoginMock = () => (
  <div className="auth">
    {/* LEFT: form */}
    <section className="auth-form-side">
      <a className="auth-back">返回首页</a>

      <div className="auth-mast">
        <div className="mark">环</div>
        <div className="name">
          <b>环球新闻</b>
          <small>HUANQIU · BERT</small>
        </div>
        <div className="issue">
          <b>第 1,247 期</b>
          2026.05.18
        </div>
      </div>

      <div className="auth-title-block">
        <div className="auth-eb">欢迎回来 · WELCOME BACK</div>
        <h1 className="auth-title">登录账号</h1>
        <p className="auth-lead">进入你的智能阅读空间, 继续我们尚未读完的故事。</p>
      </div>

      <form className="auth-form">
        <div className="auth-field">
          <label>账号 / Username</label>
          <div className="auth-input">
            <IconUser />
            <input placeholder="请输入账号或邮箱" defaultValue="zhang.wen" />
          </div>
        </div>

        <div className="auth-field">
          <label>密码 / Password</label>
          <div className="auth-input">
            <IconLock />
            <input type="password" placeholder="请输入密码" defaultValue="••••••••••••" />
            <span className="pwd-toggle"><IconEye /></span>
          </div>
        </div>

        <div className="auth-remember">
          <label className="is-on">
            <span className="box"></span>记住我 7 天
          </label>
          <span className="forgot"><a>忘记密码?</a></span>
        </div>

        <div className="auth-submit">
          <button type="submit" className="auth-submit-btn">登 录</button>
          <span className="alt">还没有账号? <a>立即注册</a></span>
        </div>
      </form>

      <div className="auth-foot">
        <div className="models">
          <small>POWERED BY</small>
          <span className="tag">BERT</span>
          <span className="tag">BERT-CNN</span>
          <span className="tag">BERT-RNN</span>
          <span className="tag">TextCNN</span>
          <span className="tag">FastText</span>
        </div>
        <div className="copy">© 2026 环球新闻 · 京 ICP 备 00000000</div>
      </div>
    </section>

    {/* RIGHT: brand panel */}
    <aside className="auth-brand-side">
      <div className="auth-brand-top">
        <div className="auth-brand-eb">EDITORIAL × INTELLIGENCE</div>
        <h2 className="auth-brand-quote">
          每一条新闻, 都先被 <span className="em">编辑</span> 与 <span className="em">智能</span> 共同审阅。
        </h2>
        <div className="auth-brand-byline">主编手记 · 环球新闻</div>
      </div>

      <div style={{position: 'relative', zIndex: 1}}>
        <div className="auth-paper">
          <div className="auth-paper-mast">
            <span>VOL. 1247</span>
            <b>HUANQIU</b>
            <span>05.18.2026</span>
          </div>
          <div className="auth-paper-eb">头版头条 · LEAD STORY</div>
          <h3 className="auth-paper-h">国务院召开常务会议, 部署优化营商环境十项新举措</h3>
          <p className="auth-paper-body">会议听取关于推进高质量发展和促进民营经济发展的工作汇报, 部署进一步优化营商环境、降低中小微企业融资成本的具体措施。</p>
          <div className="auth-paper-ai">
            <span>新华社 · 张文 · 14:32</span>
            <span className="conf">AI 时政 · 99.4%</span>
          </div>
        </div>

        {/* Floating category bubbles */}
        <div className="auth-floats">
          <span className="auth-float sp" style={{top: '-20px', right: '40px'}}>体育</span>
          <span className="auth-float fn" style={{top: '60px', right: '-12px'}}>财经</span>
          <span className="auth-float et" style={{bottom: '60px', left: '-12px'}}>娱乐</span>
          <span className="auth-float po" style={{bottom: '-12px', right: '80px'}}>时政 · 头条</span>
        </div>
      </div>

      <div className="auth-brand-stats">
        <div className="st"><b>94.7%</b><small>BERT 准确率</small></div>
        <div className="st"><b>86ms</b><small>平均耗时</small></div>
        <div className="st"><b>12,408</b><small>今日分类</small></div>
      </div>
    </aside>
  </div>
);

/* ============ V1 REGISTER ============ */
const V1RegisterMock = () => (
  <div className="auth">
    <section className="auth-form-side">
      <a className="auth-back">返回登录</a>

      <div className="auth-mast">
        <div className="mark">环</div>
        <div className="name">
          <b>环球新闻</b>
          <small>HUANQIU · BERT</small>
        </div>
        <div className="issue">
          <b>第 1,247 期</b>
          2026.05.18
        </div>
      </div>

      <div className="auth-title-block">
        <div className="auth-eb">加入我们 · JOIN HUANQIU</div>
        <h1 className="auth-title">注册新账号</h1>
        <p className="auth-lead">建立你的智能阅读档案, 让分类系统记住你关心什么。</p>
      </div>

      <form className="auth-form">
        <div className="auth-field">
          <label>用户名 / Username</label>
          <div className="auth-input">
            <IconUser />
            <input placeholder="选一个独特的用户名" defaultValue="li.wenhua" />
          </div>
        </div>

        <div className="auth-field">
          <label>邮箱 / Email</label>
          <div className="auth-input">
            <IconMail />
            <input placeholder="例如 you@example.com" defaultValue="li.wenhua@example.com" />
          </div>
        </div>

        <div className="auth-field">
          <label>密码 / Password</label>
          <div className="auth-input">
            <IconLock />
            <input type="password" placeholder="至少 8 位, 含字母与数字" defaultValue="••••••••••••••" />
            <span className="pwd-toggle"><IconEye /></span>
          </div>
          <div className="auth-strength is-3">
            <div className="meter"><i></i><i></i><i></i><i></i></div>
            <div className="hint">
              <span>密码强度</span>
              <b>较强 · GOOD</b>
            </div>
          </div>
        </div>

        <div className="auth-field">
          <label>确认密码 / Confirm</label>
          <div className="auth-input">
            <IconLock />
            <input type="password" placeholder="再次输入密码" defaultValue="••••••••••••••" />
            <span className="pwd-toggle"><IconEye /></span>
          </div>
        </div>

        <div className="auth-remember">
          <label className="is-on">
            <span className="box"></span>
            <span>我已阅读并同意 <a style={{color: 'var(--red)', borderBottom: '1px solid var(--red)'}}>服务条款</a> 与 <a style={{color: 'var(--red)', borderBottom: '1px solid var(--red)'}}>隐私政策</a></span>
          </label>
        </div>

        <div className="auth-submit">
          <button type="submit" className="auth-submit-btn">注 册</button>
          <span className="alt">已有账号? <a>立即登录</a></span>
        </div>
      </form>

      <div className="auth-foot">
        <div className="models">
          <small>POWERED BY</small>
          <span className="tag">BERT</span>
          <span className="tag">BERT-CNN</span>
          <span className="tag">BERT-RNN</span>
          <span className="tag">TextCNN</span>
          <span className="tag">FastText</span>
        </div>
        <div className="copy">© 2026 环球新闻 · 京 ICP 备 00000000</div>
      </div>
    </section>

    <aside className="auth-brand-side">
      <div className="auth-brand-top">
        <div className="auth-brand-eb">EDITORIAL × INTELLIGENCE</div>
        <h2 className="auth-brand-quote">
          注册即开启一份 <span className="em">专属</span> 的智能阅读简报。
        </h2>
        <div className="auth-brand-byline">主编手记 · 环球新闻</div>
      </div>

      <div style={{position: 'relative', zIndex: 1}}>
        <div className="auth-paper">
          <div className="auth-paper-mast">
            <span>FOR YOU</span>
            <b>简报 BRIEF</b>
            <span>每日 06:00</span>
          </div>
          <div className="auth-paper-eb">个性化推荐 · CURATED</div>
          <h3 className="auth-paper-h">基于你过去 7 天的阅读, 我为你挑了这 5 条</h3>
          <p className="auth-paper-body">智能分类系统会根据你的阅读偏好, 每日早晨自动整理一份「为你定制」的简报, 仅推送你最关心的领域。</p>
          <div className="auth-paper-ai">
            <span>智能编辑 · BERT-CNN</span>
            <span className="conf">个性化 · 92.1%</span>
          </div>
        </div>

        <div className="auth-floats">
          <span className="auth-float" style={{top: '-20px', right: '40px'}}>科技</span>
          <span className="auth-float fn" style={{top: '60px', right: '-12px'}}>财经 · 推荐</span>
          <span className="auth-float et" style={{bottom: '60px', left: '-12px'}}>娱乐</span>
          <span className="auth-float so" style={{bottom: '-12px', right: '80px'}}>社会</span>
        </div>
      </div>

      <div className="auth-brand-stats">
        <div className="st"><b>10</b><small>支持类别</small></div>
        <div className="st"><b>5</b><small>可用模型</small></div>
        <div className="st"><b>86k+</b><small>注册用户</small></div>
      </div>
    </aside>
  </div>
);

Object.assign(window, { V1LoginMock, V1RegisterMock });
