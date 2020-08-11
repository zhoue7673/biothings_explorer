#!/usr/bin/env python
# coding: utf-8

# In[1]:


from biothings_explorer.user_query_dispatcher import SingleEdgeQueryDispatcher


# In[2]:


import requests


# In[3]:


def map_curie_to_cohd(curie):
    curie=str(curie).replace(":","%3A",1)
    url='http://cohd.io/api/omop/xrefToOMOP?curie={curie}&distance=1'.replace("{curie}",curie)
    try:
        res = requests.get(url).json()
    except:
        return []
    if "results" in res and len(res["results"]) > 0:
        return list(set([item["omop_standard_concept_id"] for item in res["results"]]))
    else:
        return []


# In[4]:


def find_coocurence(concept1,concept2):
    url = "http://cohd.io/api/frequencies/pairedConceptFreq?dataset_id=1&q={concept1}%2C{concept2}".replace("{concept1}",str(concept1)).replace("{concept2}",str(concept2))
    try:
        res = requests.get(url).json()
    except:
        return 0
    if "results" in res and len(res["results"]) > 0:
        return res["results"][0]["concept_frequency"]
    else:
        return 0


# In[5]:


def find_omops(curie1,curie2):
    from itertools import chain
    OMOPlist1=map_curie_to_cohd(curie1)
    OMOPlist2=map_curie_to_cohd(curie2)
    cf = []
    range1 = len(OMOPlist1)
    range2 = len(OMOPlist2)
    for i in range(range1):
        cf.append([])
        for j in range(range2):
            OMOP1=OMOPlist1[i]
            OMOP2=OMOPlist2[j]
            cf[i].append(find_coocurence(OMOP1,OMOP2))
    cf = list(chain.from_iterable(cf))
    if not len(cf):
        return 0
    else:
        maxcf = max(cf)
        return maxcf


# In[6]:


def graph_omop(graph):
    IDa = ''
    IDb = ''
    for a in graph.nodes():
        if graph.nodes[a]['level'] == 1:
            input1 = a
            break
    if 'UMLS' in graph.nodes[input1]['equivalent_ids']:
        IDa='UMLS:'+str(graph.nodes[input1]['equivalent_ids']['UMLS']).strip("['']")
    elif 'MESH' in graph.nodes[input1]['equivalent_ids']:
        curie1 = 'MESH'
        IDa='MESH:'+str(graph.nodes[input1]['equivalent_ids']['MESH']).strip("['']")
    elif 'DOID' in graph.nodes[input1]['equivalent_ids']:
        curie1 = 'DOID'
        IDa='DOID:'+str(graph.nodes[input1]['equivalent_ids']['DOID']).strip("['']")
    for b in graph.nodes():
        if graph.nodes[b]['level'] == 2:
            if 'UMLS' in graph.nodes[b]['equivalent_ids']:
                IDb='UMLS:'+str(graph.nodes[b]['equivalent_ids']['UMLS']).strip("['']")
            elif 'MESH' in graph.nodes[b]['equivalent_ids']:
                IDb='MESH:'+str(graph.nodes[b]['equivalent_ids']['MESH']).strip("['']")
            elif 'DOID' in graph.nodes[b]['equivalent_ids']:
                IDb='DOID:'+str(graph.nodes[b]['equivalent_ids']['DOID']).strip("['']")
            cf = find_omops(IDa,IDb)
            if cf > 0:
                if 'filter' not in graph.nodes[input1]:
                    graph.nodes[input1]['filter'] = {b:cf}
                else:
                    graph.nodes[input1]['filter'].update({b:cf})
    return graph

