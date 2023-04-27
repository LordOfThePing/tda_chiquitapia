import sys
import networkx as nx
from networkx.algorithms.flow import edmonds_karp
import matplotlib.pyplot as plt
import pylab
plt.rcParams['interactive'] == True

INF_VALUE=300

def edmondsKarp(source, sink, rGraph): 
  
    # This array is filled by BFS and to store path 
    # from source to destination 
    parent = [-1] * len(rGraph[0]) 
  
    max_flow = 0 
    # Augment the flow while there is path from source 
    # to sink 
    while bfs(source, sink, rGraph, parent): 
        
        
        # Find minimum residual capacity of the edges 
        # along the path filled by BFS. Or we can say 
        # find the maximum flow through the path found. 
        path_flow = float("Inf") 
        s = sink 
        while(s !=  source): 
            path_flow = min(path_flow, rGraph[parent[s]][s]) 
            s = parent[s] 
  
        # Add path flow to overall flow 
        max_flow +=  path_flow 
  
        # update residual capacities of the edges and 
        # reverse edges along the path 
        v = sink 
        while(v !=  source): 
            u = parent[v] 
            rGraph[u][v] -= path_flow 
            rGraph[v][u] += path_flow 
            v = parent[v] 
  
    return max_flow 
  
# Returns true if there is a path from source 's' to sink 
# 't' in residual graph. Also fills parent[] to store the 
# path 
def bfs(source, sink, rGraph, parent): 
  
    # Create a visited array and mark all vertices as not 
    # visited 
    visited = [False] * len(rGraph[0])
  
    # Create a queue, enqueue source vertex and mark 
    # source vertex as visited 
    queue = [] 
    queue.append(source) 
    visited[source] = True
  
    # Standard BFS Loop 
    while queue: 
  
        #Dequeue a vertex from queue and print it 
        u = queue.pop(0) 
  
        # Get all adjacent vertices of the dequeued vertex u 
        # If a adjacent has not been visited, then mark it 
        # visited and enqueue it 
        for ind, val in enumerate(rGraph[u]): 
            if visited[ind] == False and val > 0 : 
                queue.append(ind) 
                visited[ind] = True
                parent[ind] = u 
  
    # If we reached sink in BFS starting from source, then 
    # return true, else false 
    return True if visited[sink] else False

def flujoMaximo(grafo):
    
    n = len(grafo)

    # G' tendrá 2 vértices más que G: la fuente y el sumidero
    # A la nueva fuente y sumidero le daremos
    # el anteultimo y último lugar, respectivamente.
    # fuente = n, sumidero = n+1
    grafoPrima = grafo.copy(as_view=False)
    d=0
    d_prima = 0
    # No contamos a la fuente ni al sumidero 
    for nodo in grafo.nodes:
        if nodo == 0 or nodo == (n-1):
            continue
        
        entrante = 0
        saliente = 0
        for eje in grafo.edges(data=True): 
            if eje[1] == nodo: 
                entrante += eje[2]['demand']
            if eje[0] == nodo: 
                saliente += eje[2]['demand']

        grafoPrima.add_edge(n, nodo, capacity=entrante)
        grafoPrima.add_edge(nodo, n+1, capacity=saliente)

        d += entrante
        d_prima += saliente
    
    for g in grafoPrima.edges(data=True): 
        # En el nuevo grafo no habrá demandas
        if g[0] == n or g[0] == n + 1:
            continue
        if g[1] == n or g[1] == n + 1:
            continue
        g[2]['capacity'] -= g[2]['demand']
        
        del g[2]['demand']
    
    grafoPrima.add_edge(n-1, 0)

    if d != d_prima: 
        return False, "d != d prima"
    
    imprimir_grafo(grafoPrima, n)
    grafoPrimaResidual = edmonds_karp(grafoPrima, n, n+1)
    f = grafoPrimaResidual.graph['flow_value']
    if f != d: 
        return False, f
    

    grafoPrimaResidual.remove_node(n)
    grafoPrimaResidual.remove_node(n+1)
    grafoPrimaResidual.remove_edge(n-1, 0)
    grafoPrimaResidual.remove_edge(0, n-1)
    imprimir_grafo_residual(grafoPrimaResidual, n)

    
    for eje2 in grafo.edges(data=True): 
        for eje1 in grafoPrimaResidual.edges(data=True): 
            if eje1[0] == eje2[0] and eje1[1] == eje2[1] : 
                eje1[2]['capacity'] = eje2[2]['capacity'] - eje1[2]['flow']
            if eje1[0] == eje2[1] and eje1[1] == eje2[0]:
                eje1[2]['capacity'] = eje1[2]['flow'] - eje2[2]['demand']



    grafoResidual = edmonds_karp(grafo, 0, n-1, grafoPrimaResidual)

    return True, grafoResidual.graph['flow_value']


"""
    rGrafo = [[0] * len(rGrafoCapacidades) ] * len(rGrafoCapacidades) 
    for i in range(0, len(rGrafo)):
        for j in range(0, len(rGrafo)):
            if i != len(rGrafo) and j != 0:
                if rGrafoPrima[i+1][j+1] > 0: 
                    rGrafo[i][j] = rGrafoCapacidades[i][j] - rGrafoPrima[i+1][j+1]
                elif rGrafoPrima[i+1][j+1] < 0: 
                    rGrafo[i][j] = rGrafoPrima[j+1][i+1] - rGrafoDemandas[j+1][i+1]

    return True, edmondsKarp(rGrafo)
"""
def parsearGrafo(lines):
    
    grafo = nx.DiGraph()
    col = []
    n = 0
    for line in lines: 
        item = line.split(',')
        if item[0] != 'S' and item[0] != 'T':
            item[0] = int(item[0]) 
            if item[0] > n:
                n = item[0]
        if item[1] != 'S' and item[1] != 'T':
            item[1] = int(item[1])
            if item[1] > n:
                n = item[1]
        item[2] = int(item[2])
        item[3] = int(item[3])
        col.append(item)
    

    for c in col: 
        if c[0] == 'S':
            c[0] = 0
        elif c[1] == 'S':
            c[1] = 0
        elif c[0] == 'T':
            c[0] = n+1
        elif c[1] == 'T':
            c[1] = n+1
        grafo.add_edge(c[0], c[1], capacity=c[2], demand=c[3])
    
    print("GRAFO LEÍDO:")
    imprimir_grafo(grafo, len(grafo))

    return grafo

def imprimir_grafo(gr, n):

    #nx.draw(gr, pos=nx.shell_layout(gr), with_labels=True, node_color=colors)
    #plt.show()

    # set the position according to column (x-coord)
    
    colors = ["red"] * len(gr)
    pos = {}
    for i, node in enumerate(list(gr.nodes)): 

        alt = 0
        if node%2 == 0:
            alt = 0.5
        else: 
            alt = -0.5

        if node == 0:
            colors[i] = "lightgreen"
            pos.update({node: (0, 0)})
        elif node == n-1:
            colors[i] = "lightgreen"
            pos.update({node: (n, 0)})
        elif i >= n:
            if i == (len(gr)-1):
                colors[i] = "lightblue"
                pos.update({node: (n/2, 1)})
            else: 
                colors[i] = "lightblue"
                pos.update({node: (n/2, -1)})
        else: 
            pos.update({node: (i, 0+alt)})
        
    edge_labels={}
    for edge in gr.edges(data=True): 
        string = ""
        if len(edge[2]) == 2:
            string += str(edge[2]['demand']) + '/'
        if len(edge[2]) == 0: 
            string += 'inf'
            edge_labels.update({(edge[0], edge[1]): string})
        else:
            string += str(edge[2]['capacity'])
            edge_labels.update({(edge[0], edge[1]): string})

    plt.rcParams["figure.figsize"] = (15,8)
    nx.draw_networkx(gr, pos, node_color=colors)
    nx.draw_networkx_edge_labels(gr, pos,font_color='red',
        edge_labels=edge_labels   
    )  
    #plt.show()

    print("CANT NODOS: ", len(gr))
    for edge in gr.edges(data=True):
        print(edge)

    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.show()

def imprimir_grafo_residual(grafo, n):

    #nx.draw(gr, pos=nx.shell_layout(gr), with_labels=True, node_color=colors)
    #plt.show()
    gr = grafo.copy(as_view=False)
    # set the position according to column (x-coord)
    
    colors = ["red"] * len(gr)
    pos = {}
    for i, node in enumerate(list(gr.nodes)): 

        alt = 0
        if node%2 == 0:
            alt = 0.5
        else: 
            alt = -0.5

        if node == 0:
            colors[i] = "lightgreen"
            pos.update({node: (0, 0)})
        elif node == n-1:
            colors[i] = "lightgreen"
            pos.update({node: (n, 0)})
        elif i >= n:
            if i == (len(gr)-1):
                colors[i] = "lightblue"
                pos.update({node: (n/2, 1)})
            else: 
                colors[i] = "lightblue"
                pos.update({node: (n/2, -1)})
        else: 
            pos.update({node: (i, 0+alt)})
        
    edge_labels={}
    for edge in grafo.edges(data=True): 
        if edge[2]['flow'] < 0:
            #gr.remove_edge(edge[0], edge[1])
            continue
        string = ""
        if len(edge[2]) == 2:
            string += str(edge[2]['flow']) + '/'
        if len(edge[2]) == 0: 
            string += 'inf'
            edge_labels.update({(edge[0], edge[1]): string})
        else:
            string += str(edge[2]['capacity'])
            edge_labels.update({(edge[0], edge[1]): string})

    plt.rcParams["figure.figsize"] = (15,8)
    nx.draw_networkx(gr, pos, node_color=colors)
    nx.draw_networkx_edge_labels(gr, pos,font_color='red',
        edge_labels=edge_labels   
    )  
    #plt.show()

    print("CANT NODOS: ", len(gr))
    for edge in gr.edges(data=True):
        print(edge)

    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.show()

def main(argv):
    if len(argv) == 1:
        with open(argv[0]) as f: 
            grafo = parsearGrafo(f.readlines())    
        print(flujoMaximo(grafo))
    elif len(argv) >= 2:
        print("Sólo puede pasar 1 parámetro.")
        sys.exit(1)
    else:
        print("Por favor indique el path al archivo de red de flujo.")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

