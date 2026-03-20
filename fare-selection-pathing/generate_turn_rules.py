import math
import os

def readGraph(node_file, adj_file):
    x, y, adj = [], [], []
    with open(node_file, "r") as f:
        node_lines = [ln.strip() for ln in f if ln.strip()]
    for ln in node_lines:
        parts = [p.strip() for p in ln.split(",")]
        x.append(float(parts[0]))
        y.append(float(parts[1]))
        
    adj = [[] for _ in range(len(x))]
    with open(adj_file, "r") as f:
        adj_lines = [ln.strip() for ln in f]
    for i in range(min(len(x), len(adj_lines))):
        ln = adj_lines[i]
        if not ln: continue
        adj[i] = [int(tok.strip()) for tok in ln.split(",") if tok.strip()]
        
    return x, y, adj

def generate_base_rules(node_file, adj_file, output_file):
    x, y, adj = readGraph(node_file, adj_file)
    rules = []
    
    for u in range(len(x)):
        for v in adj[u]:
            if v < 0 or v >= len(x): continue
            for w in adj[v]:
                if w < 0 or w >= len(x): continue
                if w == u: continue
                
                dx = x[v] - x[u]
                dy = y[v] - y[u]
                curr_angle = math.atan2(dy, dx) % (2*math.pi)

                releativeAngles = sorted([((math.atan2(y[n]-y[v], x[n]-x[v]) - curr_angle + math.pi) % (2*math.pi) - math.pi, n) 
                    for n in adj[v] if n != u])
                if not releativeAngles: continue
                    
                s_val, s_node = min(releativeAngles, key=lambda p: abs(p[0]))
                T_JUNCTION_THRESHOLD = math.radians(60)
                dirs = {}
                if abs(s_val) > T_JUNCTION_THRESHOLD:
                    for val, node in releativeAngles:
                        dirs[node] = 'R' if val < 0 else 'L2'
                else:
                    dirs[s_node] = 'ST'
                    sInd = releativeAngles.index((s_val, s_node))
                    for k in range(len(releativeAngles)):
                        if k < sInd:
                            dirs[releativeAngles[k][1]] = 'R'
                        elif k > sInd:
                            dirs[releativeAngles[k][1]] = 'L2'
                
                turn = dirs.get(w, 'ST')
                rules.append(f"{u}, {v}, {w}, {turn}")
                
    with open(output_file, "w") as f:
        f.write("# u, v, w, TURN_TYPE\n")
        for rule in rules:
            f.write(rule + "\n")
    print(f"Generated {len(rules)} base turn rules into {output_file}")

if __name__ == "__main__":
    generate_base_rules("graph.txt", "adj.txt", "turn_rules.txt")
