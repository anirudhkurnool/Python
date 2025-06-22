from stack import Stack
from queue import Queue

class CycleDetected(Exception):
    pass


class Edge:
    def __init__(self, from_vertex, to_vertex, weight):
        self.from_vertex = from_vertex
        self.to_vertex = to_vertex
        self.weight = weight
        self.next = None

    def __repr__(self):
        return f"Edge[from : {self.from_vertex}; to : {self.to_vertex}; weight : {self.weight}]"
    
    def __str__(self):
        return f"Edge[from : {self.from_vertex}; to : {self.to_vertex}; weight : {self.weight}]"


class Graph:
    def __init__(self, is_directed=True):
        self.adjacency_list = dict()
        self.num_nodes = 0
        self.is_direced = is_directed

    def add_vertex(self, vertex):
        try:
            self.adjacency_list[vertex] = None
            self.num_nodes += 1

        except Exception as e:
            print(e)

    def add_edge_helper(self, vertex1, vertex2, weight):
        start = self.adjacency_list[vertex1]
        if start == None:
            self.adjacency_list[vertex1] = Edge(vertex1, vertex2, weight) 

        else:
            while start.next != None:
                start = start.next

            start.next = Edge(vertex1, vertex2, weight)

    def add_edge(self, vertex1, vertex2, weight_f_t=None, weight_t_f=None):
        try:
            self.add_edge_helper(vertex1, vertex2, weight_f_t)

            if not self.is_direced:
                self.add_edge_helper(vertex2, vertex1, weight_t_f)

        except Exception as e:
            print(e)

    def __repr__(self):
        return f"=====GRAPH=====\nTotal number of nodes = {self.num_nodes}\n{self.adjacency_list}"
    
    def __str__(self):
        return f"=====GRAPH=====\nTotal number of nodes = {self.num_nodes}\n{self.adjacency_list}"
    
    def dfs(self, start_node=None):
        if not start_node:
            start_node = list(self.adjacency_list.keys())[0]

        stack = Stack()
        stack.push(start_node)

        res = []
        visited = set()

        while stack.size != 0:
            curr = stack.pop()
            visited.add(curr)
            res.append(curr)
            start = self.adjacency_list[curr]
            while start != None:
                if start.to_vertex not in visited:
                    stack.push(start.to_vertex)

                start = start.next 

        return res
    

    def bfs(self, start_node = None):
        if not start_node:
            start_node = list(self.adjacency_list.keys())[0]

        q = Queue()
        q.enqueue(start_node)

        res = []
        visited = set()

        while q.size != 0:
            curr = q.dequeue()
            visited.add(curr)
            res.append(curr)
            start = self.adjacency_list[curr]
            while start != None:
                if start.to_vertex not in visited:
                    q.enqueue(start.to_vertex)

                start = start.next 

        return res
    
    def kahns_cycle_detection_algo(self):
        pass 

    def dfs_color_cycle_detection(self):
        pass 

    def topological_sort_cycle_detection(self):
        pass
    
    def cycle_detection(self):
        if self.is_direced:
            pass 

        else:
            pass

    def topological_sort(self):
        pass 

    def dijkstra_sssp_algo(self):
        pass 

    def bellman_ford(self):
        pass 

    def floyd_warshall(self):
        pass 

    def prims_mst_algo(self):
        pass 

    def kruskals_mst_algo(self):
        pass 

def main():
    g = Graph()
    g.add_vertex(1)
    g.add_vertex(2)
    g.add_vertex(3)
    g.add_vertex(4)
    g.add_vertex(5)
    g.add_edge(1, 2, 4)
    g.add_edge(1, 3, 5)
    g.add_edge(2, 4, 6)
    g.add_edge(3, 5, 7)
    print(g)
    dfs = g.dfs(1)
    print(f"dfs : {dfs}")
    bfs = g.bfs(1)
    print(f"bfs : {bfs}")


if __name__ == "__main__":
    main()
        



