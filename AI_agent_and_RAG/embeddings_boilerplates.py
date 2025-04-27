import os
from abc import ABC, ABCMeta, abstractmethod
__doc__ = """
BookScrapeDB - Embeddings & Prompt Engineering Boilerplate
There are services and architecutre for this... 

## VECTORIZATION & KGs
Mongo DB atlas and Neo4j offer relatively good vector search... 
Otherwise consider full native or full integration with vertex AI cloud services...
There are LLM dense vectors templates for chains & LLMops here using models 
that can be small quantized models locally or online hosted-APi avaiable larger models

## HOST & DEPLOYMENT
DOCKER PORTS/NET: For ports/URL... Consider using docker networks for quick deployment

## OVERVIEW OF THIS MODULE
- Embedding classes:
    - Metaclass and Abstract class for base embedding provider OOP
    - Child classes Supports: OpenAI, Vertex AI, Sentence Transformers, Ollama (quantized & reduced param/local small models)

- Util:
    - PromptTemplateLoader
- Basic RAG:
    - VertexAIGraphRAG
    - Neo4jVectorSetup

### Quick Start
    python embeddings_setup.py --generate-embeddings
    python embeddings_setup.py --query "<context> Equally fan of historical works and high-fantasy worlds</context>fantasy books with northern europe mythical creatures"
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from neo4j import GraphDatabase
from deprecated import deprecated

import xml.etree.ElementTree as ET # From 2025 New version allowing prompt engineering XML full control 
                                   # Check compatibility and update librarie/dependencies accordingly

try:
    import vertexai
    from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
    from google.cloud import language_v1
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False
    print("Warning: Vertex AI not available. Install: pip install google-cloud-aiplatform google-cloud-language")


# ============================================
# EMBEDDINGS PROVIDERS META CLASS REGISTRY + BASE CLASS
# ============================================

class EmbeddingMeta(ABCMeta):
    """Metaclass enforcing required attributes in subclasses."""

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)
        # Skip check for base class itself
        if not any(b.__name__ == "EmbeddingProvider" for b in bases):
            # Enforce that 'model' attribute exists (either at class or instance level)
            if "model" not in namespace and not hasattr(cls, "model"):
                raise TypeError(
                    f"Class '{name}' must define a 'model' attribute or set it in __init__()."
                )
                
class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text into a vector"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts into vectors"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension"""
        pass

# ============================================
# EMBEDDINGS PROVIDERS
# ============================================
class SentenceTransformerEmbeddings(EmbeddingProvider):
    """Local embeddings using Sentence Transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError("Install: pip install sentence-transformers")
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    @property
    def dimension(self) -> int:
        return self._dimension


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embeddings (ada-002, text-embedding-3-small/large)"""
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model
            self._dimension = 1536 if "ada-002" in model else 1536  # Adjust based on model
        except ImportError:
            raise ImportError("Install: pip install openai")
    
    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]
    
    @property
    def dimension(self) -> int:
        return self._dimension


class VertexAIEmbeddings(EmbeddingProvider):
    """Google Vertex AI embeddings (textembedding-gecko, text-embedding-004)"""
    
    def __init__(
        self,
        model: str = "textembedding-gecko@003",
        project: Optional[str] = None,
        location: str = "us-central1"
    ):
        try:
            from vertexai.language_models import TextEmbeddingModel
            import vertexai
            
            project = project or os.getenv("gcp_project")
            vertexai.init(project=project, location=location)
            self.model = TextEmbeddingModel.from_pretrained(model)
            self._dimension = 768  # gecko default
        except ImportError:
            raise ImportError("Install: pip install google-cloud-aiplatform")
    
    def embed_text(self, text: str) -> List[float]:
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Vertex AI has batch limits (5 texts per request for gecko)
        embeddings = self.model.get_embeddings(texts[:5])
        return [emb.values for emb in embeddings]
    
    @property
    def dimension(self) -> int:
        return self._dimension


class OllamaEmbeddings(EmbeddingProvider):
    """Ollama local embeddings (nomic-embed-text, mxbai-embed-large)"""
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434"
    ):
        import requests
        self.model = model
        self.base_url = base_url
        self._dimension = 768  # nomic-embed-text default
        self.session = requests.Session()
    
    def embed_text(self, text: str) -> List[float]:
        import requests
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        return response.json()["embedding"]
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        return self._dimension


# ============================================
# NEO4J VECTOR INDEX SETUP (BASIC BOILERPLATE.... CUSTOMIZE FOR NEEDS ESPECIALLY AT LARGER SCALES)
# ============================================

class Neo4jVectorSetup:
    """Setup and manage Neo4j vector indexes for RAG"""
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password"
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def create_vector_index(
        self,
        index_name: str = "book-embeddings",
        node_label: str = "Book",
        property_name: str = "descriptionEmbedding",
        dimension: int = 384,
        similarity_metric: str = "cosine"
    ):
        """Create vector index in Neo4j 5.12+"""
        
        query = f"""
        CALL db.index.vector.createNodeIndex(
            '{index_name}',
            '{node_label}',
            '{property_name}',
            {dimension},
            '{similarity_metric}'
        )
        """
        
        with self.driver.session() as session:
            try:
                session.run(query)
                print(f"✅ Created vector index: {index_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ️  Vector index already exists: {index_name}")
                else:
                    raise e
    
    def generate_embeddings_batch(
        self,
        embedding_provider: EmbeddingProvider,
        batch_size: int = 100,
        limit: Optional[int] = None
    ):
        """Generate embeddings for books and store in Neo4j"""
        
        # Fetch books without embeddings
        query = """
        MATCH (b:Book)
        WHERE b.description IS NOT NULL 
          AND b.descriptionEmbedding IS NULL
        RETURN b.book_id AS id, b.description AS text
        """
        if limit:
            query += f" LIMIT {limit}"
        
        with self.driver.session() as session:
            result = session.run(query)
            books = [{"id": record["id"], "text": record["text"]} for record in result]
        
        print(f"📚 Generating embeddings for {len(books)} books...")
        
        # Process in batches
        for i in range(0, len(books), batch_size):
            batch = books[i:i + batch_size]
            texts = [book["text"][:1000] for book in batch]  # Truncate to 1000 chars
            
            # Generate embeddings
            embeddings = embedding_provider.embed_batch(texts)
            
            # Update Neo4j
            update_query = """
            UNWIND $data AS row
            MATCH (b:Book {book_id: row.id})
            SET b.descriptionEmbedding = row.embedding
            """
            
            data = [
                {"id": book["id"], "embedding": emb}
                for book, emb in zip(batch, embeddings)
            ]
            
            with self.driver.session() as session:
                session.run(update_query, data=data)
            
            print(f"  ✓ Processed batch {i//batch_size + 1}/{(len(books)-1)//batch_size + 1}")
        
        print("✅ Embeddings generation complete!")
    
    
    @deprecated(reason="Test only... Use GDS Neo4j, Google Cloud VertexAI/services, Hugging face hub+transformers or custom algs/models")
    def vector_similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        index_name: str = "book-embeddings"
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        query = f"""
        CALL db.index.vector.queryNodes(
            '{index_name}',
            $topK,
            $queryEmbedding
        ) YIELD node, score
        RETURN node.book_id AS book_id,
               node.title AS title,
               node.description AS description,
               node.averageRating AS rating,
               score
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, queryEmbedding=query_embedding, topK=top_k)
            return [dict(record) for record in result]
    
    def close(self):
        self.driver.close()

# ============================================
# BASE PROMPT LOADER - NO SPECIFIC TAG STRUCTURE
# Please extend for tag control based on e.g. Template.prompt.xml
# ============================================

class PromptTemplateLoader:
    """Loads prompt templates from an XML file."""

    def __init__(self, xml_path: str):
        self.templates = self._load_xml(xml_path)

    def _load_xml(self, path: str) -> Dict[str, str]:
        tree = ET.parse(path)
        root = tree.getroot()
        templates = {}
        for child in root:
            templates[child.tag] = child.text.strip()
        return templates

    def get(self, key: str) -> str:
        return self.templates.get(key, "")

# ============================================
# GRAPHRAG WITH VERTEX AI USING EMBEDDINGS CLASSES 
# ============================================

class VertexAIGraphRAG:
    """GraphRAG using Google Vertex AI + Neo4j"""

    def __init__(
        self,
        project: str,
        location: str = "us-central1",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        prompt_xml_path: str = "prompt_templates.xml"
    ):
        try:
            from vertexai.language_models import TextGenerationModel
            import vertexai

            vertexai.init(project=project, location=location)
            self.llm = TextGenerationModel.from_pretrained("text-bison@002")
            self.embeddings = VertexAIEmbeddings(project=project, location=location)
            self.neo4j = Neo4jVectorSetup(neo4j_uri, neo4j_user, neo4j_password)

            # Load XML templates
            self.prompts = PromptTemplateLoader(prompt_xml_path)

        except ImportError:
            raise ImportError("Install: pip install google-cloud-aiplatform")

    def query_book_basic(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Execute RAG query using Vertex AI"""

        # Generate query embedding
        query_embedding = self.embeddings.embed_text(question)

        # Retrieve relevant books from Neo4j
        results = self.neo4j.vector_similarity_search(query_embedding, top_k=top_k)

        # Format context
        context = "\n\n".join([
            f"Book: {r['title']}\nRating: {r['rating']}\nDescription: {r['description'][:300]}..."
            for r in results
        ])

        # Use template from XML
        prompt_template = self.prompts.get("BOOK_RECOMMENDATION")
        prompt = prompt_template.format(context=context, query=question)

        # Generate response using Vertex AI
        response = self.llm.predict(
            prompt,
            max_output_tokens=512,
            temperature=0.2
        )

        return {
            "answer": response.text,
            "context": results,
            "query_embedding_dim": len(query_embedding)
        }


# ==========
# MAIN CLI
# ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="BookScrapeDB Embeddings & RAG Setup")
    parser.add_argument("--embedding-type", choices=["sentence-transformers", "openai", "vertexai", "ollama"], 
                       default="sentence-transformers")
    parser.add_argument("--embedding-model", default="all-MiniLM-L6-v2")
    parser.add_argument("--generate-embeddings", action="store_true", 
                       help="Generate embeddings for all books")
    parser.add_argument("--create-index", action="store_true",
                       help="Create vector index in Neo4j")
    parser.add_argument("--query", help="Semantic search query")
    parser.add_argument("--limit", type=int, default=1000, 
                       help="Limit number of books to process")
    parser.add_argument("--batch-size", type=int, default=100)
    
    args = parser.parse_args()
    
    # Initialize embedding provider
    if args.embedding_type == "sentence-transformers":
        embeddings = SentenceTransformerEmbeddings(args.embedding_model)
    elif args.embedding_type == "openai":
        embeddings = OpenAIEmbeddings(args.embedding_model)
    elif args.embedding_type == "vertexai":
        embeddings = VertexAIEmbeddings()
    elif args.embedding_type == "ollama":
        embeddings = OllamaEmbeddings(args.embedding_model)
    
    print(f"📊 Using {args.embedding_type} embeddings (dim: {embeddings.dimension})")
    
    # Initialize Neo4j
    neo4j = Neo4jVectorSetup()
    
    # Create index
    if args.create_index:
        neo4j.create_vector_index(dimension=embeddings.dimension)
    
    # Generate embeddings
    if args.generate_embeddings:
        neo4j.generate_embeddings_batch(
            embeddings,
            batch_size=args.batch_size,
            limit=args.limit
        )
    
    # Semantic search
    if args.query:
        print(f"\n🔍 Searching for: {args.query}")
        query_embedding = embeddings.embed_text(args.query)
        results = neo4j.vector_similarity_search(query_embedding, top_k=10)
        
        print("\n Top Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Rating: {result['rating']:.2f} | Similarity: {result['score']:.4f}")
            print(f"   {result['description'][:150]}...")
    
    neo4j.close()


if __name__ == "__main__":
    main()
