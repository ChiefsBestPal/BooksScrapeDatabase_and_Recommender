# 🤖 BookScrapeDB AI Agent: GraphRAG, HybridRAG, LLMchain, Cloud

**Natural Language → Knowledge Graph → Intelligent Recommendations**

A complete GraphRAG (Graph Retrieval-Augmented Generation) implementation for BookScrapeDB, combining Neo4j's graph database with modern LLMs for intelligent book discovery, author analysis, and market intelligence.

---

## 🎯 Features

- **🔍 Semantic Search**: Vector-based similarity search across 10M+ books
- **🧠 Natural Language Queries**: Ask questions in plain English, get graph-powered answers
- **📊 Multi-Source RAG**: Combines knowledge graph structure with LLM reasoning
- **🎨 Visual Analytics**: Neo4j Browser integration for interactive graph visualization
- **🔌 Multiple LLM Backends**: OpenAI, Anthropic, Google Vertex AI, Ollama (local), Mistral, and more
- **⚡ Production Ready**: Batch processing, error handling, progress tracking

---

## 🏗️ Architecture

```
User Query (Natural Language)
    ↓
[LLM] Generate Cypher Query
    ↓
[Neo4j] Execute on Knowledge Graph
    ↓
[Vector Search] Semantic Similarity
    ↓
[LLM] Generate Human Response
    ↓
Results + Graph Visualization
```

---

## 🚀 Quick Start

### Prerequisites

- **Neo4j Desktop 1.6.3+** or **Neo4j 5.12.0+**
- **Python 3.9+**
- **BookScrapeDB** data loaded (see main repo)

### Installation

```bash
# Clone the repository
git clone https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender.git
cd BooksScrapeDatabase_and_Recommender/rag

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Option 1: Local LLM (FREE - No API Keys)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1:8b-instruct-q4_K_M

# Run RAG system
python book_rag.py --llm ollama --model llama3.1:8b --interactive
```

### Option 2: OpenAI (Fastest Setup)

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run RAG system
python book_rag.py --llm openai --model gpt-3.5-turbo --interactive
```

### Option 3: Google Vertex AI

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Run RAG system
python book_rag.py --llm vertexai --interactive
```

---

## 📚 Usage Examples

### Interactive Mode: Try it!

```bash
python {__main__} --interactive

📚 Your question: What are the best fantasy series with dragons?

🔍 Querying knowledge graph...

📊 RESULTS:
1. A Song of Ice and Fire | Rating: 4.5 | Dragons, complex politics, epic scale
2. Earthsea Cycle | Rating: 4.3 | Classic dragon lore, wizard coming-of-age
3. Temeraire Series | Rating: 4.1 | Napoleonic wars with dragons

🔧 GENERATED CYPHER:
MATCH (b:Book)-[:PART_OF_SERIES]->(s:Series)
MATCH (b)-[:FEATURES_CHARACTER]->(c:Character)
WHERE c.character_name CONTAINS 'dragon'
  AND b.averageRating > 4.0
RETURN s.series_name, avg(b.averageRating) AS avgRating
ORDER BY avgRating DESC
LIMIT 10
```

### Single Query

```bash
python book_rag.py --query "Find highly rated sci-fi books about AI"
```

### Export for Neo4j Browser

```bash
python book_rag.py --query "Best mystery novels set in Victorian London" --export

✅ Cypher query exported to: rag_query.cypher
📋 Copy and paste into Neo4j Browser to visualize results
```

---

## 🎨 Neo4j Browser Visualization

### Method 1: Using Python-Generated Queries

1. Run: `python book_rag.py --query "your question" --export`
2. Open **Neo4j Browser**
3. Paste contents of `rag_query.cypher`
4. Click **▶ Run**
5. Switch between **Graph**, **Table**, and **Text** views

### Method 2: Using GraphRAG Plugin (Neo4j Desktop)

1. **Install GenAI Plugin**:
   - Neo4j Desktop → Graph Apps → GenAI Plugin

2. **Load Setup Script**:
   ```cypher
   // In Neo4j Browser, run:
   :play neo4j_graphrag_plugin_setup.cypher
   ```

3. **Run Natural Language Queries**:
   ```cypher
   CALL genai.chat.ask(
     "What are the top fantasy books with dragons?",
     {retrievalQuery: "..."}
   ) YIELD answer
   RETURN answer;
   ```

---

## 🧪 Generate Embeddings

### Quick Setup (Sentence Transformers - Local & Free)

```bash
# Generate embeddings for all books
python embeddings_setup.py \
  --embedding-type sentence-transformers \
  --embedding-model all-MiniLM-L6-v2 \
  --create-index \
  --generate-embeddings \
  --limit 10000

# Semantic search
python embeddings_setup.py \
  --query "epic fantasy with dragons" \
  --embedding-type sentence-transformers
```

### Production Setup (OpenAI)

```bash
python embeddings_setup.py \
  --embedding-type openai \
  --embedding-model text-embedding-3-small \
  --create-index \
  --generate-embeddings \
  --batch-size 50
```

### Google Vertex AI

```bash
python embeddings_setup.py \
  --embedding-type vertexai \
  --create-index \
  --generate-embeddings
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# LLM Selection (openai, anthropic, vertexai, ollama, mistral)
LLM_TYPE=ollama
LLM_MODEL=llama3.1:8b-instruct-q4_K_M

# Embeddings
EMBEDDING_TYPE=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# API Keys (if using commercial APIs)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
```

### YAML Configuration (config.yaml)

```yaml
neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "password"

llm:
  type: "ollama"
  model: "llama3.1:8b-instruct-q4_K_M"
  temperature: 0
  max_tokens: 500

embeddings:
  type: "sentence-transformers"
  model: "all-MiniLM-L6-v2"
  dimension: 384
```

---

## 📊 Supported LLMs

### Commercial APIs

| Provider | Models | Setup |
|----------|--------|-------|
| **OpenAI** | GPT-3.5, GPT-4, GPT-4-Turbo | `export OPENAI_API_KEY=...` |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | `export ANTHROPIC_API_KEY=...` |
| **Google** | Gemini Pro, PaLM 2 | `export GOOGLE_APPLICATION_CREDENTIALS=...` |
| **Mistral AI** | Mistral 7B, Mixtral 8x7B | `export MISTRAL_API_KEY=...` |
| **Cohere** | Command, Command-R | `export COHERE_API_KEY=...` |

### Local / Open Source

| Model | Size | Quantization | Command |
|-------|------|--------------|---------|
| **Llama 3.1** | 8B, 70B | Q4_K_M, Q5_K_M | `ollama pull llama3.1:8b-instruct-q4_K_M` |
| **Mistral** | 7B | Q4_K_M | `ollama pull mistral:7b-instruct-q4_K_M` |
| **Mixtral** | 8x7B | Q4_K_M | `ollama pull mixtral:8x7b-instruct-q4_K_M` |
| **Phi-3** | 3.8B | Q4_0 | `ollama pull phi3:3.8b` |
| **Qwen 2** | 7B | Q4_K_M | `ollama pull qwen2:7b-instruct-q4_K_M` |
| **Gemma** | 7B | Q4_0 | `ollama pull gemma:7b-instruct-q4_0` |

---

## 🎯 Use Cases

### For Readers

```bash
 --query "Find books similar to The Name of the Wind with strong magic systems"
```

### For Authors

```bash
 --query "Analyze the market for space opera series with female protagonists"
```

### For Publishers

```bash
 --query "What genres are trending in the last 6 months based on ratings and reviews?"
```

### For Researchers

```bash
 --query "Map the influence network of cyberpunk authors"
```

---

## 📊 Performance Tips

1. **Use Quantized Models**: `Q4_K_M` variants are 50% smaller with minimal quality loss
2. **Batch Embeddings**: Process 100-500 books at a time
3. **Index Optimization**: Ensure vector indexes are created before querying
4. **Make your agent query specific with clustering**: Depends if you have sequential data, pure graph, range-based etc... e.g. scoring profiles you will often use .avgRatings 
5. **Local LLMs**: Use Ollama for cost-free development and testing
---

## 🔗 Links

- **Main Repository**: https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender
- **Neo4j Documentation**: https://neo4j.com/docs/
- **LangChain Docs**: https://python.langchain.com/
- **Ollama**: https://ollama.com/

---

## 📞 Support

- **Issues**: https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender/issues
- **Discussions**: https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender/discussions

---

**⭐ Star this repo if you find it useful!**