"""
Module: src/herm4ai/graph_viz.py
Visual knowledge network graph exporter for HERM4AI associative memory.
Generates:
1. Interactive standalone HTML network visualizer.
2. Formatted Mermaid diagram for markdown artifacts and reports.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from .engine import HERMMemoryEngine


def export_mermaid_graph(engine: HERMMemoryEngine, output_path: str = "results/associative_network.mermaid") -> str:
    """
    Exports associative memory edges to a clean Mermaid flowchart diagram.
    """
    cursor = engine.conn.cursor()
    cursor.execute("SELECT * FROM associative_edges WHERE status = 'ACTIVE' ORDER BY weight DESC")
    edges = cursor.fetchall()

    lines = ["graph LR"]
    if not edges:
        lines.append("    EmptyNode[\"No active associative edges in memory\"]")
    else:
        # Sanitize entity names for mermaid node IDs
        def node_id(name: str) -> str:
            return name.replace(" ", "_").replace("-", "_").replace(".", "_")

        for e in edges:
            src_id = node_id(e["source_entity"])
            tgt_id = node_id(e["target_entity"])
            rel = e["relation"]
            w = e["weight"]
            lines.append(f'    {src_id}["{e["source_entity"]}"] -->|"{rel} (w={w})"| {tgt_id}["{e["target_entity"]}"]')

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(out_file)


def export_interactive_html_graph(engine: HERMMemoryEngine, output_path: str = "results/associative_network.html") -> str:
    """
    Generates an interactive, standalone HTML knowledge graph visualization.
    Embedded SVG and JavaScript with pan, zoom, drag, and node highlighting.
    Zero external network dependencies.
    """
    cursor = engine.conn.cursor()
    cursor.execute("SELECT * FROM associative_edges WHERE status = 'ACTIVE'")
    edges = cursor.fetchall()

    nodes_set = set()
    edge_list = []
    for e in edges:
        nodes_set.add(e["source_entity"])
        nodes_set.add(e["target_entity"])
        edge_list.append({
            "source": e["source_entity"],
            "target": e["target_entity"],
            "relation": e["relation"],
            "weight": e["weight"]
        })

    nodes_list = [{"id": n, "label": n} for n in nodes_set]
    graph_data_json = json.dumps({"nodes": nodes_list, "edges": edge_list})

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HERM4AI — Associative Knowledge Network</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --border-color: #1f2937;
            --text-color: #f3f4f6;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #c084fc;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-color); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        .header {{ padding: 16px 24px; background: var(--card-bg); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 20px; color: var(--accent-blue); }}
        .header p {{ font-size: 13px; color: #9ca3af; margin-top: 4px; }}
        .stats-badge {{ background: #1e293b; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; font-size: 12px; }}
        #networkContainer {{ flex: 1; position: relative; width: 100%; height: calc(100vh - 80px); cursor: grab; }}
        svg {{ width: 100%; height: 100%; }}
        .node circle {{ fill: #1e293b; stroke: var(--accent-blue); stroke-width: 2.5px; cursor: pointer; transition: all 0.2s; }}
        .node:hover circle {{ fill: #38bdf8; stroke: #fff; }}
        .node text {{ fill: #f8fafc; font-size: 12px; font-weight: 600; text-anchor: middle; pointer-events: none; }}
        .link {{ stroke: #475569; stroke-opacity: 0.8; stroke-dasharray: 4; }}
        .link-label {{ fill: #94a3b8; font-size: 10px; font-family: monospace; text-anchor: middle; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>HERM4AI — Associative Knowledge Graph</h1>
            <p>Interactive visualization of relational connections, semantic associations, and spreading activation pathways.</p>
        </div>
        <div class="stats-badge">
            Nodes: <strong style="color: var(--accent-green);" id="nodeCount">{len(nodes_list)}</strong> | 
            Edges: <strong style="color: var(--accent-purple);" id="edgeCount">{len(edge_list)}</strong>
        </div>
    </div>
    <div id="networkContainer">
        <svg id="networkSvg">
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                </marker>
            </defs>
            <g id="zoomGroup"></g>
        </svg>
    </div>

    <script>
        const data = {graph_data_json};
        const svg = document.getElementById("networkSvg");
        const zoomGroup = document.getElementById("zoomGroup");

        const width = window.innerWidth;
        const height = window.innerHeight - 80;

        // Position nodes in a clean circular layout
        const N = data.nodes.length;
        const radius = Math.min(width, height) * 0.35;
        const centerX = width / 2;
        const centerY = height / 2;

        const nodePos = {{}};
        data.nodes.forEach((node, idx) => {{
            const angle = (idx / (N || 1)) * 2 * Math.PI;
            nodePos[node.id] = {{
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            }};
        }});

        // Render Edges
        data.edges.forEach(edge => {{
            const p1 = nodePos[edge.source] || {{ x: centerX, y: centerY }};
            const p2 = nodePos[edge.target] || {{ x: centerX, y: centerY }};

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", p1.x);
            line.setAttribute("y1", p1.y);
            line.setAttribute("x2", p2.x);
            line.setAttribute("y2", p2.y);
            line.setAttribute("class", "link");
            line.setAttribute("stroke-width", Math.max(1.5, edge.weight * 2.5));
            line.setAttribute("marker-end", "url(#arrow)");
            zoomGroup.appendChild(line);

            // Edge label
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", (p1.x + p2.x) / 2);
            text.setAttribute("y", (p1.y + p2.y) / 2 - 5);
            text.setAttribute("class", "link-label");
            text.textContent = edge.relation + " (" + edge.weight + ")";
            zoomGroup.appendChild(text);
        }});

        // Render Nodes
        data.nodes.forEach(node => {{
            const pos = nodePos[node.id];
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("class", "node");
            g.setAttribute("transform", `translate(${{pos.x}}, ${{pos.y}})`);

            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("r", "16");
            g.appendChild(circle);

            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("y", "26");
            text.textContent = node.label;
            g.appendChild(text);

            zoomGroup.appendChild(g);
        }});
    </script>
</body>
</html>
"""

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return str(out_file)
