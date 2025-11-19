const state={posts:[],filtered:[],activeIndex:-1}
const contentCache=new Map()
function renderMarkdown(md){
  md=groupBlockquotes(md)
  let html=md
  html=html.replace(/^\s*[-*_]{3,}\s*$/gm,'<hr>')
  html=html.replace(/^######\s?(.*)$/gm,'<h6>$1</h6>')
  html=html.replace(/^#####\s?(.*)$/gm,'<h5>$1</h5>')
  html=html.replace(/^####\s?(.*)$/gm,'<h4>$1</h4>')
  html=html.replace(/^###\s?(.*)$/gm,'<h3>$1</h3>')
  html=html.replace(/^##\s?(.*)$/gm,'<h2>$1</h2>')
  html=html.replace(/^#\s?(.*)$/gm,'<h1>$1</h1>')
  html=html.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
  html=html.replace(/\*(.*?)\*/g,'<em>$1</em>')
  html=html.replace(/`([^`]+)`/g,'<code>$1</code>')
  html=html.replace(/!\[(.*?)\]\((.*?)\)/g,(m,alt,url)=>`<img src="${rewriteImageUrl(url)}" alt="${alt}" loading="lazy" referrerpolicy="no-referrer">`)
  html=html.replace(/<img\s+[^>]*src="([^"]+)"[^>]*>/g,(m,url)=>m.replace(url,rewriteImageUrl(url)))
  html=html.replace(/\[(.*?)\]\((.*?)\)/g,'<a href="$2" target="_blank" rel="noopener">$1<\/a>')
  html=html.split(/\n\n+/).map(p=>{
    if(/^<h\d>/.test(p))return p
    if(p.startsWith('<blockquote>'))return p
    if(p.startsWith('```')&&p.endsWith('```')){
      const c=p.slice(3,-3)
      return `<pre><code>${escapeHtml(c)}</code></pre>`
    }
    return `<p>${p}</p>`
  }).join('')
  return html
}
function escapeHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function rewriteImageUrl(url){
  try{
    const u=new URL(url,location.href)
    const h=u.hostname||''
    if(h.includes('mmbiz.qpic.cn')||h.includes('wx.qlogo.cn')||h.includes('mp.weixin.qq.com')){
      return 'https://m.wbiao.cn/mallapi/wechat/picReverseUrl?url='+encodeURIComponent(url)
    }
    return url
  }catch(e){return url}
}
function groupBlockquotes(md){
  const lines=md.split('\n')
  let out=[]
  for(let i=0;i<lines.length;i++){
    const m=lines[i].match(/^\s*>\s?(.*)$/)
    if(m){
      let buf=[]
      while(i<lines.length){
        const mm=lines[i].match(/^\s*>\s?(.*)$/)
        if(!mm)break
        const t=(mm[1]||'').trim()
        if(t.length>0) buf.push(t)
        i++
      }
      i--
      if(buf.length>0){
        out.push(`<blockquote>${buf.join('<br>')}</blockquote>`)
      }
    }else{
      out.push(lines[i])
    }
  }
  return out.join('\n')
}
function renderList(){
  const ul=document.getElementById('list')
  ul.innerHTML=''
  state.filtered.forEach((p,i)=>{
    const li=document.createElement('li')
    const t=document.createElement('span')
    t.className='title'
    t.textContent=p.title
    const d=document.createElement('span')
    d.className='date'
    d.textContent=p.date
    li.appendChild(t)
    li.appendChild(d)
    li.addEventListener('click',()=>openPost(i))
    ul.appendChild(li)
  })
  document.getElementById('count').textContent=`${state.filtered.length}`
}
function openPost(i){
  state.activeIndex=i
  const p=state.filtered[i]
  document.getElementById('article-title').textContent=p.title
  document.getElementById('article-date').textContent=p.date
  try{location.hash=encodeURIComponent(p.filename)}catch(e){}
  if(!isAuthorized()){
    document.getElementById('article-content').textContent='请先输入密码'
    showGate()
    return
  }
  fetchContent(p).then(md=>{
    document.getElementById('article-content').innerHTML=renderMarkdown(md)
    buildTOC()
    const reader=document.querySelector('.reader'); if(reader) reader.scrollTop=0
    window.scrollTo({top:0,behavior:'instant'})
  }).catch(()=>{
    document.getElementById('article-content').textContent='加载正文失败'
  })
}
function filterPosts(q){
  const v=q.trim().toLowerCase()
  if(!v){state.filtered=[...state.posts];renderList();return}
  let out=state.posts.filter(p=>p.title.toLowerCase().includes(v))
  state.filtered=out
  renderList()
  state.posts.forEach(p=>{
    getContent(p).then(md=>{
      if(md.toLowerCase().includes(v)){
        if(!state.filtered.includes(p)){
          state.filtered.push(p)
          renderList()
        }
      }
    }).catch(()=>{})
  })
}
function setup(){
  const input=document.getElementById('search')
  input.addEventListener('input',e=>filterPosts(e.target.value))
  const tocWrap=document.getElementById('toc-wrap')
  const tocToggle=document.getElementById('toc-toggle')
  if(tocWrap){
    let tocCloseTimer=null
    const open=()=>{if(tocCloseTimer){clearTimeout(tocCloseTimer);tocCloseTimer=null}tocWrap.classList.add('open')}
    const scheduleClose=()=>{if(tocCloseTimer){clearTimeout(tocCloseTimer)}tocCloseTimer=setTimeout(()=>{tocWrap.classList.remove('open')},400)}
    tocWrap.addEventListener('mouseenter',open)
    tocWrap.addEventListener('mouseleave',scheduleClose)
    tocToggle?.addEventListener('click',()=>tocWrap.classList.toggle('open'))
    // touch devices: tap toggles panel
    tocWrap.addEventListener('touchstart',open,{passive:true})
    document.addEventListener('click',e=>{if(!tocWrap.contains(e.target)) tocWrap.classList.remove('open')})
  }
  document.addEventListener('keydown',e=>{
    if(e.key==='ArrowDown'){if(state.activeIndex<state.filtered.length-1){openPost(state.activeIndex+1)}e.preventDefault()}
    if(e.key==='ArrowUp'){if(state.activeIndex>0){openPost(state.activeIndex-1)}e.preventDefault()}
    const k=(e.key||'').toLowerCase()
    if(k==='f12')e.preventDefault()
    if(e.ctrlKey&&e.shiftKey&&(k==='i'||k==='j'||k==='c'||k==='k'))e.preventDefault()
    if(e.ctrlKey&&k==='u')e.preventDefault()
    if(e.ctrlKey&&k==='c'&&!isEditable(e.target))e.preventDefault()
  })
  document.addEventListener('copy',e=>{e.preventDefault()})
  document.addEventListener('contextmenu',e=>{e.preventDefault()})
  document.addEventListener('selectstart',e=>{if(!isEditable(e.target))e.preventDefault()})
}
function isEditable(el){return el&&((el.isContentEditable)||['INPUT','TEXTAREA','SELECT'].includes(el.tagName))}
async function load(){
  try{
    const url=new URL('../data/posts.json',location.href).toString()
    const res=await fetch(url)
    const arr=await res.json()
    const sorted=arr.slice().sort((a,b)=>dateKey(b.title)-dateKey(a.title))
    sorted.forEach(p=>{const df=formatDateFromTitle(p.title);if(df)p.date=df})
    state.posts=sorted
    state.filtered=[...sorted]
    renderList()
    const hash=decodeURIComponent(location.hash.replace('#','')||'')
    const idx=hash?state.filtered.findIndex(p=>p.filename===hash):-1
    if(idx>=0)openPost(idx); else if(state.filtered.length>0)openPost(0)
  }catch(e){
    const t=document.getElementById('article-title')
    const c=document.getElementById('article-content')
    t.textContent='数据加载失败'
    c.textContent='未能读取 posts.json，请确认服务器运行与路径正确。'
  }
}
function dateKey(title){
  const m8=title.match(/^(\d{8})/)
  if(m8) return parseInt(m8[1])
  const m6=title.match(/^(\d{6})/)
  if(m6){
    const s=m6[1]
    let y='20'+s.slice(0,2)
    if(s.startsWith('23')) y='2023'
    else if(s.startsWith('24')) y='2024'
    const key=y+s.slice(2)
    return parseInt(key)
  }
  return 0
}
function formatDateFromTitle(title){
  const m8=title.match(/^(\d{8})/)
  if(m8){const s=m8[1];return `${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`}
  const m6=title.match(/^(\d{6})/)
  if(m6){const s=m6[1];let y='20'+s.slice(0,2);if(s.startsWith('23'))y='2023';else if(s.startsWith('24'))y='2024';return `${y}-${s.slice(2,4)}-${s.slice(4,6)}`}
  return null
}
async function fetchContent(p){
  const url=new URL('../files/'+encodeURIComponent(p.filename),location.href).toString()
  const res=await fetch(url)
  return await res.text()
}
async function getContent(p){
  if(contentCache.has(p.filename)) return contentCache.get(p.filename)
  const md=await fetchContent(p)
  contentCache.set(p.filename,md)
  return md
}
init()
function init(){
  setup()
  load()
}
function isAuthorized(){
  try{const s=localStorage.getItem('lr_auth_until');if(!s)return false;const t=parseInt(s);return Date.now()<t}catch(e){return false}
}
function authorize(){
  const days=7
  const until=Date.now()+days*24*60*60*1000
  localStorage.setItem('lr_auth_until',String(until))
}
function showGate(){
  const g=document.getElementById('gate')
  g.classList.remove('hidden')
  const input=document.getElementById('gate-input')
  const btn=document.getElementById('gate-btn')
  const msg=document.getElementById('gate-msg')
  const pass=(document.querySelector('meta[name="site-password"]')?.content||'')
  const submit=()=>{
    const v=(input.value||'').trim()
    if(v===pass){authorize();hideGate();load()}else{msg.textContent='密码错误，请查看专属群总链接（每月修改一次），和【懒人知识库】同一个密码'}
  }
  btn.addEventListener('click',submit)
  input.addEventListener('keydown',e=>{if(e.key==='Enter')submit()})
  input.focus()
}
function hideGate(){
  const g=document.getElementById('gate')
  g.classList.add('hidden')
}
function buildTOC(){
  const panel=document.getElementById('toc-panel')
  if(!panel) return
  panel.innerHTML=''
  const article=document.getElementById('article-content')
  const hs=article.querySelectorAll('h1,h2,h3')
  hs.forEach(h=>{
    const text=h.textContent||''
    const id=slug(text)
    h.id=id
    const a=document.createElement('a')
    a.textContent=text
    a.href='#'+id
    a.className='toc-item toc-'+h.tagName.toLowerCase()
    a.addEventListener('click',e=>{e.preventDefault();document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'})})
    panel.appendChild(a)
  })
}
function slug(s){return s.trim().toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g,'-').replace(/^-+|-+$/g,'')||('h'+Math.random().toString(36).slice(2))}