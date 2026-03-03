from __future__ import annotations

from dataclasses import dataclass, field
import math
import matplotlib.pyplot as plt
from collections import deque
import heapq

#### TO DOS ######
"""
- CONFIRM W/ STAFF ABT ORIENTATION OF CAR WHEN WE START, AND HOW TO GET CURR POS, AND HOW TO GET LIST OF FARES
- INTEGRATE WITH RAPHAEL'S SERVER
- WRITE CODE TO CHOOSE NEXT PASSANGER
- INTERACT WITH THEIR POSITIONING API
- WRITE A FUNCTION THAT CONVERTS THE PATH LIST FROM DIJKSTRA'S TO A LIST OF TURNS / DIRECTIONS
"""



@dataclass
class NavGraph:
    carX: int = field(default_factory=int)
    carY : int =  field(default_factory=int)
    x: list[float] = field(default_factory=list)
    y: list[float] = field(default_factory=list)
    adj: list[list[int]] = field(default_factory=list)
    maxSpeed: list[float] = field(default_factory=list)
    zoneType: list[int] = field(default_factory=list)
    stop: list[int] = field(default_factory=list)

    def getDistance(self, a: int, b: int) -> float:
        dx = self.x[a] - self.x[b]
        dy = self.y[a] - self.y[b]
        return math.hypot(dx, dy)

    def readGraph(self, node_file: str = "graph.txt", adj_file: str = "adj.txt") -> None:
        try:
            with open(node_file, "r") as f:
                node_lines = [ln.strip() for ln in f.readlines()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file '{node_file}' was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred reading '{node_file}': {e}")

        # drop empty lines (common if file ends with newline)
        node_lines = [ln for ln in node_lines if ln]

        # parse: each line expected "x,y,speed,zone,stop"
        for i, ln in enumerate(node_lines):
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Bad node line {i}: expected 2 comma-separated values, got {len(parts)} -> {ln!r}")

            xval = float(parts[0])
            yval = float(parts[1])
            # speed = float(parts[2])
            # zone = int(parts[3])
            # stp = int(parts[4])

            self.x.append(xval)
            self.y.append(yval)
            # self.maxSpeed.append(speed)
            # self.zoneType.append(zone)
            # self.stop.append(stp)

        n = len(self.x)
        self.adj = [[] for _ in range(n)]  # initialize adjacency list

        try:
            with open(adj_file, "r") as f:
                adj_lines = [ln.strip() for ln in f.readlines()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file '{adj_file}' was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred reading '{adj_file}': {e}")

        for i in range(min(n, len(adj_lines))):
            ln = adj_lines[i].strip()
            if not ln:
                self.adj[i] = []
                continue
            self.adj[i] = [int(tok.strip()) for tok in ln.split(",") if tok.strip()]

    def showGraph(self) -> None:
        # scatter nodes
        plt.scatter(self.x, self.y)

        # draw directed edges based on adjacency
        for i, nbrs in enumerate(self.adj):
            for j in nbrs:
                if 0 <= j < len(self.x):
                    plt.annotate(
                        "",
                        xy=(self.x[j], self.y[j]),
                        xytext=(self.x[i], self.y[i]),
                        arrowprops=dict(arrowstyle="->", linewidth=0.7),
                    )
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

    # returns (u, v) for the closest directed edge u -> v, 
    # if the pickup point is within 10 linear units of any node k returns (k,k)
    # note that if u and v are in each others adjacency list, later logic assumes that the car is placed pointing
    # as North as possible, if the line is perfectly flat it should point right
    def findClosestEdge(self, Xcoord, Ycoord) -> tuple[int, int]:
        px, py = float(Xcoord), float(Ycoord)

        # 1) Snap to nearest node if within 10 units
        SNAP_DIST = 10.0
        snap_d2 = SNAP_DIST * SNAP_DIST
        best_u = -1
        best_v = -1
        best_d2 = float("inf")

        for u, nbrs in enumerate(self.adj):
            # check if near enough to a specific node to just return that node
            dx = px - self.x[u]
            dy = py - self.y[u]
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best_u = u
            if best_u != -1 and best_d2 <= snap_d2:
                return best_u, best_u

            ax, ay = self.x[u], self.y[u]
            for v in nbrs:
                if v < 0 or v >= len(self.x):
                    continue  # ignore bad adjacency entries

                bx, by = self.x[v], self.y[v]
                abx = bx - ax
                aby = by - ay
                apx = px - ax
                apy = py - ay

                denom = abx * abx + aby * aby
                if denom == 0.0:
                    # degenerate edge: treat like a point at A
                    dx = px - ax
                    dy = py - ay
                    d2 = dx * dx + dy * dy
                else:
                    t = (apx * abx + apy * aby) / denom
                    if t < 0.0:
                        t = 0.0
                    elif t > 1.0:
                        t = 1.0

                    qx = ax + t * abx
                    qy = ay + t * aby

                    dx = px - qx
                    dy = py - qy
                    d2 = dx * dx + dy * dy

                if d2 < best_d2:
                    best_d2 = d2
                    best_u, best_v = u, v

        if best_u == -1:
            raise ValueError("Graph has no edges; cannot find a closest edge.")
        
        
        if best_u in self.adj[best_v] and best_v in self.adj[best_u]:
            dx = self.x[best_v] - self.x[best_u]
            dy = self.y[best_v] - self.y[best_u]

            # Prefer pointing UP; if perfectly horizontal, prefer RIGHT
            if dy < 0 or (dy == 0 and dx < 0):
                best_u, best_v = best_v, best_u

        return best_u, best_v
    
    # returns [u, v, p] where u and v are the nodes that it sits between and p is the requested node. 
    # returns [-1, -1, p] in case that the new location is on top of an existing node
    def addTempNode (self, nodeX: float, nodeY: float) -> tuple[int, int, int]:
        u, v, p = (self.findClosestEdge(self, nodeX, nodeY), len(self.x)-1)
        self.x.append[nodeX]
        self.y.append[nodeY]
        if u != v:
            self.adj[u].append(p)
            if u in self.adj[v]:
                self.adj[p] = [u, v]
                self.adj[v].append(p)
            else:
                self.adj[p] = [v]
            return [u, v, p]
        else:
            return [-1, -1, u]

    def removeTempNode(self, u: int, v: int) -> None:
        # adj clean up
        self.adj[u].pop()
        if u in self.adj[v]:
            self.adj[v].pop()
        self.adj.pop()

    def findShortestPath(self, currentNode: int, targetNode: int) -> list:
        dists = [float('inf') for i in range(len(self.x))]
        dists[currentNode] = 0
        prev = [-1 for i in range(len(self.x))]
        heap = [(0, currentNode)]

        while heap and dists[targetNode] == float('inf'):
            distance, node = heapq.heappop(heap)
            if distance > dists[node]:
                continue
            for nbr in self.adj[node]:
                nextDist = self.getDistance(nbr, node) + distance
                if nextDist < dists[nbr]:
                    prev[nbr] = node
                    heapq.heappush(heap, (nextDist, nbr))
                    dists[nbr] = min(dists[nbr], nextDist)
        
        path = deque([targetNode])
        n = targetNode
        while n != currentNode:
            path.appendleft(prev[n])
            n = prev[n]

        return list(path), dists[targetNode]

    def convertToDirections(self, pathNodes: list) -> list:
        res= []
        for i in range(len(pathNodes)-2):
            curr, nxt = pathNodes[i], pathNodes[i+1]
            if len(self.adj[nxt]) < 3:
                continue
            else:
                # curr angle
                dx = self.x[nxt] - self.x[curr]
                dy = self.y[nxt] - self.y[curr]
                curr_angle = math.atan2(dy, dx) % (2*math.pi)

                # upcoming roads
                releativeAngles = sorted([((math.atan2(self.y[n]-self.y[nxt], self.x[n]-self.x[nxt]) - curr_angle + math.pi) % (2*math.pi) - math.pi, n) 
                    for n in self.adj[nxt] if n != curr])
                
                s_val, s_node = min(releativeAngles, key=lambda x: abs(x[0]))
                T_JUNCTION_THRESHOLD = math.radians(60)
                dirs = {}
                if abs(s_val) > T_JUNCTION_THRESHOLD:
                    dirs[releativeAngles[-1][1]] = 'LEFT'
                    dirs[releativeAngles[0][1]] = 'RIGHT'
                else:
                    dirs[s_node] = 'STRAIGHT'
                    if len(releativeAngles) > 1:
                        if releativeAngles[-1][1] != s_node:
                            dirs[releativeAngles[-1][1]] = 'LEFT'
                        if releativeAngles[0][1] != s_node:
                            dirs[releativeAngles[0][1]] = 'RIGHT'
                res.append(dirs[pathNodes[i+2]])
        return res
                
                
def main() -> None:
    g = NavGraph()
    g.readGraph("graph.txt", "adj.txt")
    g.showGraph()

    #main loop
    # while True:
    #     # get new passanger coordinates()
    #     #example
    #     futureRemovals = []
    #     px, py = 256, 30
    #     pu, pv, p = g.addTempNode(px, py)
    #     if pu > -1 and pv > -1:
    #          futureRemovals.append((pu, pv))

    #     #get current coordinates of car()
    #     cx, cy = 581, 102
    #     cu, cv, c = g.addTempNode(px, py)
    #     if cu > -1 and cv > -1:
    #         futureRemovals.append((cu, cv))

    #     g.findShortestPath(c, p)

    #     #clean up
    #     for u, v, n in futureRemovals:
    #         g.removeTempNode(u, v)

if __name__ == "__main__":
    main()
