import os
__doc__ = """
BookScrapeDB - Vertex AI + Neo4j Integration main core logic driver
Generate embeddings, sentiment analysis, and NLP processing

Base core logic for native Google cloud integrated Neo4j/Aura Graph DBs with Vertex AI services

Extend this logic freely on cloud instance of your Data Warehouse or data lakes/storage engine feed your AI context

Quick Start:
    python __main__ --generate-embeddings
    python __main__ --sentiment-analysis
    python __main__ --build-profiles
    
    etc... 
"""

from dotenv import load_dotenv # Use .env or similar. Never even on private clouds put raw keys or passwords

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from neo4j import GraphDatabase
import time

# Vertex AI imports (graceful fallback)
try:
    import vertexai
    from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
    from google.cloud import language_v1
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False
    print("Warning: Vertex AI not available. Install: pip install google-cloud-aiplatform google-cloud-language")


@dataclass
class ProcessingStats:
    """Track processing statistics"""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0


class VertexAINeo4jIntegration:
    """
    # Main
    # Extend in your warehouse instance/AI agent host
    # by using boilerplates of langchain + custom Embeddings for maximum control
    Integration layer between Google Vertex AI and Neo4j for BookScrapeDB
    """
    
    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        gcp_project: str = None,
        gcp_location: str = "us-central1"
    ):
        """Initialize connections to Neo4j and Vertex AI"""
        
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        
        # Vertex AI initialization
        if VERTEXAI_AVAILABLE:
            project = gcp_project or os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project:
                raise ValueError("GCP project required. Set GOOGLE_CLOUD_PROJECT env var")
            
            vertexai.init(project=project, location=gcp_location)
            
            # Initialize models
            self.embedding_model = TextEmbeddingModel.from_pretrained(
                "textembedding-gecko@003"
            )
            self.generation_model = TextGenerationModel.from_pretrained(
                "text-bison@002"
            )
            self.language_client = language_v1.LanguageServiceClient()
        else:
            print("⚠️  Vertex AI not initialized")
    
    # ================================================================
    # 1. EMBEDDINGS GENERATION
    # ================================================================
    
    def generate_book_embeddings(
        self,
        batch_size: int = 5,  # Vertex AI limit for gecko
        limit: Optional[int] = None
    ) -> ProcessingStats:
        """
        Generate embeddings for book descriptions
        
        Args:
            batch_size: Number of books per batch (max 5 for gecko)
            limit: Total number of books to process (None = all)
        """
        stats = ProcessingStats()
        
        print("📚 Generating book description embeddings...")
        
        while True:
            with self.driver.session() as session:
                # Fetch books without embeddings
                result = session.run("""
                    MATCH (b:Book)
                    WHERE b.description IS NOT NULL 
                      AND b.descriptionEmbedding IS NULL
                    RETURN b.book_id AS id, 
                           b.title AS title,
                           b.description AS text
                    LIMIT $batchSize
                """, batchSize=batch_size)
                
                books = [
                    {
                        "id": r["id"],
                        "title": r["title"],
                        "text": r["text"][:1000]  # Truncate to 1000 chars
                    }
                    for r in result
                ]
                
                if not books:
                    break
                
                try:
                    # Generate embeddings
                    texts = [b["text"] for b in books]
                    embeddings = self.embedding_model.get_embeddings(texts)
                    
                    # Store in Neo4j
                    session.run("""
                        UNWIND $data AS row
                        MATCH (b:Book {book_id: row.id})
                        SET b.descriptionEmbedding = row.embedding,
                            b.embeddingModel = 'textembedding-gecko@003',
                            b.embeddingDate = datetime()
                    """, data=[
                        {"id": b["id"], "embedding": emb.values}
                        for b, emb in zip(books, embeddings)
                    ])
                    
                    stats.successful += len(books)
                    stats.total_processed += len(books)
                    
                    print(f"  ✓ Processed {stats.total_processed} books", end="\r")
                    
                except Exception as e:
                    print(f"\n  ❌ Error processing batch: {e}")
                    stats.failed += len(books)
                    stats.total_processed += len(books)
                
                # Check limit
                if limit and stats.total_processed >= limit:
                    break
                
                # Rate limiting
                time.sleep(0.5)
        
        print(f"\n✅ Embeddings complete: {stats.successful} successful, {stats.failed} failed")
        return stats
    
    def generate_reader_profile_embeddings(
        self,
        batch_size: int = 5
    ) -> ProcessingStats:
        """Generate embeddings for reader interest profiles"""
        stats = ProcessingStats()
        
        print("👤 Generating reader profile embeddings...")
        
        with self.driver.session() as session:
            # Get reader profiles
            result = session.run("""
                MATCH (r:Reviewer)-[:HAS_PROFILE]->(p:ReaderProfile)
                WHERE p.topGenres IS NOT NULL
                  AND p.profileEmbedding IS NULL
                RETURN p.reviewer_id AS id,
                       p.topGenres AS genres,
                       p.avgRating AS rating,
                       p.genreDiversity AS diversity
                LIMIT $limit
            """, limit=batch_size * 10)
            
            profiles = list(result)
            
            # Process in batches
            for i in range(0, len(profiles), batch_size):
                batch = profiles[i:i + batch_size]
                
                try:
                    # Create text representation of profile
                    texts = [
                        f"Reader who enjoys {', '.join(p['genres'][:5])} with average rating {p['rating']:.1f}"
                        for p in batch
                    ]
                    
                    # Generate embeddings
                    embeddings = self.embedding_model.get_embeddings(texts)
                    
                    # Store in Neo4j
                    session.run("""
                        UNWIND $data AS row
                        MATCH (p:ReaderProfile {reviewer_id: row.id})
                        SET p.profileEmbedding = row.embedding,
                            p.embeddingModel = 'textembedding-gecko@003',
                            p.embeddingDate = datetime()
                    """, data=[
                        {"id": p["id"], "embedding": emb.values}
                        for p, emb in zip(batch, embeddings)
                    ])
                    
                    stats.successful += len(batch)
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    stats.failed += len(batch)
                
                stats.total_processed += len(batch)
                time.sleep(0.5)
        
        print(f"✅ Profile embeddings: {stats.successful} successful")
        return stats
    
    # ================================================================
    # 2. SENTIMENT ANALYSIS
    # ================================================================
    
    def analyze_review_sentiment(
        self,
        batch_size: int = 100,
        limit: Optional[int] = None
    ) -> ProcessingStats:
        """
        Analyze sentiment of book reviews using Vertex AI
        """
        stats = ProcessingStats()
        
        print("💭 Analyzing review sentiment...")
        
        while True:
            with self.driver.session() as session:
                # Fetch reviews without sentiment
                result = session.run("""
                    MATCH (r:Reviewer)-[rev:REVIEWED]->(b:Book)
                    WHERE rev.review_text IS NOT NULL
                      AND size(rev.review_text) > 50
                      AND rev.sentimentScore IS NULL
                    RETURN id(rev) AS relId,
                           rev.review_text AS text,
                           b.title AS bookTitle
                    LIMIT $batchSize
                """, batchSize=batch_size)
                
                reviews = list(result)
                
                if not reviews:
                    break
                
                for review in reviews:
                    try:
                        # Analyze sentiment with Vertex AI
                        document = language_v1.Document(
                            content=review["text"][:5000],  # API limit
                            type_=language_v1.Document.Type.PLAIN_TEXT
                        )
                        
                        sentiment = self.language_client.analyze_sentiment(
                            request={"document": document}
                        ).document_sentiment
                        
                        # Determine label
                        score = sentiment.score
                        if score > 0.25:
                            label = "positive"
                        elif score < -0.25:
                            label = "negative"
                        elif abs(sentiment.magnitude) < 0.5:
                            label = "neutral"
                        else:
                            label = "mixed"
                        
                        # Update Neo4j
                        session.run("""
                            MATCH ()-[rev]->()
                            WHERE id(rev) = $relId
                            SET rev.sentimentScore = $score,
                                rev.sentimentMagnitude = $magnitude,
                                rev.sentimentLabel = $label,
                                rev.sentimentProcessed = true
                        """, relId=review["relId"], 
                             score=score,
                             magnitude=sentiment.magnitude,
                             label=label)
                        
                        stats.successful += 1
                        
                    except Exception as e:
                        print(f"  ❌ Error analyzing review: {e}")
                        stats.failed += 1
                    
                    stats.total_processed += 1
                    
                    if stats.total_processed % 10 == 0:
                        print(f"  Processed {stats.total_processed} reviews", end="\r")
                
                # Check limit
                if limit and stats.total_processed >= limit:
                    break
                
                # Rate limiting
                time.sleep(0.1)
        
        print(f"\n✅ Sentiment analysis: {stats.successful} successful, {stats.failed} failed")
        return stats
    
    # ================================================================
    # 3. TEXT GENERATION & SUMMARIZATION
    # ================================================================
    
    def generate_book_summaries(
        self,
        batch_size: int = 10
    ) -> ProcessingStats:
        """Generate concise summaries from long descriptions"""
        stats = ProcessingStats()
        
        print("📝 Generating book summaries...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (b:Book)
                WHERE b.description IS NOT NULL
                  AND size(b.description) > 500
                  AND b.aiSummary IS NULL
                RETURN b.book_id AS id,
                       b.title AS title,
                       b.description AS description
                LIMIT $limit
            """, limit=batch_size)
            
            books = list(result)
            
            for book in books:
                try:
                    prompt = f"""Summarize this book description in 2-3 concise sentences:

{book['description'][:1000]}

Summary:"""
                    
                    response = self.generation_model.predict(
                        prompt,
                        max_output_tokens=150,
                        temperature=0.2
                    )
                    
                    summary = response.text.strip()
                    
                    # Store in Neo4j
                    session.run("""
                        MATCH (b:Book {book_id: $id})
                        SET b.aiSummary = $summary,
                            b.summaryModel = 'text-bison@002',
                            b.summaryDate = datetime()
                    """, id=book["id"], summary=summary)
                    
                    stats.successful += 1
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    stats.failed += 1
                
                stats.total_processed += 1
                time.sleep(0.5)  # Rate limiting
        
        print(f"✅ Summaries generated: {stats.successful}")
        return stats
    
    def generate_reader_insights(
        self,
        reviewer_id: int
    ) -> str:
        """Generate natural language insights about a reader's profile"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Reviewer {reviewer_id: $id})-[:HAS_PROFILE]->(p:ReaderProfile)
                MATCH (r)-[rev:REVIEWED]->(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
                WITH r, p, 
                     collect(DISTINCT g.genre_name)[0..5] AS genres,
                     avg(rev.rating) AS avgRating,
                     count(rev) AS reviewCount
                RETURN p.topGenres AS topGenres,
                       p.avgRating AS profileAvg,
                       p.reviewStyle AS style,
                       p.engagementLevel AS engagement,
                       genres,
                       avgRating,
                       reviewCount
            """, id=reviewer_id).single()
            
            if not result:
                return "Reader profile not found."
            
            prompt = f"""Generate a brief reader profile insight (2-3 sentences) based on this data:

Top Genres: {', '.join(result['topGenres'][:5])}
Average Rating: {result['avgRating']:.2f}/5.0
Review Style: {result['style']}
Engagement Level: {result['engagement']}
Total Reviews: {result['reviewCount']}

Profile Insight:"""
            
            response = self.generation_model.predict(
                prompt,
                max_output_tokens=150,
                temperature=0.3
            )
            
            return response.text.strip()
    
    # ================================================================
    # 4. TOPIC MODELING & THEME EXTRACTION
    # ================================================================
    
    def extract_review_topics(
        self,
        book_id: int,
        max_reviews: int = 50
    ) -> List[Dict[str, Any]]:
        """Extract main topics from book reviews"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (:Book {book_id: $bookId})<-[rev:REVIEWED]-()
                WHERE rev.review_text IS NOT NULL
                  AND size(rev.review_text) > 100
                RETURN rev.review_text AS text
                ORDER BY rev.likeCount DESC
                LIMIT $maxReviews
            """, bookId=book_id, maxReviews=max_reviews)
            
            reviews = [r["text"] for r in result]
            
            if not reviews:
                return []
            
            # Combine reviews for topic analysis
            combined_text = "\n\n".join(reviews[:10])  # Use top 10 reviews
            
            try:
                prompt = f"""Extract the 5 main themes/topics discussed in these book reviews:

{combined_text[:3000]}

Format as: Topic 1: [theme], Topic 2: [theme], etc.

Topics:"""
                
                response = self.generation_model.predict(
                    prompt,
                    max_output_tokens=200,
                    temperature=0.2
                )
                
                # Parse response into list
                topics_text = response.text.strip()
                topics = []
                for line in topics_text.split('\n'):
                    if ':' in line:
                        topic_name = line.split(':', 1)[1].strip()
                        topics.append({"topic": topic_name})
                
                return topics
                
            except Exception as e:
                print(f"Error extracting topics: {e}")
                return []
    
    # ================================================================
    # 5. SEMANTIC SEARCH QUERIES
    # ================================================================
    
    def semantic_book_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search books using natural language query"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.get_embeddings([query])[0]
        
        # Search in Neo4j
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes(
                    'book-description-embeddings',
                    $topK,
                    $queryEmbedding
                ) YIELD node, score
                
                MATCH (node)<-[:WROTE]-(author:Author)
                OPTIONAL MATCH (node)-[:BELONGS_TO_GENRE]->(genre:Genre)
                
                RETURN node.title AS title,
                       author.person_name AS author,
                       node.averageRating AS rating,
                       node.ratingsCount AS popularity,
                       collect(DISTINCT genre.genre_name) AS genres,
                       score AS similarity
                ORDER BY score DESC
            """, queryEmbedding=query_embedding.values, topK=top_k)
            
            return [dict(r) for r in result]
    
    def find_similar_readers(
        self,
        reviewer_id: int,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Find readers with similar taste profiles"""
        
        with self.driver.session() as session:
            # Get target reader's profile embedding
            result = session.run("""
                MATCH (r:Reviewer {reviewer_id: $id})-[:HAS_PROFILE]->(p:ReaderProfile)
                WHERE p.profileEmbedding IS NOT NULL
                RETURN p.profileEmbedding AS embedding
            """, id=reviewer_id).single()
            
            if not result:
                return []
            
            # Find similar profiles
            similar = session.run("""
                CALL db.index.vector.queryNodes(
                    'reader-profile-embeddings',
                    $topK,
                    $queryEmbedding
                ) YIELD node, score
                
                MATCH (node)<-[:HAS_PROFILE]-(reviewer:Reviewer)
                WHERE reviewer.reviewer_id <> $targetId
                
                RETURN reviewer.person_name AS name,
                       reviewer.followersCount AS followers,
                       node.topGenres AS genres,
                       node.avgRating AS avgRating,
                       node.engagementLevel AS engagement,
                       score AS similarity
                ORDER BY score DESC
            """, queryEmbedding=result["embedding"], 
                 topK=top_k + 1,  # +1 to exclude self
                 targetId=reviewer_id)
            
            return [dict(r) for r in similar]
    
    # ================================================================
    # 6. HYBRID RECOMMENDATIONS
    # ================================================================
    
    def hybrid_recommendations(
        self,
        reviewer_id: int,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Hybrid recommendations combining:
        - Collaborative filtering (graph patterns)
        - Content-based (embeddings)
        - Semantic understanding (LLM)
        """
        
        with self.driver.session() as session:
            # Get user's reading history
            history = session.run("""
                MATCH (r:Reviewer {reviewer_id: $id})-[rev:REVIEWED]->(b:Book)
                WHERE rev.rating >= 4.0
                RETURN b.book_id AS id,
                       b.title AS title,
                       b.descriptionEmbedding AS embedding
                ORDER BY rev.rating DESC, rev.created DESC
                LIMIT 10
            """, id=reviewer_id)
            
            liked_books = list(history)
            
            if not liked_books:
                return []
            
            # Calculate centroid of liked book embeddings
            embeddings = [b["embedding"] for b in liked_books if b["embedding"]]
            
            if not embeddings:
                return []
            
            centroid = [sum(col) / len(embeddings) for col in zip(*embeddings)]
            
            # Find books similar to centroid
            candidates = session.run("""
                CALL db.index.vector.queryNodes(
                    'book-description-embeddings',
                    50,
                    $centroid
                ) YIELD node, score AS semanticScore
                
                // Exclude already read
                WHERE NOT (node)<-[:REVIEWED]-(:Reviewer {reviewer_id: $userId})
                  AND node.averageRating > 3.5
                
                // Find collaborative signal
                MATCH (similar:Reviewer)-[:REVIEWED]->(node)
                WHERE similar <> (:Reviewer {reviewer_id: $userId})
                  AND EXISTS {
                    MATCH (similar)-[:REVIEWED]->(alsoLiked:Book)
                    WHERE alsoLiked.book_id IN $likedIds
                  }
                
                WITH node, semanticScore, count(DISTINCT similar) AS collaborativeScore
                
                // Get metadata
                MATCH (node)<-[:WROTE]-(author:Author)
                OPTIONAL MATCH (node)-[:BELONGS_TO_GENRE]->(genre:Genre)
                
                RETURN node.title AS title,
                       author.person_name AS author,
                       node.averageRating AS rating,
                       collect(DISTINCT genre.genre_name) AS genres,
                       semanticScore,
                       collaborativeScore,
                       (semanticScore * 0.6 + collaborativeScore * 0.04) AS hybridScore
                ORDER BY hybridScore DESC
                LIMIT $topK
            """, centroid=centroid,
                 userId=reviewer_id,
                 likedIds=[b["id"] for b in liked_books],
                 topK=top_k)
            
            return [dict(r) for r in candidates]
    
    # ================================================================
    # 7. BATCH PROCESSING & UTILITIES
    # ================================================================
    
    def build_all_profiles(self) -> ProcessingStats:
        """Complete pipeline: embeddings + sentiment + profiles"""
        print("🔄 Building complete reader profiles...\n")
        
        # Step 1: Generate book embeddings
        book_stats = self.generate_book_embeddings(batch_size=5, limit=1000)
        
        # Step 2: Analyze review sentiment
        sentiment_stats = self.analyze_review_sentiment(batch_size=100, limit=500)
        
        # Step 3: Calculate reader profiles
        with self.driver.session() as session:
            session.run("""
                // Run profile calculation queries from cypher file
                CALL apoc.periodic.iterate(
                    "MATCH (r:Reviewer)-[:HAS_PROFILE]->(p:ReaderProfile) RETURN r, p",
                    "MATCH (r)-[rev:REVIEWED]->(b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
                     WITH r, p, g, avg(rev.rating) AS avgRating, count(*) AS count
                     WITH r, p, collect({genre: g.genre_name, rating: avgRating, count: count}) AS prefs
                     SET p.topGenres = [pref IN prefs | pref.genre][0..10]",
                    {batchSize: 100}
                )
            """)
        
        # Step 4: Generate profile embeddings
        profile_stats = self.generate_reader_profile_embeddings(batch_size=5)
        
        print("\n✅ Profile building complete!")
        print(f"   Books: {book_stats.successful}")
        print(f"   Sentiment: {sentiment_stats.successful}")
        print(f"   Profiles: {profile_stats.successful}")
        
        return book_stats
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (b:Book)
                OPTIONAL MATCH ()-[r:REVIEWED]->()
                OPTIONAL MATCH (p:ReaderProfile)
                RETURN 
                    count(DISTINCT b) AS totalBooks,
                    count(DISTINCT b.descriptionEmbedding) AS booksWithEmbeddings,
                    count(DISTINCT r) AS totalReviews,
                    count(DISTINCT r.sentimentScore) AS reviewsWithSentiment,
                    count(DISTINCT p) AS totalProfiles,
                    count(DISTINCT p.profileEmbedding) AS profilesWithEmbeddings
            """).single()
            
            return dict(result)
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()


# ================================================================
# CLI INTERFACE
# ================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="BookScrapeDB Vertex AI Integration"
    )
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default="password")
    parser.add_argument("--gcp-project", help="GCP Project ID")
    parser.add_argument("--gcp-location", default="us-central1")
    
    # Actions
    parser.add_argument("--generate-embeddings", action="store_true")
    parser.add_argument("--sentiment-analysis", action="store_true")
    parser.add_argument("--build-profiles", action="store_true")
    parser.add_argument("--generate-summaries", action="store_true")
    parser.add_argument("--stats", action="store_true")
    
    # Query actions
    parser.add_argument("--search", help="Semantic search query")
    parser.add_argument("--recommend", type=int, help="Get recommendations for reviewer ID")
    parser.add_argument("--similar-readers", type=int, help="Find similar readers to ID")
    
    # Limits
    parser.add_argument("--limit", type=int, help="Limit number of items to process")
    parser.add_argument("--batch-size", type=int, default=5)
    
    args = parser.parse_args()
    
    # Initialize integration
    integration = VertexAINeo4jIntegration(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        gcp_project=args.gcp_project,
        gcp_location=args.gcp_location
    )
    
    try:
        if args.generate_embeddings:
            integration.generate_book_embeddings(
                batch_size=args.batch_size,
                limit=args.limit
            )
        
        if args.sentiment_analysis:
            integration.analyze_review_sentiment(
                batch_size=args.batch_size * 20,
                limit=args.limit
            )
        
        if args.build_profiles:
            integration.build_all_profiles()
        
        if args.generate_summaries:
            integration.generate_book_summaries(batch_size=args.batch_size * 2)
        
        if args.search:
            results = integration.semantic_book_search(args.search, top_k=10)
            print(f"\n🔍 Search results for: '{args.search}'\n")
            for i, book in enumerate(results, 1):
                print(f"{i}. {book['title']} by {book['author']}")
                print(f"   Rating: {book['rating']:.2f} | Similarity: {book['similarity']:.4f}")
                print(f"   Genres: {', '.join(book['genres'])}\n")
        
        if args.recommend:
            recs = integration.hybrid_recommendations(args.recommend, top_k=10)
            print(f"\n📚 Recommendations for reviewer {args.recommend}:\n")
            for i, book in enumerate(recs, 1):
                print(f"{i}. {book['title']} by {book['author']}")
                print(f"   Rating: {book['rating']:.2f} | Score: {book['hybridScore']:.4f}")
                print(f"   Genres: {', '.join(book['genres'])}\n")
        
        if args.similar_readers:
            similar = integration.find_similar_readers(args.similar_readers, top_k=10)
            print(f"\n👥 Readers similar to {args.similar_readers}:\n")
            for i, reader in enumerate(similar, 1):
                print(f"{i}. {reader['name']} ({reader['followers']} followers)")
                print(f"   Similarity: {reader['similarity']:.4f}")
                print(f"   Genres: {', '.join(reader['genres'][:5])}\n")
        
        if args.stats:
            stats = integration.get_stats()
            print("\n📊 Processing Statistics:\n")
            print(f"Books: {stats['booksWithEmbeddings']}/{stats['totalBooks']} with embeddings")
            print(f"Reviews: {stats['reviewsWithSentiment']}/{stats['totalReviews']} with sentiment")
            print(f"Profiles: {stats['profilesWithEmbeddings']}/{stats['totalProfiles']} with embeddings")
        
        if not any([args.generate_embeddings, args.sentiment_analysis, args.build_profiles,
                    args.generate_summaries, args.search, args.recommend, args.similar_readers,
                    args.stats]):
            parser.print_help()
    
    finally:
        integration.close()


if __name__ == "__main__":
    main()