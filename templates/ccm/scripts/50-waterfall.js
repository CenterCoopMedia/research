  function initWaterfall(host) {
    const scope=host.attachShadow({mode:'open'});
    scope.appendChild(host.querySelector('template').content.cloneNode(true));
    let offset=0;
    const storyTop=()=>scope.getElementById('story').getBoundingClientRect().top+window.scrollY-offset;
    const fallbackMarkup=data=>'<h3>'+escapeHTML(data.title)+'</h3><p>'+escapeHTML(data.status)+'</p><table><thead><tr><th>Group</th><th>Value</th></tr></thead><tbody>'+data.groups.map(g=>'<tr><td>'+escapeHTML(g.label)+'</td><td>'+escapeHTML(g.value)+' '+escapeHTML(data.unit)+'</td></tr>').join('')+'</tbody></table><p>'+escapeHTML(data.source)+'</p><p>'+escapeHTML(data.caveat)+'</p>';

  /** A data-first unit-chart renderer. No libraries, network calls, or scroll hijacking. */
  const $ = id => scope.getElementById(id);
  const number = new Intl.NumberFormat('en-US',{maximumSignificantDigits:21});
  const clamp = (v, lo=0, hi=1) => Math.max(lo, Math.min(hi, v));
  const smoothstep = t => t*t*(3-2*t);
  const escapeHTML = text => String(text).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clone = object => JSON.parse(JSON.stringify(object));
  const defaultData = JSON.parse($('scale-data').textContent);
  const reachData = {
    version:1,title:'Program reach, in perspective',unit:'people',totalSquares:2500,
    status:'Fictional example · not a measured population',
    source:'Entirely invented figures for demonstrating the storytelling template. These are not results from a real program, organization, or community.',
    caveat:'The four example groups are mutually exclusive and total 50,000 people. Replace all figures and narration with your own validated data before publication. “Not yet reached” should only be used when the full target population is known.',
    summaryHeadline:'The audience you know\nis not the whole audience.',
    groups:[
      {id:'regular',label:'Regular participants',shortLabel:'Regular',value:420,color:'#ec3864',headline:'The people\nyou know best.',description:'The regulars: {value} {unit}. They are highly visible, but occupy only {tiles} squares in this fictional population.'},
      {id:'occasional',label:'Occasional participants',shortLabel:'Occasional',value:1680,color:'#e7bb27',headline:'A wider\ncircle.',description:'Add the occasional participants. The picture grows, but the people actively involved are still a small group.'},
      {id:'aware',label:'Reached, not participating',shortLabel:'Reached',value:7900,color:'#00b982',headline:'Awareness\nis not engagement.',description:'These people have been reached by the fictional program but do not participate. A different relationship, and a bigger band.'},
      {id:'unreached',label:'Not yet reached',shortLabel:'Not reached',value:40000,color:'#3e4740',headline:'Beyond\nthe usual circle.',description:'The largest group: people the fictional program has not yet reached. This is what a participant-only view would leave out.'}
    ]
  };
  const dom = {track:$('story'),stage:$('stage'),box:$('chart-box'),canvas:$('unit-chart'),marker:$('boundary-marker'),hint:$('chart-hint'),nav:$('chapter-nav'),dialog:$('editor')};
  const ctx = dom.canvas.getContext('2d');
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  let reduceMotion = motionQuery.matches;
  let config, groups=[], total=0, tiles=2500, columns=50, rows=50, unitValue=0;
  let timeline=[], totalUnits=0, viewHeight=window.innerHeight, currentIndex=-1;
  let size={width:0,height:0,left:0,top:0,grid:0,pitch:0,dot:0};
  let frame=0, scrollPending=false, geometryPending=false, currentState=null, lastTally=-1;
  let lastWidth=0, lastHeight=0, draft, draftBaseline, opener, toastTimer, scrollAnimation=null;
  const hash = n => { const t=Math.sin(n*127.1+311.7)*43758.5453; return t-Math.floor(t); };

  function compact(value, digits=1) {
    const a=Math.abs(value);
    for(const [base,suffix] of [[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']]) {
      if(a>=base) return (value/base).toFixed(digits).replace(/\.0+$/,'')+suffix;
    }
    if(a>0 && a<0.000001) return value.toExponential(digits);
    if(a>0 && a<1) return new Intl.NumberFormat('en-US',{maximumSignificantDigits:digits+1}).format(value);
    return number.format(Number(value.toFixed(digits)));
  }
  function words(value) {
    for(const [base,suffix] of [[1e12,'trillion'],[1e9,'billion'],[1e6,'million']]) {
      if(Math.abs(value)>=base) return (value/base).toFixed(2).replace(/\.?0+$/,'')+' '+suffix;
    }
    return number.format(value);
  }
  function percent(value) {
    if(value>0 && value<0.01) return '<0.01';
    return value.toFixed(value<1?2:1).replace(/\.0$/,'');
  }
  function contrastInk(hex) {
    // Darken category colors for small type on paper. The squares retain the data color.
    let rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16));
    const luminance = a => a.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
    while((.897+.05)/(luminance(rgb)+.05)<4.6 && Math.max(...rgb)>20) rgb=rgb.map(v=>Math.round(v*.91));
    return '#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join('');
  }
  function validate(data) {
    if(!data || typeof data!=='object' || Array.isArray(data)) throw Error('The JSON must contain one dataset object.');
    if(typeof data.title!=='string' || !data.title.trim()) throw Error('Give the story a title.');
    if(typeof data.unit!=='string' || !data.unit.trim()) throw Error('Add a plural unit label, such as people or households.');
    if(![1000,2500,5000].includes(Number(data.totalSquares))) throw Error('Choose 1,000, 2,500, or 5,000 squares.');
    if(!Array.isArray(data.groups) || data.groups.length<2 || data.groups.length>8) throw Error('Use between two and eight groups.');
    const used=new Set();
    data.groups.forEach((g,i)=>{
      if(!g || typeof g.label!=='string' || !g.label.trim()) throw Error(`Give group ${i+1} a name.`);
      if(typeof g.value!=='number' || !Number.isFinite(g.value) || g.value<0) throw Error(`“${g.label}” needs a finite, non-negative number.`);
      if(!/^#[0-9a-f]{6}$/i.test(g.color||'')) throw Error(`Choose a six-digit color for “${g.label}”.`);
      if(g.value>Number.MAX_SAFE_INTEGER) throw Error(`“${g.label}” exceeds JavaScript's safe numeric range.`);
      if(typeof g.id!=='string' || !g.id || used.has(g.id)) g.id='group-'+i;
      used.add(g.id);
      g.shortLabel=typeof g.shortLabel==='string'&&g.shortLabel.trim()?g.shortLabel:g.label;
      g.headline=typeof g.headline==='string'&&g.headline.trim()?g.headline:g.label;
      g.description=typeof g.description==='string'?g.description:'{value} {unit}, or {share} of the total. Each square has the same weight.';
    });
    const sum=data.groups.reduce((s,g)=>s+g.value,0);
    if(!(sum>0) || !Number.isFinite(sum) || sum>Number.MAX_SAFE_INTEGER) throw Error('The combined value must be positive and within JavaScript’s safe numeric range.');
    data.totalSquares=Number(data.totalSquares);
    for(const key of ['status','source','caveat','summaryHeadline']) data[key]=typeof data[key]==='string'?data[key]:'';
    data.status=data.status.trim()||'Custom data · check source notes';
    return data;
  }
  function allocate() {
    total=config.groups.reduce((s,g)=>s+g.value,0);
    tiles=config.totalSquares;
    columns=tiles===1000?40:tiles===5000?50:50;
    rows=Math.ceil(tiles/columns);
    unitValue=total/tiles;
    groups=config.groups.map((g,i)=>({...g,index:i,share:g.value/total*100,exact:g.value/total*tiles,ink:contrastInk(g.color)}));
    groups.forEach(g=>g.count=Math.floor(g.exact));
    // Hamilton / largest-remainder apportionment keeps every square the same size
    // and makes the integer allocations sum to exactly totalSquares.
    const spare=tiles-groups.reduce((s,g)=>s+g.count,0);
    [...groups].sort((a,b)=>(b.exact-b.count)-(a.exact-a.count)||a.index-b.index).slice(0,spare).forEach(g=>g.count++);
    let cursor=0;
    groups.forEach(g=>{g.start=cursor;cursor+=g.count;g.end=cursor;});
    // The first, small group is already in place. Each later group gets its own
    // fill and hold interval. Share controls filling time, never tile area.
    let start=0;
    timeline=groups.map((g,i)=>{
      const fill=i===0?0:.82+(g.count/tiles)*2.65;
      const hold=i===0?.88:.64;
      const segment={start,fillEnd:start+fill,end:start+fill+hold,fill,hold};
      start=segment.end;return segment;
    });
    totalUnits=start+.22;
  }
  function replaceTokens(text,g) {
    const substitutions={value:words(g.value),unit:config.unit,tiles:number.format(g.count),totalSquares:number.format(tiles),share:percent(g.share)+'%'};
    return text.replace(/\{(value|unit|tiles|totalSquares|share)\}/g,(_,key)=>substitutions[key]);
  }
  function buildInterface() {
    $('story-title').textContent=config.title;

    $('data-note').textContent=config.status;
    $('chart-heading').textContent=`One whole. ${number.format(tiles)} squares.`;
    $('chart-total').textContent=`~${compact(total)} ${config.unit}`;
    $('square-key-text').textContent=`1 square ≈ ${compact(unitValue)} ${config.unit}`;
    $('total-tally').textContent=number.format(tiles);
    $('chart-description').textContent=`${config.status}. A unit chart of ${number.format(tiles)} equal squares, representing ${number.format(total)} ${config.unit}. `+groups.map(g=>`${g.label}: ${number.format(g.value)} ${config.unit}, ${percent(g.share)} percent, approximately ${g.count} squares.`).join(' ')+` The categories appear in this order as you scroll. The full values are in the data table below.`;
    dom.nav.innerHTML='';
    dom.nav.classList.toggle('many',groups.length>4);
    $('preset-select').options[0].textContent=defaultData.title+' · embedded dataset';
    groups.forEach((g,i)=>{
      const button=document.createElement('button');
      button.className='chapter-button';button.type='button';button.style.setProperty('--chapter-color',g.color);
      button.innerHTML=`<span class="nav-line"><span class="nav-num">${String(i+1)}</span><span class="nav-label">${escapeHTML(g.shortLabel)}</span></span>`;
      button.setAttribute('aria-label',`Jump to ${g.label}: ${percent(g.share)} percent`);
      button.addEventListener('click',()=>goToGroup(i));
      dom.nav.appendChild(button);
    });
    $('data-table-body').innerHTML='';
    groups.forEach(g=>{
      const row=document.createElement('tr');
      row.innerHTML=`<td><span class="table-swatch" style="background:${g.color}" aria-hidden="true"></span>${escapeHTML(g.label)}</td><td>${compact(g.value,2)}</td><td>${percent(g.share)}%</td><td>${number.format(g.count)}</td>`;
      $('data-table-body').appendChild(row);
    });
    $('value-column').textContent=config.unit.charAt(0).toUpperCase()+config.unit.slice(1);
    $('table-caption').textContent=config.title+' — '+config.status;
    $('data-table-foot').innerHTML=`<tr><td>Total</td><td>${compact(total,3)}</td><td>100%</td><td>${number.format(tiles)}</td></tr>`;
    const tiny=groups.filter(g=>g.value>0&&g.count===0);
    $('table-note').textContent=`Percentages use the sum of the input values (${number.format(total)} ${config.unit}). Displayed percentages and compact values are rounded. Squares are apportioned to the nearest whole-grid representation; labels report the input data.`+(tiny.length?` Below one square at this resolution: ${tiny.map(g=>g.label).join(', ')}. Increase the square count to improve visibility.`:'');
    const largest=groups.reduce((max,g)=>g.value>max.value?g:max,groups[0]);
    const rest=total-largest.value;
    $('summary-title').textContent=config.summaryHeadline||'Now compare\nthe whole picture.';
    $('summary-title').style.whiteSpace='pre-line';
    const comparison=rest>0 ? (largest.value/rest>=1?`<strong>${(largest.value/rest).toFixed(1)}× the size of all the other groups combined.</strong>`:`<strong>${percent(largest.share)}% of the whole.</strong>`) : '<strong>the entire population shown.</strong>';
    $('summary-text').innerHTML=`In this dataset, “${escapeHTML(largest.label)}” represents ${comparison} Same squares. Same scale. A very different picture when everyone is included.`;
    $('source-note').textContent=config.source||'No source has been entered. Add an attribution before sharing this story.';
    $('caveat-note').textContent=config.caveat||'No caveats have been entered. Validate the source, denominator, and category definitions before publication.';
    $('rounding-note').textContent=`There are exactly ${number.format(tiles)} squares. Each stands for ${number.format(unitValue)} ${config.unit}. The largest-remainder method assigns whole squares to each group so the total remains exact. This necessarily approximates small groups: for example, “${groups[0].label}” has ${number.format(groups[0].value)} ${config.unit} but is drawn as ${groups[0].count} squares, equivalent to ${number.format(groups[0].count*unitValue)} ${config.unit}. No group is given a larger square to make it more visible.`;
    currentIndex=-1;lastTally=-1;
  }
  function measure(keepProgress=false) {
    const oldHeight=viewHeight;
    const trackTop=dom.track.getBoundingClientRect().top+window.scrollY;
    const oldProgress=(window.scrollY+offset-trackTop)/oldHeight;
    // svh keeps geometry stable while mobile browser chrome expands/collapses.
    const probe=document.createElement('div');
    probe.style.cssText='position:absolute;width:0;height:100svh;pointer-events:none;visibility:hidden';
    scope.appendChild(probe);
    offset = document.querySelector('.site-header')?.getBoundingClientRect().height || 0;
    host.style.setProperty('--waterfall-offset',offset+'px');
    viewHeight=Math.max(200,(probe.getBoundingClientRect().height||window.innerHeight)-offset);
    probe.remove();
    host.style.setProperty('--vh',viewHeight+'px');
    dom.track.style.height=((totalUnits+1)*viewHeight)+'px';
    const box=dom.box.getBoundingClientRect();
    const dpr=Math.min(window.devicePixelRatio||1,2);
    dom.canvas.width=Math.round(box.width*dpr);dom.canvas.height=Math.round(box.height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const gutter=box.width<430?79:99;
    const pad=5;
    const pitch=Math.max(1,Math.min((box.width-gutter-pad*2)/columns,(box.height-pad*2)/rows));
    const gridWidth=columns*pitch,gridHeight=rows*pitch;
    const left=pad+Math.max(0,(box.width-gutter-pad*2-gridWidth)/2);
    const top=pad+Math.max(0,(box.height-pad*2-gridHeight)/2);
    size={width:box.width,height:box.height,left,top,gridWidth,gridHeight,pitch,dot:Math.max(.7,pitch*.69)};
    dom.hint.style.left=left+'px';dom.hint.style.right=Math.max(0,box.width-left-gridWidth)+'px';
    if(keepProgress && oldHeight && Math.abs(oldHeight-viewHeight)>1 && oldProgress>=0 && oldProgress<=totalUnits) window.scrollTo(0,trackTop-offset+oldProgress*viewHeight);
    lastWidth=window.innerWidth;lastHeight=window.innerHeight;
    draw();
  }
  function stateAtScroll() {
    const rect=dom.track.getBoundingClientRect();
    const u=clamp((offset-rect.top)/viewHeight,0,totalUnits);
    let index=timeline.findIndex(segment=>u<segment.end);
    if(index<0) index=groups.length-1;
    const segment=timeline[index];
    const p=segment.fill?clamp((u-segment.start)/segment.fill):1;
    return {u,index,p,holding:p>=1,finished:u>=timeline[timeline.length-1].fillEnd};
  }
  function dotPosition(index) {
    const row=Math.floor(index/columns),col=index%columns;
    const inset=(size.pitch-size.dot)/2;
    return {x:size.left+col*size.pitch+inset,y:size.top+(rows-1-row)*size.pitch+inset};
  }
  function drawTile(x,y,color,alpha=1,stretch=1) {
    const d=size.dot;
    ctx.globalAlpha=alpha;ctx.fillStyle=color;
    ctx.fillRect(x,y,d,d*stretch);
    // A one-pixel lower face gives the field weight without glowing or gradients.
    if(stretch===1 && d>3) {ctx.fillStyle='rgba(0,0,0,.13)';ctx.fillRect(x,y+d-.65,d,.65);}
  }
  function updateNarrative(state) {
    const g=groups[state.index];
    if(currentIndex!==state.index) {
      currentIndex=state.index;
      host.style.setProperty('--accent',g.color);
      host.style.setProperty('--accent-ink',g.ink);
      $('chapter-index').textContent=String(state.index+1);
      $('chapter-label').textContent=g.label;
      $('chapter-headline').textContent=g.headline;
      $('metric-number').textContent=percent(g.share);
      $('group-value').textContent=`${words(g.value)} ${config.unit} · ${number.format(g.count)} squares`;
      $('chapter-description').textContent=replaceTokens(g.description,g);
      $('boundary-percent').textContent=percent(g.share)+'%';
      $('boundary-count').textContent=compact(g.value)+' '+config.unit;
      $('next-label').textContent=state.index===groups.length-1?'Read the full picture':'Scroll to add the next group';
      for(let i=0;i<dom.nav.children.length;i++) {
        if(i===state.index) dom.nav.children[i].setAttribute('aria-current','step');
        else dom.nav.children[i].removeAttribute('aria-current');
      }
      $('chapter-announcement').textContent=`Group ${state.index+1} of ${groups.length}. ${g.label}: ${words(g.value)} ${config.unit}, ${percent(g.share)} percent.`;
    }
    for(let i=0;i<dom.nav.children.length;i++) dom.nav.children[i].style.setProperty('--chapter-progress',i<state.index?'1':i===state.index?String(state.p):'0');
    dom.hint.style.opacity=state.index===0?'1':'0';
    $('scroll-status').textContent=state.holding?(state.index===groups.length-1?'The whole picture. Keep scrolling for the numbers.':'At the boundary. Keep scrolling for the next group.'):'Adding '+g.label.toLowerCase()+'…';
  }
  function draw() {
    if(!ctx || !groups.length || !size.width) return;
    const state=stateAtScroll();currentState=state;
    updateNarrative(state);
    ctx.clearRect(0,0,size.width,size.height);
    // Four quiet corner marks describe the total capacity, without pre-revealing
    // the large final group as a field of ghost squares.
    const l=size.left-.5,t=size.top-.5,r=l+size.gridWidth+1,b=t+size.gridHeight+1;
    ctx.globalAlpha=1;ctx.strokeStyle='#c9cec1';ctx.lineWidth=.75;
    const c=Math.max(5,Math.min(9,size.pitch));
    ctx.beginPath();
    ctx.moveTo(l,t+c);ctx.lineTo(l,t);ctx.lineTo(l+c,t);
    ctx.moveTo(r-c,t);ctx.lineTo(r,t);ctx.lineTo(r,t+c);
    ctx.moveTo(l,b-c);ctx.lineTo(l,b);ctx.lineTo(l+c,b);
    ctx.moveTo(r-c,b);ctx.lineTo(r,b);ctx.lineTo(r,b-c);ctx.stroke();
    let settled=0;
    for(let gi=0;gi<=state.index;gi++) {
      const g=groups[gi],p=gi<state.index?1:state.p;
      for(let j=0;j<g.count;j++) {
        const index=g.start+j,position=dotPosition(index);
        if(p>=1) {drawTile(position.x,position.y,g.color);settled++;continue;}
        if(reduceMotion) {
          if(j<Math.floor(g.count*p)) {drawTile(position.x,position.y,g.color);settled++;}
          continue;
        }
        // Scroll-linked waterfall: deterministic start times and trajectories,
        // so scrubbing backward unwinds the same motion instead of restarting it.
        const spread=g.count>1?j/(g.count-1):0;
        const delay=spread*.75;
        const duration=.17+hash(index+1)*.065;
        const local=(p-delay)/duration;
        if(local<=0) continue;
        if(local>=1) {drawTile(position.x,position.y,g.color);settled++;continue;}
        const progress=clamp(local);
        const fall=smoothstep(progress);
        const originY=size.top-size.dot*3-hash(index+90)*size.pitch*4;
        const y=originY+(position.y-originY)*fall;
        const drift=(hash(index+77)-.5)*size.pitch*2;
        const x=position.x+drift*(1-fall);
        const alpha=clamp(progress/.12);
        const stretch=1+(1-progress)*.55;
        // Clip each flight to the chart's own field; it never covers its caption.
        if(y>=size.top-size.dot && y<size.top+size.gridHeight) drawTile(x,y,g.color,alpha,stretch);
      }
    }
    ctx.globalAlpha=1;
    const g=groups[state.index];
    if(state.holding && g.count>0) {
      const end=dotPosition(g.end-1);
      const x1=end.x+size.dot+size.pitch*.35;
      const x2=size.left+size.gridWidth+9;
      const y=end.y+size.dot/2;
      ctx.strokeStyle=g.ink;ctx.globalAlpha=.58;ctx.lineWidth=.8;
      ctx.beginPath();ctx.moveTo(x1,y);ctx.lineTo(x2,y);ctx.stroke();ctx.globalAlpha=1;
      ctx.fillStyle=g.ink;ctx.fillRect(x2-1,y-1,2,2);
      const markerY=clamp(y-22,0,size.height-43);
      dom.marker.style.transform=`translate(${size.left+size.gridWidth+9}px,${markerY}px)`;
      dom.marker.style.opacity='1';
    } else dom.marker.style.opacity='0';
    if(settled!==lastTally) {$('visible-tally').textContent=number.format(settled);lastTally=settled;}
  }
  function scheduleDraw() {
    if(frame) return;
    frame=requestAnimationFrame(()=>{frame=0;draw();});
  }
  function cancelScrollAnimation() {
    if(scrollAnimation!==null) cancelAnimationFrame(scrollAnimation);
    scrollAnimation=null;
  }
  function scrollToY(target) {
    cancelScrollAnimation();
    if(reduceMotion) {window.scrollTo(0,target);scheduleDraw();return;}
    const start=window.scrollY,distance=target-start;
    const duration=clamp(Math.abs(distance)*.22,480,1350);
    const started=performance.now();
    function step(now) {
      const progress=clamp((now-started)/duration);
      window.scrollTo(0,start+distance*smoothstep(progress));
      if(progress<1) scrollAnimation=requestAnimationFrame(step);
      else scrollAnimation=null;
    }
    scrollAnimation=requestAnimationFrame(step);
  }
  function goToGroup(index) {
    const segment=timeline[clamp(index,0,groups.length-1)];
    const top=dom.track.getBoundingClientRect().top+window.scrollY;
    scrollToY(top-offset+(segment.fillEnd+segment.hold*.30)*viewHeight);
  }
  function showToast(message) {
    $('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);
    toastTimer=setTimeout(()=>$('toast').classList.remove('show'),3300);
  }
  function apply(data,{restart=true}={}) {
    config=validate(clone(data));allocate();buildInterface();measure();
    if(restart) {cancelScrollAnimation();window.scrollTo(0,storyTop());draw();}
  }

  // Editor utilities: user content only enters HTML through escapeHTML or textContent.
  function renderGroupEditor() {
    $('edit-groups').innerHTML='';
    draft.groups.forEach((g,i)=>{
      const box=document.createElement('div');box.className='edit-group';box.dataset.index=i;
      box.innerHTML=`<div class="edit-group-top"><label class="color-field"><span class="sr-only">Color for group ${i+1}</span><input type="color" data-field="color" value="${escapeHTML(g.color)}"></label><label class="field">Group ${i+1}<input data-field="label" required maxlength="100" value="${escapeHTML(g.label)}"></label><label class="field">Value<input data-field="value" required type="number" min="0" step="any" value="${g.value}"></label><button type="button" class="remove-group" data-remove="${i}" aria-label="Remove group ${i+1}" ${draft.groups.length<=2?'disabled':''}>×</button></div><details class="group-narration"><summary>Edit this group’s narration</summary><div class="form-grid"><label class="field">Short navigation label<input data-field="shortLabel" maxlength="40" value="${escapeHTML(g.shortLabel||g.label)}"></label><label class="field">Headline (use \\n for a line break)<input data-field="headline" maxlength="140" value="${escapeHTML((g.headline||g.label).replace(/\n/g,'\\n'))}"></label><label class="field wide">Description<textarea data-field="description" rows="2" maxlength="600">${escapeHTML(g.description||'')}</textarea><small>Optional tokens: {value}, {unit}, {tiles}, {totalSquares}, {share}.</small></label></div></details>`;
      $('edit-groups').appendChild(box);
    });
    $('add-group').disabled=draft.groups.length>=8;
  }
  function populateEditor(data) {
    draft=clone(data);draftBaseline=populationKey(data);
    $('edit-title').value=draft.title;$('edit-unit').value=draft.unit;$('edit-tiles').value=draft.totalSquares;
    $('edit-status').value=draft.status;$('edit-source').value=draft.source;$('edit-caveat').value=draft.caveat;
    $('editor-error').textContent='';renderGroupEditor();
  }
  const populationKey=data=>JSON.stringify([data.title,data.groups.map(g=>[g.label,g.value])]);
  function readDraft(validateNow=true) {
    const data={...draft,title:$('edit-title').value.trim(),unit:$('edit-unit').value.trim(),totalSquares:Number($('edit-tiles').value),status:$('edit-status').value.trim(),source:$('edit-source').value.trim(),caveat:$('edit-caveat').value.trim()};
    data.groups=[...$('edit-groups').children].map((node,i)=>{
      const group={...draft.groups[i]};
      node.querySelectorAll('[data-field]').forEach(input=>{
        group[input.dataset.field]=input.dataset.field==='value'?(input.value.trim()===''?NaN:Number(input.value)):input.value.trim();
        if(input.dataset.field==='headline') group.headline=group.headline.replace(/\\n/g,'\n');
      });
      return group;
    });
    // A bespoke default summary is no longer appropriate if the population changes.
    if(populationKey(data)!==draftBaseline) data.summaryHeadline='Now compare\nthe whole picture.';
    return validateNow?validate(data):data;
  }
  function openEditor(event) {
    opener=event?.currentTarget||scope.activeElement;
    populateEditor(config);$('preset-select').value='custom';
    dom.dialog.showModal();
  }
  function closeEditor() {dom.dialog.close();if(opener?.focus) opener.focus();}
  function download(content,name,type) {
    const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);
    const anchor=document.createElement('a');anchor.href=url;anchor.download=name;document.body.appendChild(anchor);anchor.click();anchor.remove();
    setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  function safeName(title) {return title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,70)||'scale-story';}
  function handleEditorAction(action) {
    try {const data=readDraft();$('editor-error').textContent='';action(data);} catch(error) {$('editor-error').textContent=error.message;}
  }
  scope.querySelectorAll('[data-open-editor]').forEach(button=>button.addEventListener('click',openEditor));
  scope.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();$('numbers').scrollIntoView();$('summary-title').setAttribute('tabindex','-1');$('summary-title').focus({preventScroll:true});});
  $('close-editor').addEventListener('click',closeEditor);
  dom.dialog.addEventListener('click',event=>{if(event.target===dom.dialog){const r=dom.dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeEditor();}});
  dom.dialog.addEventListener('close',()=>{if(opener?.focus)opener.focus();});
  $('preset-select').addEventListener('change',event=>{if(event.target.value==='ai')populateEditor(defaultData);else if(event.target.value==='reach')populateEditor(reachData);else if(event.target.value==='custom')populateEditor(config);});
  $('edit-groups').addEventListener('click',event=>{const button=event.target.closest('[data-remove]');if(!button)return;draft=readDraft(false);draft.groups.splice(Number(button.dataset.remove),1);renderGroupEditor();});
  $('add-group').addEventListener('click',()=>{draft=readDraft(false);draft.groups.push({id:'group-'+Date.now(),label:'New group',shortLabel:'New group',value:0,color:'#526d91',headline:'Another part\nof the picture.',description:'{value} {unit}, or {share} of the total.'});renderGroupEditor();});
  $('sort-groups').addEventListener('click',()=>{draft=readDraft(false);draft.groups.sort((a,b)=>a.value-b.value);renderGroupEditor();});
  $('editor-form').addEventListener('submit',event=>{event.preventDefault();handleEditorAction(data=>{closeEditor();apply(data);showToast('Your data is in place. Scroll to rebuild the picture.');});});
  $('export-json').addEventListener('click',()=>handleEditorAction(data=>download(JSON.stringify(data,null,2),safeName(data.title)+'.json','application/json')));
  $('export-html').addEventListener('click',()=>handleEditorAction(data=>{
    const copy=host.cloneNode(true);
    copy.removeAttribute('style');
    const template=copy.querySelector('template');
    template.content.querySelector('#scale-data').textContent=JSON.stringify(data).replace(/</g,'\\u003c');
    const fallback=copy.querySelector('.waterfall-fallback');
    fallback.innerHTML=fallbackMarkup(data);
    const title=escapeHTML(data.title);
    // Publication URL and artwork belong to the exported chart's future host.
    const icon=document.head.querySelector('link[rel="icon"]')?.outerHTML||'';
    const description=escapeHTML(data.status+' '+data.source);
    const social=icon+'<meta name="description" content="'+description+'"><meta property="og:type" content="website"><meta property="og:title" content="'+title+'"><meta property="og:description" content="'+description+'"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="'+title+'"><meta name="twitter:description" content="'+description+'">';
    const script='('+initWaterfall.toString()+')(document.querySelector(".waterfall-host"));';
    download('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title>'+social+'<style>body{margin:0}.waterfall-host{display:block}</style></head><body>'+copy.outerHTML+'<script>'+script.replace(/<\/script/gi,'<\\/script')+'<'+ '/script></body></html>',safeName(data.title)+'.html','text/html');
    showToast('Standalone HTML created with your edited data.');
  }));
  $('import-json').addEventListener('click',()=>$('json-file').click());
  $('json-file').addEventListener('change',async event=>{
    const input=event.target;
    const file=input.files[0];if(!file)return;
    try {if(file.size>500000)throw Error('Use a JSON dataset smaller than 500 KB.');const data=validate(JSON.parse(await file.text()));populateEditor(data);$('preset-select').value='custom';}catch(error){$('editor-error').textContent='Could not import: '+error.message;}finally{input.value='';}
  });
  $('show-all').addEventListener('click',()=>goToGroup(groups.length-1));
  $('replay').addEventListener('click',()=>scrollToY(storyTop()));
  $('brand-link').addEventListener('click',event=>{event.preventDefault();scrollToY(storyTop());});
  $('next-group').addEventListener('click',()=>{if(currentIndex>=groups.length-1)scrollToY($('numbers').getBoundingClientRect().top+window.scrollY);else goToGroup(currentIndex+1);});
  $('data-note').addEventListener('click',()=>{$('methodology').open=true;scrollToY($('methodology').getBoundingClientRect().top+window.scrollY-22);});
  let reportPaused=document.documentElement.classList.contains('no-motion');
  if(reportPaused) reduceMotion=true;
  new MutationObserver(()=>{
    const next=document.documentElement.classList.contains('no-motion');
    if(next===reportPaused)return;
    reportPaused=next;reduceMotion=next;
    $('reduce-motion').checked=next;cancelScrollAnimation();scheduleDraw();
  }).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  $('reduce-motion').checked=reduceMotion;
  $('reduce-motion').addEventListener('change',event=>{reduceMotion=event.target.checked;cancelScrollAnimation();scheduleDraw();});
  motionQuery.addEventListener?.('change',event=>{reduceMotion=event.matches;$('reduce-motion').checked=reduceMotion;cancelScrollAnimation();scheduleDraw();});
  window.addEventListener('scroll',scheduleDraw,{passive:true});
  // A user gesture always wins over a button-initiated guided scroll.
  for(const name of ['wheel','touchstart','pointerdown'])window.addEventListener(name,cancelScrollAnimation,{passive:true});
  window.addEventListener('keydown',event=>{if(['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key))cancelScrollAnimation();});
  window.addEventListener('resize',()=>{
    // Ignore height-only changes from mobile address bars. Width changes and
    // desktop window resizes get a new, proportional chart layout.
    const widthChanged=Math.abs(window.innerWidth-lastWidth)>1;
    if(!widthChanged&&window.innerWidth<761&&Math.abs(window.innerHeight-lastHeight)<170)return;
    if(geometryPending)return;geometryPending=true;
    requestAnimationFrame(()=>{geometryPending=false;measure(true);});
  });
  if('ResizeObserver' in window){let first=true;new ResizeObserver(()=>{if(first){first=false;return;}if(!geometryPending){geometryPending=true;requestAnimationFrame(()=>{geometryPending=false;measure();});}}).observe(dom.box);}
  window.addEventListener('beforeprint',()=>$('methodology').open=true);
  // Expose a read-only snapshot for embedding diagnostics and automated QA.
  host.ScaleStory=Object.freeze({getData:()=>clone(config),getState:()=>({...currentState,settled:lastTally,totalSquares:tiles,allocations:groups.map(g=>({label:g.label,squares:g.count,value:g.value,share:g.share}))}),goToGroup});
  try {apply(defaultData,{restart:false});requestAnimationFrame(()=>measure());} catch(error) {$('chapter-headline').textContent='Check the dataset.';$('chapter-description').textContent=error.message;console.error(error);}

  }
  kit.onReady(()=>document.querySelectorAll(".waterfall-host").forEach(initWaterfall));
