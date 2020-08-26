from biothings_explorer.user_query_dispatcher import SingleEdgeQueryDispatcher
import requests

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
        
def find_curie(node,graph):
    curie_list = []
    validIDs = ['UMLS','DOID','MESH']
    for ID in validIDs:
        if ID in graph.nodes[node]['equivalent_ids']:
            for i in range(len(graph.nodes[node]['equivalent_ids'][ID])):
                value = graph.nodes[node]['equivalent_ids'][ID][i]
                if ID == 'DOID':
                    curie_list.append(value)
                else:
                    curie_list.append(ID+":"+value)
    return curie_list
    
def graph_omop(graph):
    for a in graph.nodes():
        if graph.nodes[a]['level'] == 1:
            input1 = a
            break
    IDa = find_curie(input1,graph)
    for b in graph.nodes():
        if graph.nodes[b]['level'] == 2:
            noCF=True
            IDb=find_curie(b,graph)
            for x in IDa:
                for y in IDb:
                    if noCF:
                        cf = find_omops(x,y)
                        if cf > 0:
                            graph.nodes[b]['filter'] = cf
                            noCF=False
                    else:
                        break
                        break
    return graph
