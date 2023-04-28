import sys
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.flow import edmonds_karp

INF_VALUE=300
VERBOSE=False

# Dado un grafo inicial direccionado, sin ejes paralelos, 
# con ejes con:
#   0 < capacidad (si es 0 se toma como que no existe el eje)
#   0 <= limite inferior <= capacidad
#
# Emplea Edmonds-Karp para encontrar un camino viable de flujo 
# que cumpla con los limites inferiores y que además sea máximo.
# 
# Devuelve (False, mensaje_de_error, None) si no existe flujo posible
# o (True, flujo_máximo, lista_flujos) si existe un flujo máximo.
# siendo lista_flujos la cantidad de flujo por eje
#
def flujoMaximo(grafo):
    
    n = len(grafo)

    # Creamos un nuevo grafo G' que tendrá
    # 2 vértices más que G: nuevos nodos fuente y sumidero.
    # les daremos el anteultimo y último lugar, respectivamente.
    # s' = n, t' = n+1
    grafoPrima = grafo.copy(as_view=False)
    
    # d es todo el flujo que sale de s' en G' 
    # d' es todo el flujo que entra a t' en G'
    d=0
    d_prima = 0

    # Por cada vértice V en G, calculamos:
    # 
    # La suma de los límites inferiores 
    # de los ejes entrantes a V, y asignamos 
    # esa suma como la capacidad de el nuevo eje (s', v).
    #
    # La suma de los límites inferiores 
    # de los ejes salientes de V, y asignamos
    # esa suma como la capacidad de el nuevo eje (v, t')
    #
    demandas_ok = False
    demandas_restadas = []
    for nodo in grafo.nodes:
        if nodo == 0 or nodo == (n-1):
            continue
        
        entrante = 0
        saliente = 0
        for u, v, attr in grafo.edges(data=True): 
            if attr['demand'] > 0 and not demandas_ok: 
                demandas_restadas.append((u, v, attr['demand']))
                demandas_ok = True
            if v == nodo: 
                entrante += attr['demand']
            if u == nodo: 
                saliente += attr['demand']

        grafoPrima.add_edge(n, nodo, capacity=entrante)
        grafoPrima.add_edge(nodo, n+1, capacity=saliente)

        d += entrante
        d_prima += saliente
    
    # Eliminamos todos los límites inferiores
    # de los ejes en el nuevo Grafo. 
    # La nueva capacidad de los ejes será la diferencia
    # entre su capacidad y su límite inferior. 
    for u, v, attr in grafoPrima.edges(data=True): 
        
        if u == n or u == n + 1:
            continue
        if v == n or v == n + 1:
            continue
        attr['capacity'] -= attr['demand']
        
        del attr['demand']
    
    # Agregamos un eje desde t hacia s, que 
    # tendrá capacidad "infinita", es decir,
    # un valor suficientemente grande como para 
    # no limitar flujo a través de él
    grafoPrima.add_edge(n-1, 0)
    
    if VERBOSE:
        imprimir_grafo(grafoPrima, n)

    # Utilizamos la librería de Networkx para calcular 
    # el grafo residual del flujo máximo posible a través
    # de G', con el algoritmo Edmonds-Karp 
    # 
    # Si el flujo resultante es distinto a d o d', 
    # no es un flujo saturante, es decir, máximo. 
    # Por lo tanto, no existe solución para G.
    #
    grafoPrimaResidual = edmonds_karp(grafoPrima, n, n+1)
    flujo_prima = grafoPrimaResidual.graph['flow_value']
    if flujo_prima != d or flujo_prima != d_prima: 
        return False, flujo_prima, None
    
    # Eliminamos los nodos s' y t' de G' residual. 
    grafoPrimaResidual.remove_node(n)
    grafoPrimaResidual.remove_node(n+1)

    # Eliminamos los ejes entre s y t en G' residual. 
    grafoPrimaResidual.remove_edge(n-1, 0)
    grafoPrimaResidual.remove_edge(0, n-1)

    # Modificamos las capacidades de los ejes en G' residual. 
    # El nuevo valor será capacidad - flujo. 
    # Guardamos los valores de su flujo para luego agregarlos al 
    # flujo final. Además, le agregamos al flujo guardado
    # el valor de la demanda en G si es que tenía.
    flujos_restados = []
    i = 0
    for u, v, attr in grafoPrimaResidual.edges(data=True): 
        flow_tot = 0
        if i < len(demandas_restadas):
            uD, vD, demanda = demandas_restadas[i]

        if u == uD and v == vD:
            flow_tot += demanda
            i += 1

        if attr['flow'] >= 0: 
            attr['capacity'] -= attr['flow']
            flow_tot += attr['flow']
            flujos_restados.append((u, v, flow_tot))
        
    # Con el G' residual modificado, seteamos un valor 
    # "infinito" arbitrario, y aplicamos el algoritmo 
    # Edmonds-Karp con la particularidad de que le 
    # brindamos por parámetro el grafo residual, y 
    # lo único que hace el algoritmo es buscar 
    # iterativamente los "augmented path" para 
    # encontrar el flujo máximo.
    #
    grafoPrimaResidual.graph['inf'] = INF_VALUE
    grafoResidual = edmonds_karp(grafo, 0, n-1, residual=grafoPrimaResidual)

    if VERBOSE:
        imprimir_grafo_flujo_maximo(grafo, grafoResidual, n)
    

    flujos = []
    lista_ejes = list(grafoResidual.edges(data=True))
    i = 0
    j = 0
    k = 0
    flujo_agregado = 0
    
    for u, v, attr in grafo.edges(data=True):
        
        if i >= len(lista_ejes):
            break
            
        flujo_actual = 0
        if j < len(flujos_restados):
            uf, vf, flowf = flujos_restados[j]
            if uf == 0: 
                flujo_agregado += flowf

        u1, v1, attr1 = lista_ejes[i]
        
        while u != u1 or v != v1 or attr1['flow'] < 0:
            i += 1
            u1, v1, attr1 = lista_ejes[i]
        
        if uf == u and vf == v: 
            flujo_actual += flowf
            j += 1
        
        flujo_actual += attr1['flow']
        flujos.append(flujo_actual)

    return True, grafoResidual.graph['flow_value'] + flujo_agregado, flujos


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
    
    if VERBOSE:
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

def imprimir_grafo_flujo_maximo(gr, rgr, n):

    #nx.draw(gr, pos=nx.shell_layout(gr), with_labels=True, node_color=colors)
    #plt.show()

    eje1 = list(gr.edges(data=True))
    j=0
    for eje in rgr.edges(data=True): 
        if j >= len(eje1):
            pass
        elif eje1[j][0] == eje[0] and eje1[j][1] == eje[1]:
            eje1[j][2]['capacity'] = eje[2]['capacity']
            if eje[2]['flow'] > 0:
                eje1[j][2]['flow'] = eje[2]['flow']
            print(eje1[j])
            j += 1

    # set the position according to column (x-coord)
    
    colors = ["red"] * len(gr)
    pos = {}
    node_labels = {}

    for i, node in enumerate(list(gr.nodes)): 

        if node == 0: 
            node_labels.update({node: 's'})
        elif node == n-1:
            node_labels.update({node: 't'})
        else:
            node_labels.update({node: node})

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
        
    i = 0
    edge_labels={}
    for edge in gr.edges(data=True): 
        string = ""

        if len(edge[2]) == 3:
            string += str(edge[2]['flow'])
            i += 1
        else:
            string += str(0)

        string += '/' + str(edge[2]['capacity'])
        edge_labels.update({(edge[0], edge[1]): string})

    plt.rcParams["figure.figsize"] = (15,8)
    nx.draw_networkx(gr, pos, node_color=colors, labels=node_labels)
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
        edge_labels.update({(edge[0], edge[1]): str(edge[2]['capacity'])})
    
    node_labels = {}
    for node in gr.nodes: 
        if node == 0: 
            node_labels.update({node: 's'})
            continue
        elif node == n-1:
            node_labels.update({node: 't'})
            continue

        node_labels.update({node: node})

    
    print("CANT NODOS: ", len(gr))
    for edge in gr.edges(data=True):
        print(edge)
    """ 
    # Get the edge labels and round them to 3 decimal places
    # for more clarity while drawing
    edge_labels = dict([((u,v), round(d['capacity'], 3))
                for u,v,d in gr.edges(data=True)]) 
    """

    # Set the figure size
    plt.figure(figsize=(20,12))
    # Draw edge labels and graph
    nx.draw_networkx_edge_labels(gr,pos,edge_labels=edge_labels,
                                label_pos=0.15, font_size=10)
    nx.draw_networkx_labels(gr,pos,labels=node_labels,
                                font_size=15)
    nx.draw(gr, pos,
            connectionstyle='arc3, rad = 0.15',
            node_size=400,node_color=colors)

    plt.show()

def main(argv):
    if len(argv) == 1:
        with open(argv[0]) as f: 
            grafo = parsearGrafo(f.readlines())    
        res = flujoMaximo(grafo)
        print(res[1])
        for item in res[2]:
            print(item)
    elif len(argv) >= 2:
        print("Sólo puede pasar 1 parámetro.")
        sys.exit(1)
    else:
        print("Por favor indique el path al archivo de red de flujo.")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

