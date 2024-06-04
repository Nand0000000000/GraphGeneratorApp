import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import heapq
import os

class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    def add_edge(self, source, target, weight=1):
        if source not in self.adjacency_list:
            self.add_vertex(source)
        if target not in self.adjacency_list:
            self.add_vertex(target)

        self.adjacency_list[source].append(target)
        self.edge_weights[(source, target)] = weight

        if not self.directed:
            self.adjacency_list[target].append(source)
            self.edge_weights[(target, source)] = weight

    def is_eulerian(self):
        odd_degree_vertices = sum(1 for vertex, adj in self.adjacency_list.items() if len(adj) % 2 != 0)
        if odd_degree_vertices == 0:
            return True, False  # Eulerian
        elif odd_degree_vertices == 2:
            return False, True  # Semi-Eulerian
        return False, False  # Neither

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                source, target, weight = parts[0], parts[1], int(parts[2])
                self.add_edge(source, target, weight)

    def display_graph(self):
        graph_representation = ""
        for vertex, edges in self.adjacency_list.items():
            edges_with_weights = [f"{edge} (Weight: {self.edge_weights.get((vertex, edge), 'N/A')})" for edge in edges]
            graph_representation += f"{vertex}: {', '.join(edges_with_weights)}\n"
        return graph_representation

    def get_order(self):
        return len(self.adjacency_list)

    def get_size(self):
        return sum(len(edges) for edges in self.adjacency_list.values()) // (2 if not self.directed else 1)

    def get_adjacent_vertices(self, vertex):
        return self.adjacency_list.get(vertex, [])

    def get_degree(self, vertex):
        if self.directed:
            out_degree = len(self.adjacency_list.get(vertex, []))
            in_degree = sum(vertex in edges for edges in self.adjacency_list.values())
            return {'in_degree': in_degree, 'out_degree': out_degree}
        else:
            return len(self.adjacency_list.get(vertex, []))

    def are_adjacent(self, v1, v2):
        return v2 in self.adjacency_list.get(v1, [])

    def dijkstra(self, start_vertex):
        distances = {vertex: float('infinity') for vertex in self.adjacency_list}
        distances[start_vertex] = 0
        priority_queue = [(0, start_vertex)]
        predecessors = {vertex: None for vertex in self.adjacency_list}

        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)

            for neighbor in self.adjacency_list[current_vertex]:
                weight = self.edge_weights.get((current_vertex, neighbor), 1)
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_vertex
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances, predecessors

    def shortest_path(self, start, end):
        distances, predecessors = self.dijkstra(start)
        path, current_vertex = [], end

        if distances[end] == float('infinity'):
            return "No path exists", []

        while predecessors[current_vertex] is not None:
            path.insert(0, current_vertex)
            current_vertex = predecessors[current_vertex]
        if path:
            path.insert(0, current_vertex)

        return distances[end], path

class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.graph = Graph(directed=False)
        self.title("Graph Manager")
        self.geometry("600x600")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Graph Manager", font=('Helvetica', 16)).pack(pady=10)
        self.is_directed = tk.BooleanVar()
        tk.Checkbutton(self, text="Directed Graph", variable=self.is_directed, command=self.toggle_directed).pack()
        tk.Button(self, text="Add Vertex", command=self.add_vertex).pack(pady=5)
        tk.Button(self, text="Add Edge", command=self.add_edge).pack(pady=5)
        tk.Button(self, text="Load Graph from File", command=self.load_graph).pack(pady=5)
        tk.Button(self, text="Check Eulerian Status", command=self.check_eulerian).pack(pady=5)
        self.graph_display = tk.Text(self, height=10, width=50)
        self.graph_display.pack(pady=10)
        tk.Button(self, text="Display Order and Size", command=self.display_order_size).pack(pady=5)
        tk.Button(self, text="Get Adjacent Vertices", command=self.get_adjacent_vertices).pack(pady=5)
        tk.Button(self, text="Get Degree of Vertex", command=self.get_degree_of_vertex).pack(pady=5)
        tk.Button(self, text="Check If Vertices Are Adjacent", command=self.check_adjacency).pack(pady=5)
        tk.Button(self, text="Find Shortest Path", command=self.find_shortest_path).pack(pady=5)

    def toggle_directed(self):
        self.graph.directed = self.is_directed.get()
        self.update_display()

    def add_vertex(self):
        vertex = simpledialog.askstring("Input", "Enter vertex name:", parent=self)
        if vertex:
            self.graph.add_vertex(vertex)
            self.update_display()

    def add_edge(self):
        source = simpledialog.askstring("Input", "Enter source vertex:", parent=self)
        target = simpledialog.askstring("Input", "Enter target vertex:", parent=self)
        weight = simpledialog.askinteger("Input", "Enter weight (optional, default=1):", parent=self, minvalue=1)
        if source and target:
            self.graph.add_edge(source, target, weight)
            self.update_display()

    def load_graph(self):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
        if file_path:
            self.graph.load_from_file(file_path)
            self.update_display()

    def check_eulerian(self):
        is_eulerian, is_semi_eulerian = self.graph.is_eulerian()
        message = "Graph is "
        if is_eulerian:
            message += "Eulerian."
        elif is_semi_eulerian:
            message += "Semi-Eulerian."
        else:
            message += "neither Eulerian nor Semi-Eulerian."
        messagebox.showinfo("Eulerian Check", message)

    def update_display(self):
        self.graph_display.delete(1.0, tk.END)
        self.graph_display.insert(tk.END, self.graph.display_graph())

    def display_order_size(self):
        order = self.graph.get_order()
        size = self.graph.get_size()
        messagebox.showinfo("Graph Order and Size", f"Order (Vertices): {order}\nSize (Edges): {size}")

    def get_adjacent_vertices(self):
        vertex = simpledialog.askstring("Input", "Enter vertex name:", parent=self)
        if vertex:
            adj_vertices = self.graph.get_adjacent_vertices(vertex)
            messagebox.showinfo("Adjacent Vertices", f"Adjacent vertices of {vertex}: {adj_vertices}")

    def get_degree_of_vertex(self):
        vertex = simpledialog.askstring("Input", "Enter vertex name:", parent=self)
        if vertex:
            degree = self.graph.get_degree(vertex)
            if isinstance(degree, dict):
                messagebox.showinfo("Vertex Degree",
                                    f"Degree of {vertex} - In: {degree['in_degree']}, Out: {degree['out_degree']}")
            else:
                messagebox.showinfo("Vertex Degree", f"Degree of {vertex}: {degree}")

    def check_adjacency(self):
        v1 = simpledialog.askstring("Input", "Enter first vertex name:", parent=self)
        v2 = simpledialog.askstring("Input", "Enter second vertex name:", parent=self)
        if v1 and v2:
            is_adjacent = self.graph.are_adjacent(v1, v2)
            messagebox.showinfo("Vertices Adjacency",
                                f"{v1} and {v2} are {'adjacent' if is_adjacent else 'not adjacent'}.")

    def find_shortest_path(self):
        start = simpledialog.askstring("Input", "Enter start vertex name:", parent=self)
        end = simpledialog.askstring("Input", "Enter end vertex name:", parent=self)
        if start and end:
            cost, path = self.graph.shortest_path(start, end)
            if path:
                messagebox.showinfo("Shortest Path", f"Shortest path from {start} to {end} is {path} with cost {cost}.")
            else:
                messagebox.showinfo("Shortest Path", "No path exists between the vertices.")

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
