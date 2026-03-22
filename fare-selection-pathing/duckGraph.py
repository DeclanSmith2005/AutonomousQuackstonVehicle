from __future__ import annotations
import requests
from dataclasses import dataclass, field
import math
import matplotlib.pyplot as plt
from collections import deque
import heapq
import time


import duckAPI

#### TO DOS ######
"""
- COMPLETE INTEGRATION W RAPH
- STRESS TEST ROUND ABOUT
- FIX EDGES DISAPPEARING
- ENSURE ITS GIVING ACCURATE DIRECTIONS
"""



@dataclass
class NavGraph:
    heading: float =  field(default_factory=float)
    carX: int = field(default_factory=int)
    carY : int =  field(default_factory=int)
    x: list[float] = field(default_factory=list)
    y: list[float] = field(default_factory=list)
    adj: list[list[int]] = field(default_factory=list)
    pathA: list[int] = field(default_factory=list)
    pathB: list[int] = field(default_factory=list)


    ignore = {29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41} # magic number nodes dont ask questions they have no out degree


    def getDistance(self, a: int, b: int) -> float:
        dx = self.x[a] - self.x[b]
        dy = self.y[a] - self.y[b]
        return math.hypot(dx, dy)

    def readGraph(self, node_file, adj_file) -> None:
        try:
            with open(node_file, "r") as f:
                node_lines = [ln.strip() for ln in f.readlines()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file '{node_file}' was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred reading '{node_file}': {e}")

        # drop empty lines (common if file ends with newline)
        node_lines = [ln for ln in node_lines if ln]

        # parse: each line expecte
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

    def showGraph(self, cx, cy, px, py, dx, dy) -> None:
        # Scatter base nodes
        plt.scatter(self.x, self.y, label="Graph Nodes")

        # Plot the three specific points with distinct colors
        plt.scatter(cx, cy, color='red', s=100, zorder=5, label="C Point")
        plt.scatter(px, py, color='green', s=100, zorder=5, label="P Point")
        plt.scatter(dx, dy, color='yellow', edgecolors='black', s=100, zorder=5, label="D Point")

        # Draw directed edges based on adjacency
        for i, nbrs in enumerate(self.adj):
            for j in nbrs:
                if 0 <= j < len(self.x):
                    plt.annotate(
                        "",
                        xy=(self.x[j], self.y[j]),
                        xytext=(self.x[i], self.y[i]),
                        arrowprops=dict(arrowstyle="->", linewidth=0.7, zorder = 10),
                    )
        path_xA = [self.x[i]+1 for i in self.pathA if i < len(self.x)]
        path_yA = [self.y[i]+1 for i in self.pathA if i < len(self.x)]

        path_xB = [self.x[i] for i in self.pathB if i < len(self.x)]
        path_yB = [self.y[i] for i in self.pathB if i < len(self.x)]
        
        
        # Scatter the points in purple
        plt.scatter(path_xA, path_yA, color='purple', s=80, zorder=6, label="Path Nodes")
        plt.scatter(path_xB, path_yB, color='pink', s=60, zorder=7, label="Path Nodes")

                    
        # Add a legend to explain the colors        
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

    # returns (u, v) for the closest directed edge u -> v, 
    # if the pickup point is within 10 linear units of any node k returns (k,k)
    # note that if u and v are in each others adjacency list, later logic assumes that the car is placed pointing
    # as North as possible, if the line is perfectly flat it should point right
    def findClosestEdge(self, Xcoord, Ycoord) -> tuple[int, int, float, float]:
        px, py = float(Xcoord), float(Ycoord)

        best_u = -1
        best_v = -1
        best_d2 = float("inf")
        best_qx = px  # Best closest point X
        best_qy = py  # Best closest point Y

        for u, nbrs in enumerate(self.adj):
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
                    curr_qx, curr_qy = ax, ay
                    dx = px - ax
                    dy = py - ay
                    d2 = dx * dx + dy * dy
                else:
                    t = (apx * abx + apy * aby) / denom
                    # Clamp t to the segment bounds [0, 1]
                    if t < 0.0:
                        t = 0.0
                    elif t > 1.0:
                        t = 1.0

                    curr_qx = ax + t * abx
                    curr_qy = ay + t * aby

                    dx = px - curr_qx
                    dy = py - curr_qy
                    d2 = dx * dx + dy * dy

                # If this segment gives a shorter distance, update our bests
                if d2 < best_d2:
                    best_d2 = d2
                    best_u, best_v = u, v
                    best_qx, best_qy = curr_qx, curr_qy

        if best_u == -1:
            raise ValueError("Graph has no edges; cannot find a closest edge.")
        
        # Consistent ordering for bidirectional edges
        if best_u in self.adj[best_v] and best_v in self.adj[best_u]:
            dx = self.x[best_v] - self.x[best_u]
            dy = self.y[best_v] - self.y[best_u]

            # Prefer pointing UP; if perfectly horizontal, prefer RIGHT
            if dy < 0 or (dy == 0 and dx < 0):
                best_u, best_v = best_v, best_u

        # Now returns the edge nodes AND the exact coordinate projection
        return best_u, best_v, best_qx, best_qy
    
    # returns [u, v, p] where u and v are the nodes that it sits between and p is the requested node. 
    # returns [-1, -1, p] in case that the new location is on top of an existing node
    def addTempNode (self, nodeX: float, nodeY: float) -> tuple[int, int, int]:
        u, v, newX, newY = self.findClosestEdge(nodeX, nodeY)
        self.x.append(newX)
        self.y.append(newY)
        p = len(self.x)-1
        self.adj[u].append(p)
        if u in self.adj[v]:
            self.adj[v].append(p)
            self.adj[v].remove(u)
            self.adj.append([u, v])
        else:
            self.adj.append([v])
            self.adj[u].remove(v)
        return [u, v, p]
    

    def removeTempNode(self, u: int, v: int, p: int) -> None:
        if p in self.adj[u]:
            self.adj[u].remove(p)
        if p in self.adj[v]:
            self.adj[v].remove(p)
        if u in self.adj[p]: 
            self.adj[v].append(u) # Restores v -> u
        if v in self.adj[p]:
            self.adj[u].append(v) # Restores u -> v
        self.adj.pop()
        self.x.pop()
        self.y.pop()

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
    
    def navigate(self, carHeading, carX, carY, destX, destY):
        futureRemovals = []
        #du, dv are  nodes that destination node falls between 
        du, dv, d = self.addTempNode(destX, destY)
        if du > -1 and dv > -1:
            futureRemovals.append((du, dv, d))

        # cu, cv are nodes that car node falls between 
        cu, cv, c = self.addTempNode(carX, carY)
        if cu > -1 and cv > -1:
            futureRemovals.append((cu, cv, c))

        # remove the node from adj that is behind where the car is pointing:
        original_adj_c = self.adj[c].copy()
        cpy = []
        for n in self.adj[c]:
            nx, ny = self.x[n], self.y[n]
            dx = nx - carX
            dy = ny - carY
            hx = math.cos(carHeading)
            hy = math.sin(carHeading)
            dot_product = (dx * hx) + (dy * hy)
            if dot_product >= 0:
                cpy.append(n)
        self.adj[c] = cpy
        path, dist = self.findShortestPath(c, d)

        if path and len(path) >= 2:
            finalHeading = math.atan2(self.y[path[-1]] - self.y[path[-2]], self.x[path[-1]] - self.x[path[-2]])
        else:
            finalHeading = self.heading
        p = self.convertToDirections(path)

        self.adj[c] = original_adj_c
        for u, v, n in reversed(futureRemovals):
            self.removeTempNode(u, v, n)
        return p, dist, finalHeading, path

    def convertToDirections(self, pathNodes: list) -> list:
        res= []
        for i in range(len(pathNodes)-2):
            curr, nxt = pathNodes[i], pathNodes[i+1]
            if nxt in self.ignore:
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
                    for val, node in releativeAngles:
                        dirs[node] = 'RIGHT' if val < 0 else 'LEFT'
                else:
                    dirs[s_node] = 'STRAIGHT' + str(math.degrees(s_val))
                    sInd = releativeAngles.index((s_val, s_node))
                    for k in range(len(releativeAngles)):
                        if releativeAngles[k][0] == s_val:
                            dirs[releativeAngles[k][1]] = dirs[s_node]
                        elif k < sInd:
                            dirs[releativeAngles[k][1]] = 'RIGHT' + str(math.degrees(releativeAngles[k][0]))
                        elif k > sInd:
                            dirs[releativeAngles[k][1]] = 'LEFT' + str(math.degrees(releativeAngles[k][0]))
                                        
                res.append(dirs[pathNodes[i+2]])
        return res
    
    def getBestFare(self):
        #self.updatePosition()
        """uncomment"""

        fareInfo = {} # {fareId : [score, pathTostart, pathtoFinishFromStart]}
        fares = duckAPI.getFares()
        bestFare, bestScore = -1, -1

        """****"""
        self.carX, self.carY = 300,85 
        """^^^ remove after testing """

        for fare in fares:
            fareRate = 10 if fare['modifiers'] == 0 else 5
            fareStartEndAbsDist = (math.sqrt((fare['src']['x'] - fare['dest']['x'])**2 + (fare['src']['y'] - fare['dest']['y'])**2))/100
            dirs1, d1, finalHeading, points1 = self.navigate(self.heading, self.carX, self.carY, fare['src']['x'], fare['src']['y'])
            dirs2, d2, h, points2 = self.navigate(finalHeading, fare['src']['x'], fare['src']['y'], fare['dest']['x'], fare['dest']['y'])
            score = (10 + (fareStartEndAbsDist*fareRate))/((d1 + d2)/100)
            fareInfo[fare['id']] = [ fare['src']['x'], fare['src']['y'], fare['dest']['x'], fare['dest']['y'], score, dirs1, dirs2, points1, points2]
            if score > bestScore:
                bestFare, bestScore = fare['id'], score
        print("car pos" , self.carX, self.carY)
        print("pasanger pos ", fareInfo[bestFare][0], fareInfo[bestFare][1])
        print("destination pos", fareInfo[bestFare][2], fareInfo[bestFare][3])
        print("dirs 1", fareInfo[bestFare][5])
        print("dirs 2", fareInfo[bestFare][6])
        self.pathA.extend(fareInfo[bestFare][-2])
        self.pathB.extend(fareInfo[bestFare][-1])
        
        return bestFare, fareInfo[bestFare]
    
    def updatePosition(self):
        positionJSON = duckAPI.getCurrentLocation()
        position = positionJSON['position']
        self.heading, self.carX, self.carY = position['heading'], position['x'], position['y']
        
            

                
def main() -> None:
    g = NavGraph()
    g.readGraph("graph.txt", "adj.txt")
    g.heading = math.pi/2
    fid, info = g.getBestFare()

    g.showGraph(g.carX, g.carY, info[0], info[1], info[2], info[3])
    #main loop
    
            

            
if __name__ == "__main__":
    main()
