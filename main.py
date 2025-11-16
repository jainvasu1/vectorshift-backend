from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """
    Check if the graph formed by nodes and edges is a Directed Acyclic Graph (DAG).
    Uses topological sort algorithm.
    """
    if not nodes:
        return True  # Empty graph is a DAG
    
    if not edges:
        return True  # Graph with no edges is a DAG
    
    # Build adjacency list and in-degree count
    node_ids = {node.id for node in nodes}
    adjacency = {node_id: [] for node_id in node_ids}
    in_degree = {node_id: 0 for node_id in node_ids}
    
    for edge in edges:
        if edge.source in node_ids and edge.target in node_ids:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1
    
    # Find all nodes with in-degree 0
    queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
    processed = 0
    
    # Process nodes with no incoming edges
    while queue:
        current = queue.pop(0)
        processed += 1
        
        # Reduce in-degree of neighbors
        for neighbor in adjacency[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If we processed all nodes, it's a DAG
    # If there are cycles, some nodes will have in_degree > 0
    return processed == len(node_ids)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: PipelineRequest):
    """
    Parse the pipeline and return:
    - num_nodes: number of nodes
    - num_edges: number of edges
    - is_dag: whether the graph is a Directed Acyclic Graph
    """
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    is_dag_result = is_dag(pipeline.nodes, pipeline.edges)
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag_result
    }
