from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).parent
D=ROOT/'data/processed'
cat=pd.read_csv(D/'category_summary.csv').head(8)
mo=pd.read_csv(D/'monthly_trend.csv')
sent=pd.read_csv(D/'sentiment_summary.csv')
formats=pd.read_csv(D/'format_summary.csv')
plt.rcParams['font.family']='DejaVu Sans'
fig=plt.figure(figsize=(16,10),facecolor='#F4F7FA')
fig.text(.04,.955,'SOCIAL / BUZZ',color='#0C2735',fontsize=17,weight='bold')
fig.text(.04,.92,'Executive Analytics  |  Content Popularity & Engagement',color='#192F3F',fontsize=22,weight='bold')
fig.text(.04,.89,'SYNTHETIC PRACTICE DATA  ·  Accenture–Forage-inspired independent portfolio project',fontsize=11,color='#738194')
labels=[('POPULARITY POINTS','1,252,226'),('REACTION EVENTS','24,986'),('CATEGORY COUNT','16'),('TOP FIVE SCORE SHARE','62.9%')]
for i,(lab,val) in enumerate(labels):
    x=.04+i*.239
    patch=FancyBboxPatch((x,.77),.218,.091,boxstyle='round,pad=0.003,rounding_size=.012',transform=fig.transFigure,facecolor='white',edgecolor='#E5EAF1',linewidth=1)
    fig.patches.append(patch)
    fig.text(x+.015,.827,lab,fontsize=9,color='#7B8798',weight='bold')
    fig.text(x+.015,.79,val,fontsize=22,color='#183146',weight='bold')

def panel(bounds):
    ax=fig.add_axes(bounds,facecolor='white')
    for spine in ax.spines.values():spine.set_visible(False)
    ax.tick_params(colors='#566679',labelsize=10,length=0)
    return ax
ax1=panel([.065,.405,.41,.31]);ax1.set_title('Top categories by total popularity',loc='left',pad=14,color='#1D3444',weight='bold',fontsize=13)
ax1.barh(cat.iloc[::-1]['category'],cat.iloc[::-1]['popularity_score']/1000,color='#0F766E',height=.63)
ax1.grid(axis='x',alpha=.13);ax1.set_axisbelow(True);ax1.set_xlabel('Weighted points (thousands)',color='#556374')
ax2=panel([.55,.405,.405,.31]);ax2.set_title('Monthly popularity trend',loc='left',pad=14,color='#1D3444',weight='bold',fontsize=13)
ax2.plot(range(len(mo)),mo['popularity_score']/1000,color='#3268C8',linewidth=2.7,marker='o',markersize=4.8)
ax2.set_xticks(range(0,12,2),mo.iloc[range(0,12,2)]['month'].str[-2:].tolist());ax2.set_xlabel('Month of 2025',color='#556374');ax2.grid(alpha=.15);ax2.set_axisbelow(True);ax2.set_ylabel('Points (thousands)',color='#556374')
ax3=panel([.065,.085,.41,.235]);ax3.set_title('Weighted points by content format',loc='left',pad=11,color='#1D3444',weight='bold',fontsize=13)
ax3.bar(formats['content_type'],formats['popularity_score']/1000,color=['#6366F1','#0F766E','#F59E0B','#94A3B8'],width=.55)
ax3.grid(axis='y',alpha=.13);ax3.set_axisbelow(True);ax3.set_ylabel('Points (thousands)',color='#556374')
ax4=panel([.61,.095,.28,.215]);ax4.set_title('Sentiment event mix',loc='left',pad=11,color='#1D3444',weight='bold',fontsize=13)
colors=[{'positive':'#0F766E','negative':'#DC2626','neutral':'#9CA3AF'}.get(v,'#6366F1') for v in sent['sentiment']]
ax4.pie(sent['reactions'],colors=colors,startangle=90,wedgeprops={'width':.42,'edgecolor':'white'},pctdistance=.8)
fig.legend([plt.Line2D([0],[0],color=c,marker='o',lw=0) for c in colors],sent['sentiment'],loc='lower right',bbox_to_anchor=(.978,.15),frameon=False,fontsize=10)
fig.text(.04,.028,'DATA PROVENANCE: Deterministically generated for teaching; NOT official Social Buzz or Accenture results.',color='#7C899A',fontsize=9)
fig.savefig(ROOT/'Social_Buzz_Dashboard_Preview.png',dpi=160,bbox_inches='tight',facecolor=fig.get_facecolor())
print('Created',ROOT/'Social_Buzz_Dashboard_Preview.png')
