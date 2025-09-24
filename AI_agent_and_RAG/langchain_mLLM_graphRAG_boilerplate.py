"""
BookScrapeDB RAG - LLM Chain GraphRAG Implementation
Compatible with Neo4j 5.12.0+ and Neo4j Desktop 1.6.3

See embeddings_boilerplates.py and others VertexAI and other

Usage:
    python {__main__ or driver}.py --query "Find highest rated fiction books indirectly, likely influenced by east asian cultures"
    python {__main__ or driver}.py --interactive
"""

import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import argparse
import json


try:
    from langchain_community.graphs import Neo4jGraph
    from langchain.chains import GraphCypherQAChain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not installed. Using basic mode.")

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class BookGraphRAG:
    """
    GraphRAG implementation for BookScrapeDB literature database.
    Supports multiple LLM backends and fallback modes.
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        llm_type: str = "openai", #TODO Make warnings to annonce local quantized LLMs needed if no more tokens for openAI
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None
    ):
        """
        Initialize GraphRAG system.
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            llm_type: 'openai', 'ollama', or 'basic'
            model: Model name (gpt-3.5-turbo, llama3.1:8b,qwen2.5:7B etc.)
            api_key: API key for commercial LLMs
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.llm_type = llm_type
        
        # Initialize Neo4j connection
        if LANGCHAIN_AVAILABLE:
            self.graph = Neo4jGraph(
                url=uri,
                username=username,
                password=password
            )
        else:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Initialize LLM
        self.llm = self._initialize_llm(llm_type, model, api_key)
        
        # Initialize RAG chain if LangChain available
        if LANGCHAIN_AVAILABLE and self.llm:
            self.chain = self._create_rag_chain()
        else:
            self.chain = None
    
    def _initialize_llm(self, llm_type: str, model: str, api_key: Optional[str]):
        """Initialize the appropriate LLM backend."""
        if llm_type == "openai" and OPENAI_AVAILABLE:
            return ChatOpenAI(
                temperature=0,
                model=model,
                openai_api_key=api_key or os.getenv("OPENAI_API_KEY")
            )
        elif llm_type == "ollama" and OLLAMA_AVAILABLE:
            return Ollama(model=model, temperature=0)
        else:
            print(f"Warning: {llm_type} not available. Using basic mode.")
            return None
    
    def _create_rag_chain(self):
        """Create the GraphCypherQA chain with custom prompt."""
        
        CYPHER_GENERATION_TEMPLATE = """You are a Neo4j Cypher expert for a comprehensive literature database called BookScrapeDB.

Database Schema:
===============

Node Types:
- Book: Contains title, description, averageRating, ratingsCount, pageCount, publishedDate, isbn_10, isbn_13, language
- Author: Contains person_name, avgRating, ratingsCount, reviewsCount, about, birthDate, deathDate
- Genre: Contains genre_name
- Series: Contains series_name
- Character: Contains character_name
- Place: Contains place_name
- Subject: Contains subject_name
- Publisher: Contains publisher_name
- Reviewer: Contains person_name, followersCount, isAuthor

Relationship Types:
- (Author)-[:WROTE]->(Book)
- (Book)-[:BELONGS_TO_GENRE]->(Genre)
- (Book)-[:PART_OF_SERIES]->(Series)
- (Book)-[:FEATURES_CHARACTER]->(Character)
- (Book)-[:SET_IN_PLACE]->(Place)
- (Book)-[:HAS_SUBJECT]->(Subject)
- (Book)-[:PUBLISHED_BY]->(Publisher)
- (Reviewer)-[:REVIEWED {{rating, review_text, likeCount, created, updated}}]->(Book)

Important Notes:
- Use averageRating for book ratings (float 0-5)
- Use ratingsCount for popularity metrics
- Date fields: publishedDate (date), created/updated (datetime)
- Always include LIMIT clause for large result sets
- Use DISTINCT when aggregating to avoid duplicates

User Question: {question}

Generate a valid Neo4j Cypher query to answer this question.
Return ONLY the Cypher query without explanations or markdown formatting.
"""

        cypher_prompt = PromptTemplate(
            template=CYPHER_GENERATION_TEMPLATE,
            input_variables=["question"]
        )
        
        return GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=cypher_prompt,
            return_intermediate_steps=True,
            allow_dangerous_requests=True  # Required for Neo4j 5.x
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a natural language query against the graph.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with 'result', 'cypher', and 'raw_results'
        """
        if self.chain:
            # Use LangChain GraphRAG
            try:
                response = self.chain.invoke({"query": question})
                return {
                    "result": response["result"],
                    "cypher": response.get("intermediate_steps", [{}])[0].get("query", "N/A"),
                    "raw_results": response.get("intermediate_steps", [{}])[0].get("context", [])
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "result": "Error executing query. Try simplifying your question.",
                    "cypher": "N/A"
                }
        else:
            # Fallback: Use predefined query templates
            return self._basic_query(question)
    
    def _basic_query(self, question: str) -> Dict[str, Any]:
        """Fallback query system using template matching."""
        question_lower = question.lower()
        
        # Template matching for common queries
        if "highest rated" in question_lower or "best" in question_lower:
            cypher = """
            MATCH (b:Book)
            WHERE b.averageRating IS NOT NULL
            RETURN b.title AS title, 
                   b.averageRating AS rating,
                   b.ratingsCount AS numRatings
            ORDER BY b.averageRating DESC, b.ratingsCount DESC
            LIMIT 10
            """
        elif "author" in question_lower and "most books" in question_lower:
            cypher = """
            MATCH (a:Author)-[:WROTE]->(b:Book)
            RETURN a.person_name AS author, 
                   count(b) AS bookCount,
                   avg(b.averageRating) AS avgRating
            ORDER BY bookCount DESC
            LIMIT 10
            """
        elif "genre" in question_lower:
            cypher = """
            MATCH (g:Genre)<-[:BELONGS_TO_GENRE]-(b:Book)
            RETURN g.genre_name AS genre,
                   count(b) AS bookCount,
                   avg(b.averageRating) AS avgRating
            ORDER BY bookCount DESC
            LIMIT 10
            """
        elif "series" in question_lower:
            cypher = """
            MATCH (s:Series)<-[:PART_OF_SERIES]-(b:Book)
            RETURN s.series_name AS series,
                   count(b) AS booksInSeries,
                   avg(b.averageRating) AS avgRating
            ORDER BY avgRating DESC
            LIMIT 10
            """
        else:
            cypher = """
            MATCH (b:Book)
            RETURN b.title AS title, b.averageRating AS rating
            ORDER BY b.averageRating DESC
            LIMIT 5
            """
        
        # Execute query
        with self.driver.session() as session:
            result = session.run(cypher)
            records = [dict(record) for record in result]
        
        return {
            "result": self._format_results(records),
            "cypher": cypher,
            "raw_results": records
        }
    
    def _format_results(self, records: List[Dict]) -> str:
        """Format query results into readable text."""
        if not records:
            return "No results found."
        
        lines = []
        for i, record in enumerate(records[:10], 1):
            line_parts = [f"{i}."]
            for key, value in record.items():
                if value is not None:
                    if isinstance(value, float):
                        line_parts.append(f"{key}: {value:.2f}")
                    else:
                        line_parts.append(f"{key}: {value}")
            lines.append(" | ".join(line_parts))
        
        return "\n".join(lines)
    
    def demo_queries(self) -> List[str]:
        """Return a list of demo queries to showcase capabilities."""
        return [
            "What are the highest rated fantasy books?",
            "Which authors have written the most books?",
            "What are the most popular book series?",
            "Show me books with dragons as characters",
            "Find books set in medieval times with high ratings",
            "What genres are most popular in the database?",
            "Which reviewers have the most followers?",
            "Show me recent highly-rated science fiction books"
        ]
    
    def interactive_mode(self):
        """Run interactive query session."""
        print("\n" + "="*70)
        print("BookScrapeDB GraphRAG - Interactive Mode")
        print("="*70)
        print(f"\nConnected to: {self.uri}")
        print(f"LLM Backend: {self.llm_type}")
        print("\nType 'demo' to see example queries")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("\n📚 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if question.lower() == 'demo':
                    print("\n🎯 Demo Queries:")
                    for i, q in enumerate(self.demo_queries(), 1):
                        print(f"  {i}. {q}")
                    continue
                
                if not question:
                    continue
                
                print("\n🔍 Querying knowledge graph...")
                response = self.query(question)
                
                print("\n" + "-"*70)
                print("📊 RESULTS:")
                print("-"*70)
                print(response["result"])
                
                print("\n" + "-"*70)
                print("🔧 GENERATED CYPHER:")
                print("-"*70)
                print(response["cypher"])
                print("-"*70)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def export_for_browser(self, question: str, output_file: str = "rag_query.cypher"):
        """
        Export query as Cypher file for Neo4j Browser execution.
        
        Args:
            question: Natural language question
            output_file: Output filename
        """
        response = self.query(question)
        
        with open(output_file, 'w') as f:
            f.write(f"// Question: {question}\n")
            f.write(f"// Generated by BookScrapeDB GraphRAG\n\n")
            f.write(response["cypher"])
        
        print(f"\n✅ Cypher query exported to: {output_file}")
        print(f"📋 Copy and paste into Neo4j Browser to visualize results")
        
        return response
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'driver'):
            self.driver.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BookScrapeDB GraphRAG - Natural language queries for book database"
    )
    parser.add_argument(
        "--uri",
        default="bolt://localhost:7687",
        help="Neo4j connection URI"
    )
    parser.add_argument(
        "--username",
        default="neo4j",
        help="Neo4j username"
    )
    parser.add_argument(
        "--password",
        default="password",
        help="Neo4j password"
    )
    parser.add_argument(
        "--llm",
        choices=["openai", "ollama", "basic"],
        default="basic",
        help="LLM backend to use"
    )
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="Model name (gpt-3.5-turbo, llama3.1:8b, etc.)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for commercial LLMs"
    )
    parser.add_argument(
        "--query",
        help="Single query to execute"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export query to .cypher file for Neo4j Browser"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo queries"
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = BookGraphRAG(
        uri=args.uri,
        username=args.username,
        password=args.password,
        llm_type=args.llm,
        model=args.model,
        api_key=args.api_key
    )
    
    try:
        if args.interactive:
            rag.interactive_mode()
        elif args.demo:
            print("\n🎯 Running Demo Queries...\n")
            for question in rag.demo_queries()[:3]:  # Run first 3
                print(f"\n{'='*70}")
                print(f"Q: {question}")
                print('='*70)
                response = rag.query(question)
                print(f"\n{response['result']}\n")
                print(f"Cypher: {response['cypher']}\n")
        elif args.query:
            response = rag.query(args.query)
            if args.export:
                rag.export_for_browser(args.query)
            else:
                print(f"\n{response['result']}\n")
                print(f"Cypher:\n{response['cypher']}")
        else:
            parser.print_help()
    finally:
        rag.close()


if __name__ == "__main__":
    main()