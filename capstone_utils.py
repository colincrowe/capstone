import random as rd
import networkx as nx
import matplotlib.pyplot as plt
import csv


class Node():
    adjacent = []
    sample_q = []
    nearest_manhole = None
    timer = 999999999
    def __init__(self, name, status=0, samplable=False):
        self.name = name
        self.status = status
        self.samplable = samplable
    def __str__(self):
        temp = str(self.name) + " | STATUS: " + str(self.status) + " | ADJ: "
        temp2 = " | QUEUE: " + str(self.sample_q)
        return temp + str(self.adjacent) + " | MANHOLE: " + str(self.nearest_manhole) + temp2



def build_weighted_net(file_in):
    nodes = []
    counter = 0
    with open(file_in) as f:
        while(True):
            line = f.readline()
        
            # check for end of SIR layer
            if line == "\n":
                break
        
            new = Node(counter)
            split = line.split()
            adj = []
            assert len(split) % 2 == 0, "ERROR: each line in net cosntruction should have an even number of paramaters"
            for i in range(int(len(split)/2)):
                i = i * 2
                adj.append((int(split[i]), int(split[i + 1])))
            new.adjacent = adj
            nodes.append(new)
            counter += 1
            
        # sewer time
        sewer = {}
        while(True):
            line = f.readline()
            
            # check for end of manhole assignment
            if line == "\n":
                break
                
            split = line.split()
            name = ""
            adj = []
            assert len(split) % 2 == 0, "ERROR: each line in manhole construction should have an even number of paramaters"
            
            for i in range(int(len(split)/2)):
                i = i * 2
                name += split[i] + "-"
                adj.append((int(split[i]), int(split[i + 1])))
            name = name[:-1]
            new = Node(name)
            new.adjacent = adj
            new.samplable = True
            sewer[name] = new
            
            for i in adj:
                nodes[i[0]].nearest_manhole = (name, i[1])
                

        # creating sample queue
        for i in sewer.keys():
            for j in sewer[i].adjacent:
                queue = []
                for k in range(j[1]):
                    queue.append(0)
                nodes[j[0]].sample_q = queue
                
        # connecting manholes
        while(True):
            line = f.readline()
            
            # check for end of file
            if len(line) == 0:
                break
                
            split = line.split()
            assert len(split) == 3, "ERROR: each line connecting manholes should have exactly 3 paramaters"
            if split[1] != 'end':
                sewer[split[0]].nearest_manhole = (split[1], int(split[2]))
            else:
                end = Node('end')
                end.samplable = True
                sewer['end'] = end
                sewer[split[0]].nearest_manhole = ('end', int(split[2]))
                
        for i in sewer.keys():
            if i == 'end':
                break
            queue = []
            for j in range(sewer[i].nearest_manhole[1]):
                queue.append(0)
            sewer[i].sample_q = queue
            
    return nodes, sewer




def sample_simulate(net, sewer, rates, time):
    t = 0
    
    infected = []
    recovered = []
    samples = []
    sewer_nxt = []
    for i in net:
        if i.status == 1:
            infected.append(i)
        elif i.status == 2:
            recovered.append(i)
            
    while(t < time):
        t += 1
        
        new_infected = []
        for i in infected:
            
            # infecting others
            for j in i.adjacent:
                weight = j[1]
                j = net[j[0]]
                if j not in infected and j not in recovered and j not in new_infected:
                    # there is a chance to get infected
                    chance = rd.random() * weight
                    if chance > 1 - rates[0]:
                        j.status = 1
                        new_infected.append(j)
                        
            # recovering
            chance = rd.random()
            if chance < rates[1]:
                infected.remove(i)
                i.status = 2
                recovered.append(i)
                
        for i in new_infected:
            infected.append(i)
            
        # propagating sewer samples
        for i in net:
            i.sample_q.append(i.status % 2) # < --- change if you want more than 3 categories (i.e. SEIR instead of SIR)
        
        for i in sewer.keys():
            adj = sewer[i].adjacent
            marker = False
            for j in adj:
                popped = net[j[0]].sample_q.pop(0)
                if popped == 1:
                    marker = True
                    print("Sample recieved from node", j[0], "now node", sewer[i].name, "is samplable")
            sewer[i].status = int(marker)
            
        for i in sewer.keys():
            sewer[i].sample_q.append(sewer[i].status)
            
        for i in sewer.keys():
            if sewer[i].nearest_manhole != None:
                temp = sewer[i].nearest_manhole
                popped = sewer[i].sample_q.pop(0)
                sewer[temp[0]].status = max(sewer[temp[0]].status, popped)
                if popped == 1:
                    print("Sample recieved from node", i, "now node", sewer[temp[0]].name, "is samplable")
                    
        sewer['end'].sample_q = []
                
                
                
                
        print("TIME ---------------------------------", t)
        inf_string = ""
        for i in infected:
            inf_string += str(i.name) + " "
        rec_string = ""
        for i in recovered:
            rec_string += str(i.name) + " "
        print("INFECTED:", inf_string, "RECOVERED:", rec_string)
        sample_string = ""
        for i in sewer.keys():
            if sewer[i].status == 1:
                sample_string += i + " "
        print("VIABLE SAMPLE LOCATIONS:", sample_string, "\n")

    return net, sewer


def draw_graph(net, sewer, net_color, sewer_color, sewer_weights=True, all_weights=False):
    G = nx.Graph()

    for i in sewer.keys():
        for j in sewer[i].adjacent:
            G.add_edge(j[0], i, weight=j[1])
        if sewer[i].nearest_manhole != None:
            temp = sewer[i].nearest_manhole
            G.add_edge(i, temp[0], weight=temp[1])

    for i in net:
        G.add_node(i.name)

    for i in net:
        for j in i.adjacent:
            if not G.has_edge(i.name, j[0]):
                G.add_edge(i.name, j[0], weight=j[1])

    color_map = []
    for i in G:
        if i in sewer.keys():
            color_map.append(sewer_color)
        else:
            color_map.append(net_color)
            
    pos = nx.fruchterman_reingold_layout(G)
    nx.draw(G, pos, with_labels=True, cmap = plt.get_cmap('jet'), node_color=color_map)
    
    if all_weights:
        labels = {e: G.edges[e]['weight'] for e in G.edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    elif sewer_weights:
        temp = []
        for e in G.edges:
            if e[0] in sewer.keys() and e[1] in sewer.keys():
                temp.append(e)
        labels = {e: G.edges[e]['weight'] for e in temp}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        
    plt.show()
    return


def write_to_file_simulate(net_file, rates, time, file, trials, randomize_init=(True, 4), label=False):
    
    net, sewer = build_weighted_net(net_file)
    header = []
    for i in net:
        header.append(i.name)
    for j in sewer.keys():
        header.append(j)
    
    f = open(file, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
            
    for trial in range(trials):
        if label:
            writer.writerow(["TRIAL " + str(trial)])
        
        t = 0
        net, sewer = build_weighted_net(net_file)
        if randomize_init[0]:
            nums = []
            for i in range(len(net)):
                nums.append(i)
            init_infect = rd.sample(nums, randomize_init[1])
            for i in init_infect:
                net[i].status = 1
    
        infected = []
        recovered = []
        samples = []
        sewer_nxt = []
        for i in net:
            if i.status == 1:
                infected.append(i)
            elif i.status == 2:
                recovered.append(i)
        
        while(t < time):
            t += 1
        
            new_infected = []
            for i in infected:
            
                # infecting others
                for j in i.adjacent:
                    weight = j[1]
                    j = net[j[0]]
                    if j not in infected and j not in recovered and j not in new_infected:
                        # there is a chance to get infected
                        chance = rd.random() * weight
                        if chance > 1 - rates[0]:
                            j.status = 1
                            new_infected.append(j)
                        
                # recovering
                chance = rd.random()
                if chance < rates[1]:
                    infected.remove(i)
                    i.status = 2
                    recovered.append(i)
                
            for i in new_infected:
                infected.append(i)
            
            # propagating sewer samples
            for i in net:
                i.sample_q.append(i.status % 2) # < --- change if you want more than 3 categories (i.e. SEIR instead of SIR)
        
            for i in sewer.keys():
                adj = sewer[i].adjacent
                marker = False
                for j in adj:
                    popped = net[j[0]].sample_q.pop(0)
                    if popped == 1:
                        marker = True
                        #print("Sample recieved from node", j[0], "now node", sewer[i].name, "is samplable")
                sewer[i].status = int(marker)
            
            for i in sewer.keys():
                sewer[i].sample_q.append(sewer[i].status)
            
            for i in sewer.keys():
                if sewer[i].nearest_manhole != None:
                    temp = sewer[i].nearest_manhole
                    popped = sewer[i].sample_q.pop(0)
                    sewer[temp[0]].status = max(sewer[temp[0]].status, popped)
                    #if popped == 1:
                    #    print("Sample recieved from node", i, "now node", sewer[temp[0]].name, "is samplable")
                    
            sewer['end'].sample_q = []
        
        
            new_content = []
            for i in net:
                new_content.append(i.status)
            for i in sewer.keys():
                new_content.append(sewer[i].status)
            writer.writerow(new_content)
        
    f.close()

    # return net, sewer
    return

