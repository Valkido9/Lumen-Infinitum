/* Original timepiece choreography, inspired by RhineLabUI's staged geometric
 * boot sequence. All visual phases are sampled from one soundtrack clock. */
(() => {
  'use strict';
  const root = document.querySelector('.cinema');
  if (!root) return;
  const canvas = root.querySelector('canvas');
  const ctx = canvas.getContext('2d');
  const audio = root.querySelector('audio');
  const enter = root.querySelector('.cinema-enter');
  const title = root.querySelector('.cinema-title');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const REVEAL = Number(root.dataset.revealTime) || 14.6;
  const TAU = Math.PI * 2;
  let state = 'playing', raf = 0, previous = 0, fallbackTime = 0;
  let silent = true, busy = false, disposed = false, width = 0, height = 0;
  let current = 0, clockOffset = 0, blocked = false, gated = true, startedAt = 0, audioError = false;
  let pointerX = 0, pointerY = 0;
  const priorInert = new Map();
  const clamp = v => Math.max(0, Math.min(1, v));
  const phase = (t, a, b) => clamp((t-a)/(b-a));
  const ease = x => x*x*(3-2*x);
  // Seeded coordinates remain stable through resizing, seeking and screenshots.
  let seed = 71837;
  const random = () => {seed = (seed*1664525+1013904223)>>>0;return seed/4294967296;};
  const motes = Array.from({length:180},()=>({a:random()*TAU,r:random(),z:random(),s:random()}));

  function dismissImmediately() {
    disposed = true; state = 'entered'; root.hidden = true; audio.pause();
    document.body.classList.remove('at-opening');
  }
  // Existing chapter/ability links must open their destination directly.
  if (location.hash && location.hash !== '#opening-title') {dismissImmediately();return;}
  document.documentElement.classList.add('cinema-locked');
  for (const el of document.body.children) {
    if (el === root || /^(SCRIPT|STYLE|LINK)$/.test(el.tagName)) continue;
    priorInert.set(el,el.inert);el.inert=true;
  }
  root.tabIndex = -1;
  root.focus({preventScroll:true});
  audio.volume = .35;
  audio.loop = false;

  function line(x1,y1,x2,y2,color,weight=1) {
    ctx.strokeStyle=color;ctx.lineWidth=weight;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
  }
  function arc(radius,start,end,color,weight=1) {
    if(radius<=0 || end<=start) return;
    ctx.strokeStyle=color;ctx.lineWidth=weight;ctx.beginPath();ctx.arc(0,0,radius,start,end);ctx.stroke();
  }
  function polygon(radius,sides,rotation,color,weight=1) {
    ctx.strokeStyle=color;ctx.lineWidth=weight;ctx.beginPath();
    for(let i=0;i<=sides;i++){
      const a=rotation+i*TAU/sides;const x=Math.cos(a)*radius,y=Math.sin(a)*radius;
      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }ctx.stroke();
  }
  function infinity(t,opacity,scale=1) {
    ctx.save();ctx.scale(scale,scale);ctx.lineWidth=1.6;ctx.strokeStyle=`rgba(170,202,172,${opacity})`;ctx.beginPath();
    const n=Math.floor(300*ease(phase(t,.7,3)));
    for(let i=0;i<=n;i++) {
      const a=i/300*TAU;const x=114*Math.cos(a)/(1+Math.sin(a)**2),y=114*Math.sin(a)*Math.cos(a)/(1+Math.sin(a)**2);
      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }ctx.stroke();ctx.restore();
  }
  function ringAssembly(t,alpha=1) {
    ctx.save();ctx.globalAlpha=alpha;
    const draw=phase(t,.25,3.3), spread=ease(phase(t,3,5.8));
    for(let ring=0;ring<7;ring++) {
      const radius=142+ring*(9+spread*9);
      const rot=(ring%2?-1:1)*t*(.05+ring*.013);
      for(let j=0;j<6;j++){
        const start=rot+j*TAU/6;
        arc(radius,start,start+(TAU/6-.1)*draw,ring%3===0?'#a5824b':'#90b8a0',ring===3?2:.65);
      }
    }
    for(let i=0;i<120*draw;i++) {
      const a=i*TAU/120+t*.035,r=276;
      const len=i%10===0?14:i%5===0?8:3;
      line(Math.cos(a)*r,Math.sin(a)*r,Math.cos(a)*(r+len),Math.sin(a)*(r+len),'#91a98b',i%10===0?1.3:.6);
    }
    // Offset orbital bearings, articulated spokes and a rotating reticle.
    for(let j=0;j<4;j++){
      const a=j*Math.PI/2+t*.12;
      ctx.save();ctx.rotate(a);line(194,0,252,0,'#98b399',.7);
      ctx.strokeStyle='#9db395';ctx.lineWidth=.8;ctx.strokeRect(224,-5,10,10);ctx.restore();
    }
    ctx.save();ctx.rotate(t*.08);polygon(113+spread*18,4,Math.PI/4,'#a7b78a55');ctx.restore();
    infinity(t,1-phase(t,4.8,6));
    ctx.restore();
  }
  function spatialBackdrop(t) {
    // Perspective projection with a slowly orbiting camera. The same geometry
    // continues behind the title; there is no scene replacement at the cue.
    const yaw=t*.028+pointerX*.055, pitch=.42+Math.sin(t*.13)*.09+pointerY*.04;
    const cy=Math.cos(yaw),sy=Math.sin(yaw),cx=Math.cos(pitch),sx=Math.sin(pitch);
    const project=([x,y,z])=>{
      const rx=x*cy+z*sy,rz=-x*sy+z*cy;
      const ry=y*cx-rz*sx,depth=y*sx+rz*cx;
      const perspective=1050/(1250+depth);
      return [rx*perspective,ry*perspective,depth];
    };
    const path=(vertices,stroke,fill,weight=.7)=>{
      const points=vertices.map(project);ctx.beginPath();
      points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));
      ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill();}
      ctx.strokeStyle=stroke;ctx.lineWidth=weight;ctx.stroke();
    };
    ctx.save();
    ctx.globalAlpha=.55+.2*phase(t,0,6);
    const glow=ctx.createRadialGradient(-180,-120,30,0,0,800);
    glow.addColorStop(0,'#437f6630');glow.addColorStop(1,'#07151700');
    ctx.fillStyle=glow;ctx.fillRect(-1600,-1100,3200,2200);
    // Axonometric ribs and bevelled translucent annuli.
    for(let ring=0;ring<5;ring++){
      const r=370+ring*36,z=(ring-2)*34;
      const vertices=[];
      for(let i=0;i<112;i++){
        const a=i/112*TAU;vertices.push([Math.cos(a)*r,Math.sin(a)*r,z]);
      }
      path(vertices,ring%2?'#9cb99b40':'#d0bd8460',null,ring===2?1.2:.65);
      if(ring===2)for(let i=0;i<48;i++){
        const a=i/48*TAU;
        const p=project([Math.cos(a)*r,Math.sin(a)*r,z-26]);
        const q=project([Math.cos(a)*(r+12),Math.sin(a)*(r+12),z+26]);
        line(p[0],p[1],q[0],q[1],'#9caf8e55',.65);
      }
    }
    // Stars have depth and follow the camera instead of sliding in screen space.
    for(const m of motes){
      const a=m.a+t*.006,p=project([Math.cos(a)*(200+m.r*1100),Math.sin(a)*(200+m.r*900),(m.z-.5)*450]);
      ctx.fillStyle=`rgba(205,216,182,${.13+m.s*.38})`;
      ctx.beginPath();ctx.arc(p[0],p[1],.4+m.s*.8,0,TAU);ctx.fill();
    }
    ctx.restore();
  }
  function draw(t) {
    if(!ctx || !width || !height)return;
    const settled=t>=REVEAL;
    ctx.globalAlpha=1;ctx.fillStyle='#071517';ctx.fillRect(0,0,width,height);
    const scale=Math.min(width/1100,height/850);
    ctx.save();ctx.translate(width/2,height/2);ctx.scale(scale,scale);
    if(reduced.matches){
      ctx.globalAlpha=.16;arc(240,0,TAU,'#d2c9a3');arc(258,0,TAU,'#d2c9a3');ctx.restore();return;
    }
    spatialBackdrop(t);
    // 0–6s: registration grid, traced infinity emblem, seven concentric mechanisms.
    if(t<9.5) {
      const gridAlpha=(1-phase(t,6,9))*.12;
      for(let i=-12;i<=12;i++){
        line(i*64,-900,i*64,900,`rgba(122,161,139,${gridAlpha})`,.55);
        line(-1400,i*64,1400,i*64,`rgba(122,161,139,${gridAlpha})`,.55);
      }
      const crop=ease(phase(t,0,1.5));
      for(const sx of [-1,1])for(const sy of [-1,1]){
        line(sx*320,sy*320,sx*(320-26*crop),sy*320,'#a3b494',1);
        line(sx*320,sy*320,sx*320,sy*(320-26*crop),'#a3b494',1);
      }
      ctx.save();
      const zoom=1+ease(phase(t,5.5,7.8))*.4;
      ctx.scale(zoom,zoom);ringAssembly(t,1-phase(t,7.8,9.5));ctx.restore();
    }
    // 6–10s: scan planes, counter-rotating apertures and travelling orange nodes.
    if(t>=5.8 && t<11.5){
      const a=phase(t,5.8,6.4)*(1-phase(t,10,11.5));ctx.globalAlpha=a;
      const sweep=(t-5.8)*1.1;
      for(let j=0;j<3;j++){
        ctx.save();ctx.rotate(sweep*(j%2?-1:1)+j);
        const r=190+j*72;arc(r,-.5,1.4,'#a5bd9f',1.2);arc(r,2.1,3.9,'#b6c49a',.6);
        line(-r-50,0,r+50,0,'#a9be9a33',.65);
        ctx.fillStyle='#bb7c39';ctx.beginPath();ctx.arc(r,0,4,0,TAU);ctx.fill();ctx.restore();
      }
      const scanY=Math.sin((t-5.8)*1.25)*270;
      line(-370,scanY,370,scanY,'#a17d42',1.1);
      for(let i=0;i<18;i++)line(-370,scanY-i*3,370,scanY-i*3,`rgba(119,134,101,${.07*(1-i/18)})`,1);
      ctx.globalAlpha=1;
    }
    // 8–13s: projected archive planes form a deep, accelerating time tunnel.
    if(t>8 && t<14.8){
      const alpha=phase(t,8,9.2)*(1-phase(t,13.2,14.8));ctx.save();ctx.globalAlpha=alpha;
      ctx.rotate(-.28+Math.sin(t*.2)*.12);
      const travel=(t-8)*(.16+phase(t,10,13)*.4);
      for(let i=0;i<24;i++){
        const z=((i/24+travel)%1),p=1/(.18+z*3.8),r=170*p;
        ctx.globalAlpha=alpha*Math.min(1,z*5)*.48;
        ctx.save();ctx.rotate(i*.038+Math.sin(t*.3)*.06);
        ctx.strokeStyle=i%4===0?'#987641':'#91af9b';ctx.lineWidth=i%4===0?1.5:.7;
        ctx.strokeRect(-r,-r*.65,r*2,r*1.3);
        arc(r*.46,0,TAU,'#b8c598',.7);
        for(const side of [-1,1]){
          line(side*r*.82,-r*.43,side*r*.82,r*.43,'#8fae92',.55);
          for(let k=0;k<5;k++)line(side*r*.7,-r*.3+k*r*.13,side*r*.55,-r*.3+k*r*.13,'#b6c697',.65);
        }ctx.restore();
      }
      ctx.restore();
    }
    // 12–15s: everything contracts into one time singularity.
    if(t>=12 && t<REVEAL){
      const p=ease(phase(t,12,REVEAL));ctx.save();ctx.globalAlpha=phase(t,12,12.6);
      const radius=260*(1-p)+4;
      for(let j=0;j<12;j++){
        const r=radius*(1+j*.12),a=t*(.2+j*.09);
        arc(r,a,a+Math.PI*(1.4+.5*p),j%3?'#a2bc93':'#ac894e',j%3?.65:1.5);
      }
      for(let j=0;j<36;j++){
        const a=j*TAU/36+t*.25;
        const r=radius+30*(1-p),end=r+170*(1-p);
        line(Math.cos(a)*r,Math.sin(a)*r,Math.cos(a)*end,Math.sin(a)*end,'#b9c68f66',.7);
      }
      ctx.fillStyle='#c6d9ae';ctx.beginPath();ctx.arc(0,0,3+9*phase(t,14.5,REVEAL),0,TAU);ctx.fill();ctx.restore();
    }
    // On the music attack: expanding wave over the same continuous spatial scene.
    if(settled){
      const dt=t-REVEAL;
      const glow=ctx.createRadialGradient(0,0,10,0,0,600);
      glow.addColorStop(0,'#54745522');glow.addColorStop(.5,'#264e3f16');glow.addColorStop(1,'#07151700');
      ctx.fillStyle=glow;ctx.fillRect(-1200,-900,2400,1800);
      for(let j=0;j<5;j++){
        ctx.save();ctx.scale(1,.58+j*.07);ctx.rotate(-.35+j*.05);
        arc(330+j*48,dt*.014+j,dt*.014+j+TAU*.85,'#bec59922',.7);ctx.restore();
      }
      if(dt<2.5){ctx.globalAlpha=(1-dt/2.5)*.5;arc(20+dt*450,0,TAU,'#dedab3',1.2);ctx.globalAlpha=1;}
      for(const m of motes){
        const r=80+m.r*950,a=m.a+dt*.006*(m.s+.1);
        ctx.fillStyle=`rgba(201,211,173,${.15+m.s*.42})`;ctx.beginPath();ctx.arc(Math.cos(a)*r,Math.sin(a)*r*.7,.4+m.s,0,TAU);ctx.fill();
      }
    }
    ctx.restore();
  }

  function resize(){
    width=root.clientWidth;height=root.clientHeight;
    const dpr=Math.min(devicePixelRatio||1,1.5);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    if(ctx)ctx.setTransform(dpr,0,0,dpr,0,0);
    draw(current);
  }
  function reveal(){
    if(state==='ready')return;
    state='ready';root.classList.add('ready');
    title.setAttribute('aria-hidden','false');enter.disabled=false;
    enter.focus({preventScroll:true});
  }
  function tick(now){
    raf=0;if(disposed || document.hidden)return;
    const delta=previous?Math.min((now-previous)/1000,.1):0;previous=now;
    if(silent)fallbackTime+=delta;
    current=silent?fallbackTime:Math.max(current,audio.currentTime+clockOffset);
    if(current>=REVEAL)reveal();
    draw(current);
    raf=requestAnimationFrame(tick);
  }
  function runSilent(){
    silent=true;fallbackTime=current;
  }
  async function start(align=false){
    if(disposed || busy)return;
    busy=true;
    try{
      if(localStorage.getItem('lumen-music-muted')==='1'){runSilent();return;}
      if(align && audio.readyState>0)audio.currentTime=current;
      await audio.play();
      if(disposed){audio.pause();return;}
      clockOffset=(align || state==='ready')?current-audio.currentTime:0;
      blocked=false;silent=false;audioError=false;
    }catch(error){
      if(!disposed){blocked=error.name==='NotAllowedError';runSilent();}
    }finally{busy=false;}
  }
  function skip(){
    if(disposed || state==='ready')return;
    current=Math.max(current,REVEAL);fallbackTime=current;
    if(!silent){
      try{audio.currentTime=REVEAL;}catch(_){}
      clockOffset=current-audio.currentTime;
    }
    reveal();draw(current);
    // The skip click is a user gesture — retry a soundtrack that failed to load.
    if(silent || blocked)start(true);
  }
  function leave(){
    if(state!=='ready' || disposed)return;
    disposed=true;state='entered';cancelAnimationFrame(raf);
    root.classList.add('leaving');
    // The soundtrack exits with the picture; story music can then take over.
    const volume=audio.volume,startTime=performance.now();
    function fade(now){
      const p=clamp((now-startTime)/600);audio.volume=volume*(1-p);
      if(p<1)requestAnimationFrame(fade);else audio.pause();
    }requestAnimationFrame(fade);
    setTimeout(()=>{
      root.hidden=true;audio.pause();
      for(const [el,inert] of priorInert)el.inert=inert;
      document.documentElement.classList.remove('cinema-locked');
      document.body.classList.remove('at-opening');
      window.scrollTo({top:0,behavior:'instant'});
      document.getElementById('reading-interface').focus({preventScroll:true});
      window.dispatchEvent(new Event('scroll'));
      removeEventListener('resize',resize);
    },reduced.matches?0:650);
  }
  enter.addEventListener('click',e=>{e.stopPropagation();leave();});
  // Click-to-start prologue: until the first gesture the film is frozen on its
  // opening frame behind a blinking "点击屏幕"; one click (or Enter / Space)
  // launches the visuals and the soundtrack together from 0.
  const wantsSound = () => localStorage.getItem('lumen-music-muted') !== '1';
  const soundOn = () => !audio.paused;
  function startSoundAtCurrent(){
    // Begin at the film's current clock position so a late start never leaps
    // to a loud cue; on the very first gesture the clock is still ~0.
    if(disposed) return;
    try{ if(audio.readyState>0) audio.currentTime = current; }catch(_){}
    start(false);
  }
  function begin(){
    if(disposed || !gated) return;
    gated=false;startedAt=performance.now();
    root.classList.add('started');
    previous=0;
    startSoundAtCurrent();
    raf=requestAnimationFrame(tick);
  }
  function gateGesture(ev){
    if(!gated) return;
    if(ev.type==='pointerdown' && ev.button!==0) return;
    if(ev.type==='keydown' && ev.key!=='Enter' && ev.key!==' ') return;
    if(ev.type==='keydown') ev.preventDefault();
    begin();
  }
  document.addEventListener('pointerdown', gateGesture, true);
  document.addEventListener('keydown', gateGesture, true);
  root.addEventListener('click',()=>{
    const justStarted = startedAt && performance.now()-startedAt<900;
    if(justStarted) startedAt=0;
    if(state!=='ready'){
      // Some mobile browsers release the audio element only on a *click*, so the
      // first pointerdown may play the film muted. Until the soundtrack is truly
      // running, a click just turns it on from the film's current time — never a
      // skip, never a jump to the reveal cue. Once music is playing, a click skips.
      if(wantsSound() && !soundOn() && !audioError){ startSoundAtCurrent(); return; }
      if(!justStarted) skip();
    }
  });
  root.addEventListener('keydown',e=>{
    if((e.key==='Enter'||e.key===' ') && e.target===root){
      if(startedAt && performance.now()-startedAt<900){startedAt=0;return;}
      e.preventDefault();skip();
    }
  });
  root.addEventListener('pointermove',e=>{
    pointerX=(e.clientX/width-.5)*2;pointerY=(e.clientY/height-.5)*2;
  },{passive:true});
  root.addEventListener('pointerleave',()=>{pointerX=0;pointerY=0;});
  audio.addEventListener('error',()=>{if(!disposed){audioError=true;runSilent();}});
  audio.addEventListener('seeked',()=>{if(!disposed && !silent)clockOffset=current-audio.currentTime;});
  audio.addEventListener('ended',()=>{if(!disposed){audioError=true;runSilent();}});
  function resume(){
    if(disposed)return;
    if(gated)return; // still frozen on the click-to-start screen
    previous=0;cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);
    if(!silent)start(true);
  }
  document.addEventListener('visibilitychange',()=>{
    cancelAnimationFrame(raf);previous=0;
    if(disposed)return;
    if(document.hidden)audio.pause();else resume();
  });
  addEventListener('pagehide',()=>{audio.pause();cancelAnimationFrame(raf);});
  addEventListener('pageshow',e=>{if(e.persisted)resume();});
  addEventListener('resize',resize);resize();
})();
