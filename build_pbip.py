"""Author a Power BI PBIP source project using public PBIR + TMDL formats.
Static JSON/TMDL checks are performed; opening in Desktop remains unverified in Linux.
"""
from pathlib import Path
import json,uuid,base64,zlib,hashlib
ROOT=Path(__file__).parent
PROJECT=ROOT/'powerbi'/'Social_Buzz_Dashboard'
REPORT=PROJECT/'Social_Buzz_Dashboard.Report'
MODEL=PROJECT/'Social_Buzz_Dashboard.SemanticModel'
SM=MODEL/'definition'; TB=SM/'tables'; RD=REPORT/'definition'; PAGES=RD/'pages'
for d in (TB,PAGES):d.mkdir(parents=True,exist_ok=True)
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/'
def j(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def id20(key):return hashlib.sha1(key.encode()).hexdigest()[:20]
def platform(item_type,display):
    return {'$schema':SCHEMA+'gitIntegration/platformProperties/2.0.0/schema.json',
            'metadata':{'type':item_type,'displayName':display},
            'config':{'version':'2.0','logicalId':str(uuid.uuid5(uuid.NAMESPACE_DNS,'example.socialbuzz.'+item_type))}}

j(PROJECT/'Social_Buzz_Dashboard.pbip',{
    '$schema':SCHEMA+'pbip/pbipProperties/1.0.0/schema.json',
    'version':'1.0','artifacts':[{'report':{'path':'Social_Buzz_Dashboard.Report'}}],
    'settings':{'enableAutoRecovery':True}})
(PROJECT/'.gitignore').write_text('**/.pbi/localSettings.json\n**/.pbi/cache.abf\n',encoding='utf8')
j(REPORT/'.platform',platform('Report','Social Buzz Analytics'))
j(MODEL/'.platform',platform('SemanticModel','Social Buzz Analytics Model'))
j(REPORT/'definition.pbir',{'$schema':SCHEMA+'item/report/definitionProperties/2.0.0/schema.json',
    'version':'4.0','datasetReference':{'byPath':{'path':'../Social_Buzz_Dashboard.SemanticModel'}}})
j(MODEL/'definition.pbism',{'$schema':SCHEMA+'item/semanticModel/definitionProperties/1.0.0/schema.json',
    'version':'4.0','settings':{}})
j(RD/'version.json',{'$schema':SCHEMA+'item/report/definition/versionMetadata/1.0.0/schema.json',
    'version':'2.0.0'})
# Explicitly supply a real base-theme resource; this minimal Theme JSON is for local source authoring.
base='CY26SU02'
theme={"name":base,"dataColors":["#0F766E","#3B82F6","#F59E0B","#8B5CF6","#DC2626","#64748B","#22C55E","#EC4899"],
       "background":"#FFFFFF","foreground":"#1E293B","tableAccent":"#0F766E"}
j(REPORT/'StaticResources'/'SharedResources'/'BaseThemes'/f'{base}.json',theme)
j(RD/'report.json',{'$schema':SCHEMA+'item/report/definition/report/3.2.0/schema.json',
    'themeCollection':{'baseTheme':{'name':base,'reportVersionAtImport':{'visual':'2.6.0','report':'3.1.0','page':'2.3.0'},'type':'SharedResources'}},
    'resourcePackages':[{'name':'SharedResources','type':'SharedResources','items':[{'name':base,'path':f'BaseThemes/{base}.json','type':'BaseTheme'}]}],
    'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized',
                'defaultDrillFilterOtherVisuals':True,'allowChangeFilterTypes':True,'useEnhancedTooltips':True}})

# Self-contained data source. M decompresses the CSV in memory; no Windows file paths, no credentials.
source=(ROOT/'data/processed/fact_reactions.csv').read_bytes()
co=zlib.compressobj(level=9,wbits=-15)
comp=co.compress(source)+co.flush()
encoded=base64.b64encode(comp).decode('ascii')
assert zlib.decompress(comp,-15)==source

(SM/'database.tmdl').write_text('database SocialBuzz\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n\tlanguage: 1033\n',encoding='utf8')
(SM/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\nref table Reactions\n',encoding='utf8')
cols=[('Reaction ID','string'),('Content ID','string'),('Category','string'),('Content Type','string'),('Reaction Type','string'),('Sentiment','string'),('Score','double'),('Datetime','dateTime'),('Date','string'),('Month','string'),('Month Name','string'),('Year','int64')]
q=lambda c:"'"+c+"'" if ' ' in c else c
lines=['table Reactions','']
measures=[('Total Popularity','SUM(Reactions[Score])','#,##0'),
          ('Reaction Events','COUNTROWS(Reactions)','#,##0'),
          ('Unique Posts','DISTINCTCOUNT(Reactions[Content ID])','#,##0'),
          ('Distinct Categories','DISTINCTCOUNT(Reactions[Category])','#,##0'),
          ('Points per Reaction','DIVIDE([Total Popularity], [Reaction Events])','0.0'),
          ('Points per Post','DIVIDE([Total Popularity], [Unique Posts])','#,##0.0'),
          ('Positive Reactions','CALCULATE([Reaction Events], Reactions[Sentiment] = "positive")','#,##0'),
          ('Positive Share','DIVIDE([Positive Reactions], [Reaction Events])','0.0%')]
for name,dax,fmt in measures:
    lines+= [f'\tmeasure {q(name)} = {dax}',f'\t\tformatString: {fmt}','']
for name,t in cols:
    lines += [f'\tcolumn {q(name)}',f'\t\tdataType: {t}', f'\t\tsourceColumn: {name}', '\t\tsummarizeBy: none','']
lines += [ '\tpartition Reactions = m','\t\tmode: import','\t\tsource =',
           '\t\t\tlet',
           f'\t\t\t\tCompressed = Binary.FromText("{encoded}", BinaryEncoding.Base64),',
           '\t\t\t\tRawBytes = Binary.Decompress(Compressed, Compression.Deflate),',
           '\t\t\t\tParsed = Csv.Document(RawBytes, [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
           '\t\t\t\tHeaders = Table.PromoteHeaders(Parsed, [PromoteAllScalars=true]),',
           '\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {',
           '\t\t\t\t\t{"Reaction ID", type text}, {"Content ID", type text}, {"Category", type text},',
           '\t\t\t\t\t{"Content Type", type text}, {"Reaction Type", type text}, {"Sentiment", type text},',
           '\t\t\t\t\t{"Score", type number}, {"Datetime", type datetime}, {"Date", type text},',
           '\t\t\t\t\t{"Month", type text}, {"Month Name", type text}, {"Year", Int64.Type}',
           '\t\t\t\t}, "en-US")',
           '\t\t\tin',
           '\t\t\t\tTyped','']
(TB/'Reactions.tmdl').write_text('\n'.join(lines),encoding='utf8')

# PBIR source based on Microsoft's documented queryState/visualContainer structure.
VISSCHEMA=SCHEMA+'item/report/definition/visualContainer/2.7.0/schema.json'
PAGESCHEMA=SCHEMA+'item/report/definition/page/2.1.0/schema.json'
def cf(prop):return {'field':{'Column':{'Expression':{'SourceRef':{'Entity':'Reactions'}},'Property':prop}},'queryRef':f'Reactions.{prop}','nativeQueryRef':prop}
def mf(prop):return {'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'Reactions'}},'Property':prop}},'queryRef':f'Reactions.{prop}','nativeQueryRef':prop}
def literal(x):return {'expr':{'Literal':{'Value':x}}}
def title_object(title):
    return {'title':[{'properties':{'show':literal('true'),'text':literal("'"+title.replace("'","''")+"'"),
                                   'fontSize':literal('13D')}}],
            'background':[{'properties':{'show':literal('true'),
                                         'color':{'solid':{'color':literal("'#FFFFFF'")}},
                                         'transparency':literal('0D')}}]}

def visual(key,x,y,w,h,typ,qs,title):
    body={'visualType':typ,'drillFilterOtherVisuals':True}
    if qs:body['query']={'queryState':qs}
    body['visualContainerObjects']=title_object(title)
    return {'$schema':VISSCHEMA,'name':id20(key),'position':{'x':x,'y':y,'z':1000,'height':h,'width':w,'tabOrder':1000},'visual':body}

def card(key,x,y,title,measure):return visual(key,x,y,276,112,'cardVisual',{'Data':{'projections':[mf(measure)]}},title)
def bar(key,x,y,w,h,title,col,measure,typ='clusteredBarChart'):
    return visual(key,x,y,w,h,typ,{'Category':{'projections':[cf(col)]},'Y':{'projections':[mf(measure)]}},title)
def donut(key,x,y,w,h,title,col,measure):
    return visual(key,x,y,w,h,'donutChart',{'Category':{'projections':[cf(col)]},'Y':{'projections':[mf(measure)]}},title)
def slicer(key,x,y,w,h,title,col):
    return visual(key,x,y,w,h,'slicer',{'Values':{'projections':[cf(col)]}},title)
def write_page(key,title,visuals):
    pageid=id20('page'+key);pdir=PAGES/pageid
    j(pdir/'page.json',{'$schema':PAGESCHEMA,'name':pageid,'displayName':title,'displayOption':'FitToPage','height':720,'width':1280})
    for v in visuals:j(pdir/'visuals'/v['name']/'visual.json',v)
    return pageid

page_one=write_page('overview','01 · Executive Overview',[
    card('p1kpi1',24,20,'Aggregate popularity points','Total Popularity'),
    card('p1kpi2',316,20,'Recorded reaction events','Reaction Events'),
    card('p1kpi3',608,20,'Distinct content posts','Unique Posts'),
    card('p1kpi4',900,20,'Content categories','Distinct Categories'),
    bar('p1cat',24,154,598,325,'Category popularity • weighted score','Category','Total Popularity'),
    bar('p1month',646,154,608,325,'Monthly engagement points','Month','Total Popularity','lineChart'),
    donut('p1sent',24,500,360,197,'Sentiment composition','Sentiment','Reaction Events'),
    bar('p1formats',408,500,543,197,'Popularity by media format','Content Type','Total Popularity','clusteredColumnChart'),
    slicer('p1filter',972,500,282,197,'Filter category','Category')
])
page_two=write_page('deepdive','02 · Content Deep Dive',[
    card('p2kpi1',24,24,'Score per post','Points per Post'),
    card('p2kpi2',316,24,'Points per reaction','Points per Reaction'),
    card('p2kpi3',608,24,'Positive reaction share','Positive Share'),
    slicer('p2filter',914,24,340,112,'Select content format','Content Type'),
    bar('p2avg',24,170,600,475,'Popularity points per distinct post','Category','Points per Post'),
    bar('p2count',650,170,600,475,'Reaction event counts by category','Category','Reaction Events'),
])
j(PAGES/'pages.json',{'$schema':SCHEMA+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':[page_one,page_two],'activePageName':page_one})

# Structural sanity checks; this is NOT a replacement for Desktop render/refresh testing.
for p in PROJECT.rglob('*.json'):
    json.loads(p.read_text(encoding='utf8'))
assert sum(1 for _ in (PAGES/page_one/'visuals').glob('*/visual.json'))==9
assert sum(1 for _ in (PAGES/page_two/'visuals').glob('*/visual.json'))==6
assert (TB/'Reactions.tmdl').stat().st_size>100000
print('Generated PBIP source in',PROJECT)
print('Compressed embedded data',len(comp),'bytes; source rows',source.count(b'\n')-1)
