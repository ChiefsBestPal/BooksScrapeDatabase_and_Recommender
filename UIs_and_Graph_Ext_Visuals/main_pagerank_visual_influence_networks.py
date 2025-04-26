"""
Version 2.0
Main Driver BookScrapeDB PageRank & Network Visualizations using data directly from Neo4j Graph Database
Interactive analysis of influence networks: Authors, Reviewers, Books

GDS Graphs/projects and other cypher queries shoudl be much more complex and parameterized
These are just base versions and proven base working formulas. Adjust to need
NB: formulas e.g. normalization/scaling of values into weights/heatmap colors, influence statistical models

TODO: Make seperate files for: 
TODO            - Dataclasses, Enums, Configs
TODO            - Main classes
TODO            - Tests, integrators/connectors
Supports:
  - Neo4j GDS PageRank algorithms
  - Interactive visualization (Pyvis, Plotly)
  - Export to CSV/Parquet for Spark/other tools
  - Multiple network types (Author, Reviewer, Book influence)

Quick Examples:
     --network author --algorithm pagerank --visualize
     --network reviewer --algorithm betweenness --export parquet
"""

import os
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
import sklearn as sk
import networkx as nx
from neo4j import GraphDatabase
import json
import pyspark
from functools import wraps
from dotenv import load_dotenv
import random
import colorsys

load_dotenv(r"./.neo4j.env") #! NB: neo4j env/conf file should be in CWD !

# Visualization libraries
try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# ============
# DATA MODELS (TODO: TO BE CONFIG-EXTENDED?)
# ============

@dataclass
class NetworkNode:
    """Represents a node in the influence network"""
    id: str
    label: str
    node_type: str  # 'author', 'reviewer', 'book', 'genre'
    pagerank_score: float = 0.0
    betweenness_score: float = 0.0
    closeness_score: float = 0.0
    degree_score: int = 0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class NetworkEdge:
    """Represents an edge in the influence network"""
    source: str
    target: str
    relationship_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
            
# ##################=#####################
# NEO4J PAGERANK CALCULATOR
# ##################=#####################

class Neo4jPageRankCalculator:
    """Calculate PageRank and other centrality measures in Neo4j using GDS"""
    
    def __init__(
        self,
        uri: str ,
        username: str,
        password: str
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def create_author_influence_projection(self) -> str:
        """Create projection for author influence network"""
        #? REMOVED:  a.author_id as author_id, a.person_name as name (GDS DOESNT SUPPORT STRING PROPERTIES IN PROJECTIONS)
        query = """
        CALL gds.graph.project.cypher(
            'authorInfluenceGraph',
            'MATCH (a:Author) RETURN id(a) as id',
            'MATCH (a1:Author)-[:WROTE]->(:Book)<-[:WROTE]-(a2:Author)
            WHERE a1 <> a2
            RETURN id(a1) as source, id(a2) as target, count(*) as weight'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            print(f"✓ Created projection: {record['graphName']}")
            print(f"  Nodes: {record['nodeCount']}, Relationships: {record['relationshipCount']}")
            return record['graphName']
        
    def create_reviewer_influence_projection(self) -> str:
        """Create projection for reviewer influence network"""
        #? REMOVED:  r.reviewer_id as reviewer_id, r.person_name as name (GDS DOESNT SUPPORT STRING PROPERTIES IN PROJECTIONS)
        query = """
        CALL gds.graph.project.cypher(
            'reviewerInfluenceGraph',
            'MATCH (r:Reviewer) RETURN id(r) as id',
            'MATCH (r1:Reviewer)-[rev1:REVIEWED]->(b:Book)<-[rev2:REVIEWED]-(r2:Reviewer)
             WHERE r1 <> r2
             RETURN id(r1) as source, id(r2) as target, 
                    (rev1.likeCount + rev2.likeCount + 1) as weight'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            print(f"✓ Created projection: {record['graphName']}")
            return record['graphName']
    
    def create_book_influence_projection(self) -> str:
        """Create projection for book influence network"""
        query = """
        CALL gds.graph.project.cypher(
            'bookInfluenceGraph',
            'MATCH (b:Book) RETURN id(b) as id, b.book_id as book_id, b.title as title',
            'MATCH (b1:Book)-[:BELONGS_TO_GENRE]->(:Genre)<-[:BELONGS_TO_GENRE]-(b2:Book)
             WHERE b1 <> b2
             RETURN id(b1) as source, id(b2) as target, 1 as weight
             UNION
             MATCH (b1:Book)-[:PART_OF_SERIES]->(:Series)<-[:PART_OF_SERIES]-(b2:Book)
             WHERE b1 <> b2
             RETURN id(b1) as source, id(b2) as target, 3 as weight'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            print(f"✓ Created projection: {record['graphName']}")
            return record['graphName']
    
    def calculate_pagerank(
        self,
        graph_name: str,
        dampening_factor: float = 0.85,
        iterations: int = 20
    ) -> str:
        """Calculate PageRank scores"""
        query = """
        CALL gds.pageRank.write(
            $graphName,
            {
                maxIterations: $iterations,
                dampingFactor: $dampeningFactor,
                writeProperty: 'pagerank_score'
            }
        )
        YIELD nodePropertiesWritten, ranIterations
        RETURN nodePropertiesWritten, ranIterations
        """
        with self.driver.session() as session:
            result = session.run(
                query,
                graphName=graph_name,
                iterations=iterations,
                dampeningFactor=dampening_factor
            )
            record = result.single()
            print(f"✓ PageRank calculated")
            print(f"  Nodes updated: {record['nodePropertiesWritten']}")
            print(f"  Iterations: {record['ranIterations']}")
            print(f"  Damping factor: {dampening_factor}")
            return graph_name
    
    def calculate_betweenness_centrality(
        self,
        graph_name: str
    ):
        """Calculate Betweenness Centrality (importance by connectivity)"""
        query = f"""
        CALL gds.betweenness.write(
            '{graph_name}',
            {{writeProperty: 'betweenness_score'}}
        )
        YIELD nodePropertiesWritten
        RETURN nodePropertiesWritten
        """
        with self.driver.session() as session:
            result = session.run(query)
            print(f"✓ Betweenness Centrality calculated: {result.single()['nodePropertiesWritten']} nodes")
    
    def calculate_closeness_centrality(
        self,
        graph_name: str
    ):
        """Calculate Closeness Centrality (average distance to all nodes)"""
        query = f"""
        CALL gds.closeness.write(
            '{graph_name}',
            {{writeProperty: 'closeness_score'}}
        )
        YIELD nodePropertiesWritten
        RETURN nodePropertiesWritten
        """
        with self.driver.session() as session:
            result = session.run(query)
            print(f"✓ Closeness Centrality calculated: {result.single()['nodePropertiesWritten']} nodes")
    
    def get_top_nodes(
        self,
        node_type: str,
        metric: str = 'pagerank_score',
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """Get top nodes by specified metric"""
        query = f"""
        MATCH (n:{node_type})
        WHERE n.{metric} IS NOT NULL
        RETURN 
            n.person_name as name,
            n.book_id as id,
            n.title as title,
            n.{metric} as score,
            COALESCE(n.ratingsCount, 0) as popularity,
            COALESCE(n.averageRating, 0) as rating
        ORDER BY score DESC
        LIMIT {top_k}
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def get_network_data(
        self,
        node_type: str,
        relationship_types: List[str],
        limit_nodes: int = 100
    ) -> Tuple[List[NetworkNode], List[NetworkEdge]]:
        """Extract network data from Neo4j"""
        
        # Get nodes
        node_query = f"""
        MATCH (n:{node_type})
        WHERE n.pagerank_score IS NOT NULL
        RETURN 
            id(n) as node_id,
            COALESCE(n.person_name, n.title, n.genre_name) as label,
            n.pagerank_score as pagerank,
            n.betweenness_score as betweenness,
            n.closeness_score as closeness,
            COALESCE(n.averageRating, 0) as rating,
            COALESCE(n.ratingsCount, 0) as popularity
        ORDER BY pagerank DESC
        LIMIT {limit_nodes}
        """
        
        nodes = {}
        with self.driver.session() as session:
            result = session.run(node_query)
            for record in result:
                node = NetworkNode(
                    id=str(record['node_id']),
                    label=record['label'],
                    node_type=node_type,
                    pagerank_score=record['pagerank'] or 0.0,
                    betweenness_score=record['betweenness'] or 0.0,
                    closeness_score=record['closeness'] or 0.0,
                    properties={
                        'rating': record['rating'],
                        'popularity': record['popularity']
                    }
                )
                nodes[record['node_id']] = node
        
        # Get edges
        rel_types = ', '.join([f":{rel}" for rel in relationship_types])
        edge_query = f"""
        MATCH (a:{node_type})-[r{rel_types}]->(b:{node_type})
        WHERE a.pagerank_score IS NOT NULL AND b.pagerank_score IS NOT NULL
        RETURN id(a) as source, id(b) as target, type(r) as rel_type, 1 as weight
        """
        
        edges = []
        with self.driver.session() as session:
            result = session.run(edge_query)
            for record in result:
                if record['source'] in nodes and record['target'] in nodes:
                    edge = NetworkEdge(
                        source=str(record['source']),
                        target=str(record['target']),
                        relationship_type=record['rel_type'],
                        weight=record['weight']
                    )
                    edges.append(edge)
        
        return list(nodes.values()), edges
    
    
    def get_network_dataV2(
        self,
        node_type: str,
        relationship_types: List[str],
        limit_nodes: int = 100
    ) -> Tuple[List[NetworkNode], List[NetworkEdge]]:
        """Extract network data from Neo4j"""
        
        # Get nodes with elementId() instead of deprecated id()
        node_query = f"""
        MATCH (n:{node_type})
        WHERE n.pagerank_score IS NOT NULL
        RETURN 
            elementId(n) as node_id,
            COALESCE(n.person_name, n.title, n.genre_name) as label,
            n.pagerank_score as pagerank,
            n.betweenness_score as betweenness,
            n.closeness_score as closeness,
            COALESCE(n.averageRating, 0) as rating,
            COALESCE(n.ratingsCount, 0) as popularity
        ORDER BY pagerank DESC
        LIMIT {limit_nodes}
        """
        
        nodes = {}
        with self.driver.session() as session:
            result = session.run(node_query)
            for record in result:
                node = NetworkNode(
                    id=str(record['node_id']),
                    label=record['label'],
                    node_type=node_type,
                    pagerank_score=record['pagerank'] or 0.0,
                    betweenness_score=record['betweenness'] or 0.0,
                    closeness_score=record['closeness'] or 0.0,
                    properties={
                        'rating': record['rating'],
                        'popularity': record['popularity']
                    }
                )
                nodes[record['node_id']] = node
        
        # Get edges - handle different relationship patterns based on node type
        if node_type == "Author":
            # Authors are connected through books they co-authored
            edge_query = """
            MATCH (a:Author)-[:WROTE]->(b:Book)<-[:WROTE]-(c:Author)
            WHERE a <> c 
            AND a.pagerank_score IS NOT NULL 
            AND c.pagerank_score IS NOT NULL
            WITH a, c, count(b) as collaborations
            RETURN elementId(a) as source, 
                elementId(c) as target, 
                'COLLABORATED_ON' as rel_type, 
                collaborations as weight
            """
        elif node_type == "Reviewer":
            # Reviewers are connected through books they both reviewed
            edge_query = """
            MATCH (a:Reviewer)-[:REVIEWED]->(b:Book)<-[:REVIEWED]-(c:Reviewer)
            WHERE a <> c 
            AND a.pagerank_score IS NOT NULL 
            AND c.pagerank_score IS NOT NULL
            WITH a, c, count(b) as common_books
            RETURN elementId(a) as source, 
                elementId(c) as target, 
                'REVIEWED_SAME' as rel_type, 
                common_books as weight
            """
        else:  # Book
            # Books are connected through genres or series
            rel_types = '|'.join([f":{rel}" for rel in relationship_types])
            edge_query = f"""
            MATCH (a:Book)-[r:{rel_types}]->(n)<-[r2:{rel_types}]-(b:Book)
            WHERE a <> b 
            AND a.pagerank_score IS NOT NULL 
            AND b.pagerank_score IS NOT NULL
            RETURN elementId(a) as source, 
                elementId(b) as target, 
                type(r) as rel_type, 
                1 as weight
            """
        
        edges = []
        with self.driver.session() as session:
            result = session.run(edge_query)
            for record in result:
                if record['source'] in nodes and record['target'] in nodes:
                    edge = NetworkEdge(
                        source=str(record['source']),
                        target=str(record['target']),
                        relationship_type=record['rel_type'],
                        weight=record['weight']
                    )
                    edges.append(edge)
        
        print(f"✓ Extracted {len(nodes)} nodes and {len(edges)} edges")
        return list(nodes.values()), edges
     
    def close(self):
        self.driver.close()


# ================================================================
# NETWORK VISUALIZATION
# ================================================================

class NetworkVisualizer:
    """Create interactive network visualizations"""
    
    @staticmethod
    def create_pyvis_network(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_file: str = "network.html",
        metric: str = 'pagerank_score',
        directed: bool = True
    ):
        """Create interactive Pyvis visualization"""
        if not PYVIS_AVAILABLE:
            print("❌ Pyvis not installed. Install: pip install pyvis")
            return
        
        net = Network(
            directed=directed,
            height="750px",
            width="100%",
            physics=True #TODO: MAYBE PROBLEMATIC
        )
        
        # Add nodes with size based on PageRank
        for node in nodes:
            size = 10 + (node.pagerank_score * 100)  # Scale PageRank to size
            color = f"rgb({int(node.pagerank_score*255)}, 100, {int(255-node.pagerank_score*255)})"
            
            title = f"""
            <b>{node.label}</b><br>
            Type: {node.node_type}<br>
            PageRank: {node.pagerank_score:.6f}<br>
            Betweenness: {node.betweenness_score:.6f}<br>
            Closeness: {node.closeness_score:.6f}
            """
            
            net.add_node(
                node.id,
                label=node.label,
                title=title,
                size=size,
                color=color,
                physics=True
            )
        
        # Add edges
        for edge in edges:
            net.add_edge(
                edge.source,
                edge.target,
                weight=edge.weight,
                title=edge.relationship_type,
                color="rgba(100, 100, 100, 0.3)"
            )
        
        net.show(output_file)
        print(f"✅ Visualization saved to: {output_file}")
        return net
    
    @staticmethod
    def create_plotly_graph(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_file: str = "network_plotly.html",
        metric: str = 'pagerank_score'
    ):
        """Create Plotly interactive graph"""
        if not PLOTLY_AVAILABLE:
            print("❌ Plotly not installed. Install: pip install plotly")
            return
        
        # Build edge trace
        edge_x = []
        edge_y = []
        print(f"!!!!!!!!!!!!!!!!!!!!!!! NUMBER OF NODES={len(nodes)}, NUMBER OF EDGES={len(edges)}")
        for edge in edges:
            source_node = next((n for n in nodes if n.id == edge.source), None)
            target_node = next((n for n in nodes if n.id == edge.target), None)
            
            if source_node and target_node:
                edge_x.extend([source_node.pagerank_score, target_node.pagerank_score, None])
                edge_y.extend([source_node.betweenness_score, target_node.betweenness_score, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        
        # Build node trace
        node_x = [n.pagerank_score for n in nodes]
        node_y = [n.betweenness_score for n in nodes]
        node_color = [n.closeness_score for n in nodes]
        node_size = [10 + (n.pagerank_score * 100) for n in nodes]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(thickness=15, title='Closeness')
            ),
            text=[n.label for n in nodes],
            hoverinfo='text',
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='BookScrapeDB Influence Network - PageRank Analysis',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        fig.write_html(output_file)
        print(f"✅ Plotly visualization saved to: {output_file}")


# ================================================================
# DATA EXPORT
# ================================================================

class NetworkExporter:
    """Export network data to various formats"""
    
    @staticmethod
    def to_csv(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_dir: str = "./"
    ):
        """Export to CSV format"""
        # Nodes CSV
        nodes_data = [{
            'id': n.id,
            'label': n.label,
            'type': n.node_type,
            'pagerank_score': n.pagerank_score,
            'betweenness_score': n.betweenness_score,
            'closeness_score': n.closeness_score,
            'degree': n.degree_score,
            **n.properties
        } for n in nodes]
        
        nodes_df = pd.DataFrame(nodes_data)
        nodes_file = os.path.join(output_dir, 'network_nodes.csv')
        nodes_df.to_csv(nodes_file, index=False)
        print(f"✅ Nodes exported: {nodes_file}")
        
        # Edges CSV
        edges_data = [{
            'source': e.source,
            'target': e.target,
            'relationship': e.relationship_type,
            'weight': e.weight,
            **e.properties
        } for e in edges]
        
        edges_df = pd.DataFrame(edges_data)
        edges_file = os.path.join(output_dir, 'network_edges.csv')
        edges_df.to_csv(edges_file, index=False)
        print(f"✅ Edges exported: {edges_file}")
        
        return nodes_df, edges_df
    
    @staticmethod
    def to_parquet(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_dir: str = "./"
    ):
        """Export to Parquet format (for Spark/PySpark)"""
        try:
            # Nodes Parquet
            nodes_data = [{
                'id': n.id,
                'label': n.label,
                'type': n.node_type,
                'pagerank_score': float(n.pagerank_score),
                'betweenness_score': float(n.betweenness_score),
                'closeness_score': float(n.closeness_score),
                'degree': n.degree_score
            } for n in nodes]
            
            nodes_df = pd.DataFrame(nodes_data)
            nodes_file = os.path.join(output_dir, 'network_nodes.parquet')
            nodes_df.to_parquet(nodes_file)
            print(f"✅ Nodes exported: {nodes_file}")
            
            # Edges Parquet
            edges_data = [{
                'source': e.source,
                'target': e.target,
                'relationship': e.relationship_type,
                'weight': float(e.weight)
            } for e in edges]
            
            edges_df = pd.DataFrame(edges_data)
            edges_file = os.path.join(output_dir, 'network_edges.parquet')
            edges_df.to_parquet(edges_file)
            print(f"✅ Edges exported: {edges_file}")
            
            return nodes_df, edges_df
            
        except Exception as e:
            print(f"❌ Parquet export failed: {e}")
    
    @staticmethod
    def to_gexf(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_file: str = "network.gexf"
    ):
        """Export to GEXF format (compatible with Gephi, Cytoscape)"""
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node in nodes:
            G.add_node(
                node.id,
                label=node.label,
                type=node.node_type,
                pagerank=node.pagerank_score,
                betweenness=node.betweenness_score,
                closeness=node.closeness_score
            )
        
        # Add edges
        for edge in edges:
            G.add_edge(
                edge.source,
                edge.target,
                weight=edge.weight,
                relationship=edge.relationship_type
            )
        
        nx.write_gexf(G, output_file)
        print(f"✅ GEXF exported: {output_file} (open in Gephi/Cytoscape)")
    
    @staticmethod
    def to_json(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge],
        output_file: str = "network.json"
    ):
        """Export to JSON format"""
        data = {
            'nodes': [{
                'id': n.id,
                'label': n.label,
                'type': n.node_type,
                'pagerank_score': n.pagerank_score,
                'betweenness_score': n.betweenness_score,
                'closeness_score': n.closeness_score,
                'properties': n.properties
            } for n in nodes],
            'edges': [{
                'source': e.source,
                'target': e.target,
                'relationship': e.relationship_type,
                'weight': e.weight,
                'properties': e.properties
            } for e in edges]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ JSON exported: {output_file}")


# ================================================================
# ANALYSIS & INSIGHTS
# ================================================================

class NetworkAnalyzer:
    """Generate insights from network analysis"""
    
    @staticmethod
    def summarize_network(
        nodes: List[NetworkNode],
        edges: List[NetworkEdge]
    ) -> Dict[str, Any]:
        """Generate network summary statistics"""
        
        pagerank_scores = [n.pagerank_score for n in nodes]
        betweenness_scores = [n.betweenness_score for n in nodes]
        
        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'avg_pagerank': sum(pagerank_scores) / len(pagerank_scores) if pagerank_scores else 0,
            'max_pagerank': max(pagerank_scores) if pagerank_scores else 0,
            'min_pagerank': min(pagerank_scores) if pagerank_scores else 0,
            'avg_betweenness': sum(betweenness_scores) / len(betweenness_scores) if betweenness_scores else 0,
            'max_betweenness': max(betweenness_scores) if betweenness_scores else 0,
            'density': len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        }
    
    @staticmethod
    def find_influencers(
        nodes: List[NetworkNode],
        top_k: int = 10
    ) -> List[NetworkNode]:
        """Find top influencers by PageRank"""
        return sorted(nodes, key=lambda n: n.pagerank_score, reverse=True)[:top_k]
    
    @staticmethod
    def find_bridges(
        nodes: List[NetworkNode],
        top_k: int = 10
    ) -> List[NetworkNode]:
        """Find bridge nodes (high betweenness centrality)"""
        return sorted(nodes, key=lambda n: n.betweenness_score, reverse=True)[:top_k]
    
    @staticmethod
    def find_hubs(
        nodes: List[NetworkNode],
        top_k: int = 10
    ) -> List[NetworkNode]:
        """Find hub nodes (high closeness centrality)"""
        return sorted(nodes, key=lambda n: n.closeness_score, reverse=True)[:top_k]


# ================================================================
# CLI & MAIN EXECUTION
# ================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="BookScrapeDB PageRank Visualization")
    parser.add_argument("--test-funcs", action="store_true", help="Flag to run TEST functions and then return. Skips all")
    parser.add_argument("--network", choices=["author", "reviewer", "book"], 
                       default="author", help="Network type")
    parser.add_argument("--algorithm", choices=["pagerank", "betweenness", "closeness", "all"],
                       default="pagerank", help="Centrality algorithm")
    parser.add_argument("--visualize", action="store_true", help="Create visualizations")
    parser.add_argument("--viz-type", choices=["pyvis", "plotly", "both"],
                       default="pyvis", help="Visualization library")
    parser.add_argument("--export", choices=["csv", "parquet", "gexf", "json", "all"],
                       help="Export format")
    parser.add_argument("--analyze", action="store_true", help="Generate analysis")
    parser.add_argument("--limit", type=int, default=100, help="Limit nodes")
    parser.add_argument("--output-dir", default="./", help="Output directory")
    
    args = parser.parse_args()
    
    print("🚀 BookScrapeDB PageRank & Network Analysis\n")
    NEO4J_AUTH_ENV_ARGS = dict( 
        uri=f'bolt://{os.getenv(r"NEO4J_DEV_DBMS_IP_ADDR")}:{os.getenv(r"NEO4J_BOLT_PORT")}',
        username=os.getenv(r"NEO4J_DEV_DBMS_USER"),
        password=os.getenv(r"NEO4J_DEV_DBMS_PWD")
    )

    # Initialize calculator
    calc = Neo4jPageRankCalculator(
        **NEO4J_AUTH_ENV_ARGS
    )
    
    try:
        # Create projection
        print(f"📊 Building {args.network} influence network...\n")
        
        if args.network == "author":
            graph_name = calc.create_author_influence_projection()
            node_type = "Author"
            relationships = ["WROTE"]
        elif args.network == "reviewer":
            graph_name = calc.create_reviewer_influence_projection()
            node_type = "Reviewer"
            relationships = ["REVIEWED"]
        else:  # book
            graph_name = calc.create_book_influence_projection()
            node_type = "Book"
            relationships = ["BELONGS_TO_GENRE", "PART_OF_SERIES"]
        
        # Calculate centrality measures
        print(f"\n🔍 Calculating centrality measures...\n")
        
        if args.algorithm in ["pagerank", "all"]:
            calc.calculate_pagerank(graph_name)
        if args.algorithm in ["betweenness", "all"]:
            calc.calculate_betweenness_centrality(graph_name)
        if args.algorithm in ["closeness", "all"]:
            calc.calculate_closeness_centrality(graph_name)
        
        # Get network data
        print(f"\n📥 Extracting network data...\n")
        nodes, edges = calc.get_network_dataV2(node_type, relationships, args.limit)
        
        # Analysis
        if args.analyze:
            print("\n📈 Network Analysis:\n")
            summary = NetworkAnalyzer.summarize_network(nodes, edges)
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            print(f"\n🌟 Top Influencers (PageRank):")
            for i, node in enumerate(NetworkAnalyzer.find_influencers(nodes, 5), 1):
                print(f"  {i}. {node.label}: {node.pagerank_score:.6f}")
            
            print(f"\n🌉 Top Bridges (Betweenness):")
            for i, node in enumerate(NetworkAnalyzer.find_bridges(nodes, 5), 1):
                print(f"  {i}. {node.label}: {node.betweenness_score:.6f}")
        
        # Visualize
        if args.visualize:
            print(f"\n🎨 Creating visualizations...\n")
            if args.viz_type in ["pyvis", "both"]:
                NetworkVisualizer.create_pyvis_network(
                    nodes, edges,
                    output_file=os.path.join(args.output_dir, f"{args.network}_network.html"),
                    directed=True
                )
            if args.viz_type in ["plotly", "both"]:
                NetworkVisualizer.create_plotly_graph(
                    nodes, edges,
                    output_file=os.path.join(args.output_dir, f"{args.network}_network_plotly.html")
                )
        
        # Export
        if args.export:
            print(f"\n💾 Exporting data...\n")
            if args.export in ["csv", "all"]:
                NetworkExporter.to_csv(nodes, edges, args.output_dir)
            if args.export in ["parquet", "all"]:
                NetworkExporter.to_parquet(nodes, edges, args.output_dir)
            if args.export in ["gexf", "all"]:
                NetworkExporter.to_gexf(nodes, edges, 
                                       os.path.join(args.output_dir, f"{args.network}_network.gexf"))
            if args.export in ["json", "all"]:
                NetworkExporter.to_json(nodes, edges,
                                       os.path.join(args.output_dir, f"{args.network}_network.json"))
        
        print("\n✅ Complete!")
        
    finally:
        calc.close()


if __name__ == "__main__":
    main()