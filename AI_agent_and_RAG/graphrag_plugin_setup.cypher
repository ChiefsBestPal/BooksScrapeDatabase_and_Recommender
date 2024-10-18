// ==============================================================
// NEO4J DESKTOP + GRAPHRAG PLUGIN - READY-TO-USE CYPHER SCRIPTS STEP BY STEP
// (AuraDB with GCP or Neo4J Bloom could be good options for quick to production GraphDB interfaces!)
//
// For Neo4j 5.12.0+ with GenAI/GraphRAG Plugin
// ==============================================================

// ================================================================
// BOILERPLATE ONLY. YOU SHOULD TAILOR DEPENDING ON SCHEMAS, REQUIREMENTS, CLOUD CONFIGS, USER PRIORITIES
// ================================================================

// --------------------------------------------------------------
// #1 CREATE VECTOR INDEX FOR SEMANTIC SEARCH OR/AND 'PART-TEXT'
// --------------------------------------------------------------

// Create vector index on Book descriptions (384 dimensions for all-MiniLM-L6-v2)
CALL db.index.vector.createNodeIndex(
  'book-description-embeddings',
  'Book',
  'descriptionEmbedding',
  384,
  'cosine'
);

// For larger embeddings (OpenAI ada-002: 1536 dimensions)
CALL db.index.vector.createNodeIndex(
  'book-description-embeddings-large',
  'Book',
  'descriptionEmbedding',
  1536,
  'cosine'
);

// Create vector index on Book titles (for title-based semantic search)
CALL db.index.vector.createNodeIndex(
  'book-title-embeddings',
  'Book',
  'titleEmbedding',
  384,
  'cosine'
);

// Verify indexes created
SHOW INDEXES;


// -------------------------------------------------
// #2 GENERATE EMBEDDINGS USING GRAPHRAG PLUGIN
// -------------------------------------------------

// Option A: Using GenAI Plugin with OpenAI (if plugin installed)
// Generate embeddings for book descriptions
CALL {
  MATCH (b:Book)
  WHERE b.description IS NOT NULL 
    AND b.descriptionEmbedding IS NULL
  RETURN b
  LIMIT 100
}
CALL genai.vector.encodeBatch(
  [b IN collect(b) | b.description],
  'OpenAI',
  {model: 'text-embedding-ada-002'}
) YIELD index, vector
WITH collect({index: index, vector: vector}) AS vectors
UNWIND range(0, size(vectors)-1) AS idx
MATCH (b:Book)
WHERE b.description IS NOT NULL
  AND b.descriptionEmbedding IS NULL
WITH b, vectors[idx].vector AS embedding
SKIP idx LIMIT 1
SET b.descriptionEmbedding = embedding
RETURN count(b) AS embeddingsGenerated;

// Option B: For batch processing with progress tracking
CALL apoc.periodic.iterate(
  "MATCH (b:Book) WHERE b.description IS NOT NULL AND b.descriptionEmbedding IS NULL RETURN b",
  "CALL genai.vector.encode(b.description, 'OpenAI', {model: 'text-embedding-ada-002'}) 
   YIELD vector 
   SET b.descriptionEmbedding = vector",
  {batchSize: 50, parallel: false}
) YIELD batches, total
RETURN batches, total;


// ----------------------------------------------------------------
// #3 SEMANTIC SEARCH QUERIES
// ----------------------------------------------------------------

// Search for books similar to a query using vector similarity
:param query => "epic fantasy with dragons and magic"

CALL genai.vector.encode($query, 'OpenAI', {model: 'text-embedding-ada-002'}) 
YIELD vector AS queryVector
CALL db.index.vector.queryNodes(
  'book-description-embeddings',
  10,
  queryVector
) YIELD node, score
RETURN node.title AS title,
       node.description AS description,
       node.averageRating AS rating,
       score AS similarity
ORDER BY score DESC;


// ----------------------------------------------------------------
// #4 HYBRID SEARCH (Vector + Graph Traversal)
// ----------------------------------------------------------------

// Find similar books AND their related authors/series
:param query => "science fiction space opera"

CALL genai.vector.encode($query, 'OpenAI') YIELD vector AS queryVector
CALL db.index.vector.queryNodes('book-description-embeddings', 10, queryVector) 
YIELD node AS book, score
MATCH (book)<-[:WROTE]-(author:Author)
OPTIONAL MATCH (book)-[:PART_OF_SERIES]->(series:Series)
OPTIONAL MATCH (book)-[:BELONGS_TO_GENRE]->(genre:Genre)
RETURN book.title AS title,
       author.person_name AS author,
       series.series_name AS series,
       collect(DISTINCT genre.genre_name) AS genres,
       book.averageRating AS rating,
       score AS similarity
ORDER BY score DESC;


// ----------------------------------------------------------------
// #5 GRAPHRAG QUESTION ANSWERING
// ----------------------------------------------------------------

// Use GenAI Plugin for natural language Q&A over graph
:param question => "What are the highest rated fantasy books with strong female characters?"

CALL genai.chat.ask(
  $question,
  {
    systemPrompt: "You are a book recommendation expert with access to a comprehensive literature database.",
    retrievalQuery: "
      MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
      WHERE g.genre_name CONTAINS 'Fantasy'
        AND b.averageRating > 4.0
      OPTIONAL MATCH (b)-[:FEATURES_CHARACTER]->(c:Character)
      RETURN b.title, b.description, b.averageRating, collect(c.character_name) AS characters
      ORDER BY b.averageRating DESC
      LIMIT 10
    "
  }
) YIELD answer, context
RETURN answer, context;


// ----------------------------------------------------------------
// #6 CONTEXTUAL RETRIEVAL FOR RAG
// ----------------------------------------------------------------

// Retrieve relevant context for a query using semantic + keyword search
:param userQuery => "mystery novels set in Victorian London"

// SETUP (LIBs, KGs, vector, comp-index tune): Get semantic matches
CALL genai.vector.encode($userQuery, 'OpenAI') YIELD vector AS queryVector
CALL db.index.vector.queryNodes('book-description-embeddings', 20, queryVector) 
YIELD node AS book, score AS semanticScore

// QUERY: Combine with keyword search
WITH book, semanticScore
WHERE book.description CONTAINS 'Victorian' 
   OR book.description CONTAINS 'London'
   OR book.description CONTAINS 'mystery'
MATCH (book)-[:SET_IN_PLACE]->(place:Place)
MATCH (book)-[:BELONGS_TO_GENRE]->(genre:Genre)
MATCH (book)<-[:WROTE]-(author:Author)
RETURN book.title AS title,
       author.person_name AS author,
       place.place_name AS setting,
       genre.genre_name AS genre,
       book.averageRating AS rating,
       book.description AS description,
       semanticScore
ORDER BY semanticScore DESC, book.averageRating DESC
LIMIT 5;


// ----------------------------------------------------------------
// #7 MULTI-HOP REASONING WITH GRAPHRAG
// ----------------------------------------------------------------

// Find books through complex graph patterns with semantic understanding
:param query => "books similar to Harry Potter but for adults"

// Generate embedding for query
CALL genai.vector.encode($query, 'OpenAI') YIELD vector AS queryVector

// Find Harry Potter
MATCH (hp:Book)
WHERE hp.title CONTAINS 'Harry Potter'
WITH hp, queryVector

// Find similar books through multiple paths
MATCH (hp)-[:BELONGS_TO_GENRE]->(g:Genre)<-[:BELONGS_TO_GENRE]-(similar:Book)
WHERE similar <> hp
  AND similar.pageCount > 400  // Adult novels tend to be longer
  AND similar.averageRating > 4.0

// Also find books with similar themes/characters
OPTIONAL MATCH (hp)-[:FEATURES_CHARACTER]->(c:Character)<-[:FEATURES_CHARACTER]-(similar)

// Get semantic similarity
WITH DISTINCT similar, queryVector
WHERE similar.descriptionEmbedding IS NOT NULL
WITH similar, 
     gds.similarity.cosine(queryVector, similar.descriptionEmbedding) AS semanticScore

// Enrich with metadata
MATCH (similar)<-[:WROTE]-(author:Author)
OPTIONAL MATCH (similar)-[:PART_OF_SERIES]->(series:Series)
RETURN similar.title AS title,
       author.person_name AS author,
       series.series_name AS series,
       similar.averageRating AS rating,
       similar.pageCount AS pages,
       semanticScore
ORDER BY semanticScore DESC, rating DESC
LIMIT 10;


// ----------------------------------------------------------------
// #8 REVIEWER INFLUENCE + SEMANTIC RECOMMENDATIONS
// ----------------------------------------------------------------

// Find influential reviewers who liked similar books
:param userPreferences => "dark fantasy with complex characters"

CALL genai.vector.encode($userPreferences, 'OpenAI') YIELD vector AS prefVector
CALL db.index.vector.queryNodes('book-description-embeddings', 20, prefVector) 
YIELD node AS likedBook, score

WITH likedBook, score
WHERE score > 0.7

// Find reviewers who gave high ratings to these books
MATCH (likedBook)<-[review:REVIEWED]-(reviewer:Reviewer)
WHERE review.rating >= 4.0

// Find what else they highly rated
MATCH (reviewer)-[otherReview:REVIEWED]->(otherBook:Book)
WHERE otherReview.rating >= 4.5
  AND otherBook <> likedBook
  AND otherBook.descriptionEmbedding IS NOT NULL

// Check semantic similarity of their recommendations
WITH otherBook, 
     avg(otherReview.rating) AS avgReviewRating,
     count(DISTINCT reviewer) AS influencerCount,
     gds.similarity.cosine(prefVector, otherBook.descriptionEmbedding) AS semanticMatch
WHERE influencerCount >= 3

MATCH (otherBook)<-[:WROTE]-(author:Author)
RETURN otherBook.title AS recommendation,
       author.person_name AS author,
       otherBook.averageRating AS rating,
       avgReviewRating AS influencerAvgRating,
       influencerCount,
       semanticMatch
ORDER BY semanticMatch DESC, influencerAvgRating DESC
LIMIT 10;


// ----------------------------------------------------------------
// #9 CYPHER WITH LLM CHAIN (GRAPHRAG PLUGIN)
// ----------------------------------------------------------------

// Use LLM to generate Cypher from natural language, then execute
CALL genai.cypher.generate(
  "Find the top 5 authors who have written the most highly-rated fantasy series",
  {
    schema: "
      Nodes: Book, Author, Series, Genre
      Relationships: (Author)-[:WROTE]->(Book)-[:PART_OF_SERIES]->(Series), 
                     (Book)-[:BELONGS_TO_GENRE]->(Genre)
    "
  }
) YIELD cypher
CALL apoc.cypher.run(cypher, {}) YIELD value
RETURN value;


// ----------------------------------------------------------------
// #10 CONVERSATIONAL RAG WITH MEMORY/CTX WINDOW/SCORE TABLES etc...
// Good for latent space or mutli-file ctx ... but Be careful of token cost + 'overfitting'
// ----------------------------------------------------------------

// Multi-turn conversation with context retention
// Turn 1: Initial query
CALL genai.chat.ask(
  "What are some good sci-fi books?",
  {
    conversationId: 'session-123',
    retrievalQuery: "
      MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
      WHERE g.genre_name CONTAINS 'Science Fiction'
        AND b.averageRating > 4.0
      RETURN b.title, b.description, b.averageRating
      ORDER BY b.averageRating DESC
      LIMIT 10
    "
  }
) YIELD answer, conversationId
RETURN answer;

// Turn 2: Follow-up (remembers previous context)
CALL genai.chat.ask(
  "What about space operas specifically?",
  {
    conversationId: 'session-123',  // Same conversation ID
    retrievalQuery: "
      MATCH (b:Book)-[:BELONGS_TO_GENRE]->(g:Genre)
      WHERE g.genre_name CONTAINS 'Science Fiction'
        AND (b.description CONTAINS 'space' OR b.description CONTAINS 'galaxy')
        AND b.averageRating > 4.0
      RETURN b.title, b.description
      LIMIT 10
    "
  }
) YIELD answer
RETURN answer;


// ----------------------------------------------------------------
// #11 GRAPH-AUGMENTED GENERATION (GAG)
// ----------------------------------------------------------------

// Retrieve graph structure and use in prompt
:param question => "Recommend books based on my reading history"
:param userId => 12345

// Get user's reading history
MATCH (u:User {id: $userId})-[r:REVIEWED|RATED]->(b:Book)
WITH collect(b) AS readBooks

// Find similar books through graph patterns
UNWIND readBooks AS read
MATCH (read)-[:BELONGS_TO_GENRE]->(g:Genre)<-[:BELONGS_TO_GENRE]-(rec:Book)
WHERE NOT rec IN readBooks
  AND rec.averageRating > 4.0
WITH rec, count(*) AS genreOverlap
ORDER BY genreOverlap DESC
LIMIT 20

// Prepare context for LLM
MATCH (rec)<-[:WROTE]-(author:Author)
OPTIONAL MATCH (rec)-[:PART_OF_SERIES]->(series:Series)
WITH collect({
  title: rec.title,
  author: author.person_name,
  series: series.series_name,
  rating: rec.averageRating,
  description: rec.description
}) AS recommendations

// Generate personalized explanation
CALL genai.chat.complete(
  "Based on the user's reading history, explain why these books are good recommendations: " + 
  apoc.convert.toJson(recommendations),
  {
    systemPrompt: "You are a personalized book recommendation system. 
                   Provide thoughtful, detailed explanations for recommendations."
  }
) YIELD answer
RETURN answer AS personalizedRecommendations;


// ----------------------------------------------------------------
// #12 EXPORT RESULTS FOR NEO4J BROWSER VISUALIZATION
// ----------------------------------------------------------------

// Save query results as graph for visualization
:param userQuery => "epic fantasy series"

// Execute semantic search
CALL genai.vector.encode($userQuery, 'OpenAI') YIELD vector AS queryVector
CALL db.index.vector.queryNodes('book-description-embeddings', 10, queryVector) 
YIELD node AS book, score

// Build subgraph with relationships
WITH book, score
MATCH (book)<-[:WROTE]-(author:Author)
MATCH (book)-[:BELONGS_TO_GENRE]->(genre:Genre)
OPTIONAL MATCH (book)-[:PART_OF_SERIES]->(series:Series)
OPTIONAL MATCH (book)-[:FEATURES_CHARACTER]->(character:Character)

// Return full subgraph for visualization
RETURN book, author, genre, series, character, score
ORDER BY score DESC;


// ----------------------------------------------------------------
// #13 BATCH PROCESSING WITH ERROR HANDLING
// ----------------------------------------------------------------

// Generate embeddings with error handling and progress tracking
CALL apoc.periodic.iterate(
  "MATCH (b:Book) 
   WHERE b.description IS NOT NULL 
     AND b.descriptionEmbedding IS NULL 
   RETURN b",
  
  "CALL apoc.when(
     b.description IS NOT NULL,
     'CALL genai.vector.encode(b.description, \"OpenAI\") 
      YIELD vector 
      SET b.descriptionEmbedding = vector 
      RETURN b',
     'RETURN b',
     {b: b}
   ) YIELD value
   RETURN value",
  
  {
    batchSize: 100,
    parallel: false,
    retries: 3,
    errorHandler: "CONTINUE"
  }
) YIELD batches, total, errorMessages
RETURN batches, total, errorMessages;


// ----------------------------------------------------------------
// #14 PERFORMANCE MONITORING
// ----------------------------------------------------------------

// Check embedding generation status
MATCH (b:Book)
RETURN 
  count(b) AS totalBooks,
  count(b.descriptionEmbedding) AS booksWithEmbeddings,
  count(b.description) AS booksWithDescriptions,
  100.0 * count(b.descriptionEmbedding) / count(b) AS embeddingCoverage;

// Check vector index performance
CALL db.index.vector.queryNodes('book-description-embeddings', 10, [0.1, 0.2, 0.3, /* ... 384 values */]) 
YIELD node, score
RETURN count(*) AS resultsReturned;


// -------------------------------
// #15 CLEANUP AND MAINTENANCE 
// -------------------------------

// Drop vector index if needed
CALL db.index.vector.drop('book-description-embeddings');

// Clear embeddings (if regenerating with different model)
MATCH (b:Book)
REMOVE b.descriptionEmbedding;

// Reindex after bulk updates
CALL db.index.vector.rebuild('book-description-embeddings');


