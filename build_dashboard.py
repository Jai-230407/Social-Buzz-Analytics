from pathlib import Path
import json
import pandas as pd
import plotly
ROOT=Path(__file__).parent
DATA=ROOT/'data/processed'
fact=pd.read_csv(DATA/'fact_reactions.csv')
rows=fact[['Category','Content Type','Sentiment','Score','Month','Content ID']].values.tolist()
raw=json.dumps(rows,separators=(',',':'))
js=plotly.offline.get_plotlyjs()
styles='''
*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#192438;font-family:Inter,Segoe UI,Arial,sans-serif}
.wrapper{max-width:1370px;margin:auto;padding:30px 28px 50px}
.header{background:linear-gradient(115deg,#0b2030,#133b46);color:#fff;border-radius:18px;padding:30px 36px;margin-bottom:22px;display:flex;justify-content:space-between;align-items:center;gap:16px}
.tag{display:inline-block;background:#d7ece9;color:#0f665d;border-radius:18px;font-size:11px;letter-spacing:.07em;font-weight:800;padding:6px 12px;text-transform:uppercase}
.header h1{font-size:32px;line-height:1.14;letter-spacing:-.7px;margin:12px 0 9px}.header p{opacity:.78;margin:0;line-height:1.6}.logo{font-weight:800;font-size:20px;letter-spacing:.05em;white-space:nowrap}
.controls{display:flex;gap:15px;flex-wrap:wrap;margin-bottom:22px;padding:15px;background:white;border:1px solid #e6eaf0;border-radius:12px}
.controls label{font-size:12px;color:#536274;font-weight:700;display:flex;flex-direction:column;gap:7px;flex:1;min-width:190px}
select{background:white;border:1px solid #dce3eb;border-radius:7px;padding:11px 12px;font-size:13px;color:#1c3046;outline-color:#0f766e}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:18px}
.kpi{background:#fff;border:1px solid #e7ebf0;padding:22px 22px 19px;border-radius:13px;box-shadow:0 4px 13px rgba(16,24,40,.02)}
.kpi b{display:block;color:#657185;text-transform:uppercase;letter-spacing:.07em;font-size:11px;margin-bottom:9px}
.kpi strong{font-size:30px;letter-spacing:-.9px;color:#172d3d}.kpi small{display:block;margin-top:6px;font-size:11px;color:#7f8c9c}
.chartgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:17px}.panel{background:#fff;border:1px solid #e7ebf0;border-radius:12px;padding:18px 18px 10px;min-width:0}
.panel h3{font-size:15px;margin:0 0 0 6px;color:#19283c}.panel .sub{font-size:11px;margin:6px 0 0 6px;color:#6c7688}
.chart{height:330px;width:100%}.bottom{margin-top:19px;display:grid;grid-template-columns:1.1fr .9fr;gap:17px}.insight{background:white;border:1px solid #e7ebf0;border-radius:12px;padding:25px 28px}
.insight h3{margin:0 0 12px;font-size:16px}.insight li{margin:10px 0;line-height:1.55;font-size:13px;color:#4e596b}
.tbl{width:100%;border-collapse:collapse;margin-top:13px}.tbl td,.tbl th{padding:9px 8px;text-align:left;border-bottom:1px solid #edf0f5;font-size:12px}.tbl th{font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em}
.foot{font-size:11px;color:#7d8795;padding-top:21px;line-height:1.5}
@media(max-width:900px){.kpis{grid-template-columns:1fr 1fr}.chartgrid,.bottom{grid-template-columns:1fr}.header{flex-direction:column;align-items:flex-start}}@media(max-width:460px){.kpis{grid-template-columns:1fr}.wrapper{padding:12px}.header{padding:22px}.header h1{font-size:25px}}
'''
script='''
const DATA=DATA_PLACEHOLDER;
const CATEGORY=0, FORMAT=1, SENTIMENT=2, SCORE=3, MONTH=4, POST=5;
const fmt=x=>Math.round(x).toLocaleString('en-US');
const val=id=>document.getElementById(id).value;
function aggregate(rows,col){const d={};rows.forEach(r=>{const k=r[col];if(!d[k])d[k]={s:0,n:0,p:new Set()};d[k].s+=Number(r[SCORE]);d[k].n++;d[k].p.add(r[POST]);});return Object.entries(d).map(([k,v])=>({name:k,score:v.s,count:v.n,posts:v.p.size}));}
function filters(){const ca=val('category'),f=val('format'),s=val('sentiment');return DATA.filter(r=>(ca==='all'||r[CATEGORY]===ca)&&(f==='all'||r[FORMAT]===f)&&(s==='all'||r[SENTIMENT]===s));}
function plot(id,traces,layout){Plotly.react(id,traces,{...layout,margin:layout.margin||{l:55,r:15,t:15,b:53},paper_bgcolor:'white',plot_bgcolor:'white',font:{family:'Segoe UI, Arial',color:'#526173',size:11},showlegend:layout.showlegend||false}, {displayModeBar:false,responsive:true});}
function render(){
const rows=filters(),cats=aggregate(rows,CATEGORY).sort((a,b)=>b.score-a.score);
const formats=aggregate(rows,FORMAT).sort((a,b)=>b.score-a.score),months=aggregate(rows,MONTH).sort((a,b)=>a.name.localeCompare(b.name)),sent=aggregate(rows,SENTIMENT).sort((a,b)=>b.count-a.count);
const points=rows.reduce((s,r)=>s+Number(r[SCORE]),0);document.getElementById('points').innerText=fmt(points);
document.getElementById('events').innerText=fmt(rows.length);document.getElementById('posts').innerText=fmt(new Set(rows.map(r=>r[POST])).size);document.getElementById('categories').innerText=fmt(cats.length);
const catsDesc=cats.slice(0,10).reverse();
plot('cat-chart',[{type:'bar',orientation:'h',x:catsDesc.map(c=>c.score),y:catsDesc.map(c=>c.name),marker:{color:'#0F766E'},hovertemplate:'%{y}: %{x:,.0f} points<extra></extra>'}],{margin:{l:120,r:18,t:18,b:32},xaxis:{gridcolor:'#edf1f4',title:'Weighted popularity points'},yaxis:{automargin:true}});
plot('month-chart',[{type:'scatter',mode:'lines+markers',x:months.map(d=>d.name),y:months.map(d=>d.score),line:{color:'#3268C8',width:3},marker:{size:7},hovertemplate:'%{x}: %{y:,.0f} points<extra></extra>'}],{margin:{l:55,r:18,t:17,b:57},xaxis:{tickangle:-45},yaxis:{gridcolor:'#edf1f4',title:'Points'}});
plot('format-chart',[{type:'bar',x:formats.map(d=>d.name),y:formats.map(d=>d.score),marker:{color:['#6366F1','#10B981','#F59E0B','#94A3B8']},hovertemplate:'%{x}: %{y:,.0f} points<extra></extra>'}],{margin:{l:64,r:17,t:17,b:49},yaxis:{gridcolor:'#edf1f4'}});
plot('sent-chart',[{type:'pie',hole:.60,labels:sent.map(d=>d.name),values:sent.map(d=>d.count),textinfo:'label+percent',marker:{colors:sent.map(d=>({'positive':'#0F766E','negative':'#DC2626','neutral':'#9CA3AF'})[d.name]||'#6366F1')},sort:false}],{margin:{l:10,r:10,t:10,b:10},showlegend:false});
const top5=cats.slice(0,5),sum5=top5.reduce((s,v)=>s+v.score,0);document.getElementById('top5share').innerText=(points?100*sum5/points:0).toFixed(1)+'%';
document.getElementById('top5').innerHTML=top5.map((r,i)=>`<tr><td>${i+1}</td><td>${r.name}</td><td>${fmt(r.score)}</td><td>${fmt(r.count)}</td></tr>`).join('');
}
window.addEventListener('DOMContentLoaded',()=>{['category','format','sentiment'].forEach(id=>document.getElementById(id).addEventListener('change',render));render();});
'''.replace('DATA_PLACEHOLDER',raw)
html=f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Social Buzz | Executive Analytics</title><style>{styles}</style><script>{js}</script></head><body>
<div class="wrapper"><div class="header"><div><span class="tag">Independent portfolio build • Synthetic teaching data</span><h1>Social Buzz | Executive Analytics</h1><p>Content popularity · weighted engagement · audience reaction patterns<br>Interactive demonstration inspired by the Accenture–Forage case study.</p></div><div class="logo">SOCIAL / BUZZ</div></div>
<div class="controls"><label>Content category<select id="category"><option value="all">All categories</option>{''.join('<option>'+x+'</option>' for x in sorted(fact['Category'].unique()))}</select></label><label>Content format<select id="format"><option value="all">All formats</option>{''.join('<option>'+x+'</option>' for x in sorted(fact['Content Type'].unique()))}</select></label><label>Reaction sentiment<select id="sentiment"><option value="all">All sentiments</option>{''.join('<option>'+x+'</option>' for x in sorted(fact['Sentiment'].unique()))}</select></label></div>
<div class="kpis"><div class="kpi"><b>Weighted popularity</b><strong id="points">–</strong><small>Sum of reaction-type scores</small></div><div class="kpi"><b>Reaction events</b><strong id="events">–</strong><small>Valid records after cleaning</small></div><div class="kpi"><b>Distinct posts</b><strong id="posts">–</strong><small>Posts with ≥1 retained reaction</small></div><div class="kpi"><b>Active categories</b><strong id="categories">–</strong><small>Categories in filtered records</small></div></div>
<div class="chartgrid"><div class="panel"><h3>Top categories by popularity</h3><p class="sub">Sum of weighted scores, not unique users</p><div class="chart" id="cat-chart"></div></div><div class="panel"><h3>Monthly popularity trend</h3><p class="sub">Reaction timestamp grouped by YYYY-MM</p><div class="chart" id="month-chart"></div></div><div class="panel"><h3>Popularity by media format</h3><p class="sub">Compare photo, video, GIF and audio contributions</p><div class="chart" id="format-chart"></div></div><div class="panel"><h3>Reaction sentiment mix</h3><p class="sub">Mapped from predefined reaction-type labels</p><div class="chart" id="sent-chart"></div></div></div>
<div class="bottom"><div class="insight"><h3>Executive recommendations</h3><ul><li>Run controlled pilots for the highest-scoring content categories rather than assuming high totals prove superior engagement.</li><li>Compare formats within categories using impressions and posting windows before allocating marketing budgets.</li><li>Introduce reliable event IDs, join-integrity checks, and audience-denominator metrics to strengthen analytics governance.</li></ul></div><div class="insight"><h3>Top five categories</h3><p class="sub">Combined share of popularity points: <b id="top5share">–</b></p><table class="tbl"><thead><tr><th>#</th><th>Category</th><th>Points</th><th>Events</th></tr></thead><tbody id="top5"></tbody></table></div></div>
<p class="foot">DATA ORIGIN: Synthetic reproducible dataset generated for portfolio teaching. This is not the official Accenture/Forage dataset, an Accenture client report, or evidence of programme completion. Rankings change with report filters. File contains an embedded copy of Plotly.js and runs offline.</p></div><script>{script}</script></body></html>'''
out=ROOT/'Social_Buzz_Interactive_Dashboard.html';out.write_text(html,encoding='utf8')
print(out,out.stat().st_size)
