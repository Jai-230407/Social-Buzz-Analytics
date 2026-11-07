"""Deterministic *synthetic* Social Buzz records with the same three-table business schema.
Not the original Forage dataset; never represent simulated results as actual client data.
"""
from pathlib import Path
import numpy as np
import pandas as pd

CATEGORIES = ['animals','science','healthy eating','technology','food','travel','fitness','education','culture','cooking','veganism','studying','public speaking','tennis','soccer','dogs']
REACTION_DEFS = [
    ('heart','positive',60),('want','positive',70),('adore','positive',72),
    ('love','positive',65),('super love','positive',75),('like','positive',50),
    ('interested','positive',30),('intrigued','positive',45),('cherish','positive',70),
    ('disgust','negative',0),('hate','negative',5),('dislike','negative',10),
    ('worried','negative',12),('scared','negative',15),('indifferent','neutral',20),('peeking','neutral',35)
]

def make_data(out_dir: Path, seed: int=2026):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    n=1000
    # Stronger content interest for five themes, but not identical engagement weights.
    content_mix=np.array([.13,.105,.105,.10,.09,.065,.06,.055,.05,.05,.045,.04,.035,.035,.025,.025]);content_mix/=content_mix.sum()
    cats=rng.choice(CATEGORIES,n,p=content_mix)
    types=rng.choice(['photo','video','GIF','audio'],n,p=[.49,.30,.17,.04]); ids=[f'SB-{i:05d}' for i in range(1,n+1)]
    content=pd.DataFrame({'Content ID':ids,'User ID':[f'U-{j:04d}' for j in rng.integers(1,851,n)],'Type':types,'Category':cats, 'URL':['https://example.org/content/'+i for i in ids]})
    # Deliberate standardizable strings to exercise actual cleaning.
    content.loc[11,'Category']='"animals"'
    content.loc[22,'Category']=' Technology '
    content.loc[35,'Category']='SCIENCE'
    content.loc[99,'Category']=None
    # User-sensitive fields not needed for business question.
    content.to_csv(out_dir/'Content.csv',index=False)
    reaction_types=pd.DataFrame(REACTION_DEFS,columns=['Type','Sentiment','Score'])
    reaction_types.to_csv(out_dir/'ReactionTypes.csv',index=False)
    # Weighted content popularity and temporal peaks to make plausible, reproducible analysis.
    category_multiplier={'animals':2.2,'science':1.8,'healthy eating':1.68,'technology':1.52,'food':1.42,
                         'travel':1.1,'fitness':1.02,'education':.95,'culture':1.0,'cooking':.86,'veganism':.89,
                         'studying':.78,'public speaking':.73,'tennis':.82,'soccer':.85,'dogs':1.2}
    format_multiplier={'photo':1.25,'video':1.21,'GIF':.85,'audio':.65}
    weights=np.array([category_multiplier.get(str(c).strip().strip('"').lower(),1)*format_multiplier[t] for c,t in zip(cats,types)])
    weights*=rng.lognormal(0,.35,n)
    weights/=weights.sum()
    m=25000
    picks=rng.choice(n,m,p=weights)
    react_probs=np.array([.10,.075,.065,.11,.04,.22,.10,.07,.06,.02,.01,.025,.025,.02,.035,.025]); react_probs/=react_probs.sum()
    reactions=rng.choice(reaction_types['Type'],m,p=react_probs)
    months=rng.choice(np.arange(1,13),m,p=np.array([.07,.075,.08,.08,.085,.09,.08,.075,.085,.105,.10,.075])/1.0)
    # Day capped to 28 to avoid invalid timestamps and simplify QA.
    days=rng.integers(1,29,m); hours=rng.integers(0,24,m)
    dt=pd.to_datetime({'year':np.full(m,2025),'month':months,'day':days,'hour':hours})
    records=pd.DataFrame({'Reaction ID':[f'RX-{i:07d}' for i in range(1,m+1)],
                          'Content ID':np.array(ids)[picks],
                          'User ID':[f'U-{j:04d}' for j in rng.integers(1,4001,m)],
                          'Type':reactions,
                          'Datetime':dt})
    # Deliberate quality issues, counted and exposed transparently in the notebook.
    records.loc[3,'Type']=None
    records.loc[7,'Content ID']='SB-99999' # nonexistent referenced content
    records.loc[16,'Type']='UNKNOWN' # absent reaction type
    records.loc[44,'Datetime']=pd.NaT
    records.loc[210,'Type']=' LIKE ' # normalizable
    records=pd.concat([records, records.iloc[[80]].copy()],ignore_index=True) # duplicate ID
    records.to_csv(out_dir/'Reactions.csv',index=False)
    return {'content':len(content),'reactions':len(records),'reaction_types':len(reaction_types)}
if __name__=='__main__':
    import sys
    print(make_data(Path(sys.argv[1]) if len(sys.argv)>1 else Path('data/raw')))
