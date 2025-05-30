import heapq

class AStar:
    def __init__(self, graph, coordinates):
        self.graph = graph
        self.coordinates = coordinates

    def heuristic(self, node, goal):
        """Tính toán khoảng cách heuristic giữa hai thành phố dựa trên tọa độ."""
        x1, y1 = self.coordinates[node]
        x2, y2 = self.coordinates[goal]
        return abs(x1 - x2) + abs(y1 - y2)  # Khoảng cách Manhattan

    def find_path(self, start, goal):
        """Thuật toán A* tìm đường đi ngắn nhất từ start đến goal."""
        open_set = []
        heapq.heappush(open_set, (0, start))  # (f_score, node)
        came_from = {}  # Lưu trữ đường đi
        g_score = {node: float('inf') for node in self.graph}
        g_score[start] = 0
        f_score = {node: float('inf') for node in self.graph}
        f_score[start] = self.heuristic(start, goal)
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], g_score[goal]  # Trả về đường đi và tổng chi phí
            
            for neighbor in self.graph.neighbors(current):
                edge_data = self.graph.get_edge_data(current, neighbor)

                if isinstance(edge_data, dict):
                    if 0 in edge_data:  # MultiDiGraph
                        min_cost = min(attr.get('length', 1) for attr in edge_data.values())
                    else:
                        min_cost = edge_data.get('length', 1)
                else:
                    min_cost = 1

                tentative_g_score = g_score[current] + min_cost
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
        return None, float('inf')  # Không tìm thấy đường đi và chi phí là vô cùng