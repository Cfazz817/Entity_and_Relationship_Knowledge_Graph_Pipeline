# Vector Embeddings and Entity Resolution

## What are Vector Embeddings?
At a high level, a vector embedding is a way of translating text (like a name, a description, or an entire article) into an array of numbers (a high-dimensional vector) using AI language models. 

Unlike traditional database matching that looks for exact character matches (where "John Doe" and "Jon Doe" are completely different strings), embeddings capture **semantic meaning**. Because AI models are trained on vast amounts of text, they understand that variations of names or terms often appear in similar contexts. When the text is converted into numbers, semantically similar concepts (or slight spelling variations of the same name) end up having vectors that are mathematically very close to each other in vector space.

## How are Vector Embeddings Used for Deduplication?
Embeddings are the foundation for **Entity Resolution (ER)**, but generating them is only the first step. A complete deduplication pipeline looks like this:

1. **Generation:** Pass entity names (and contextual descriptions) into an embedding model to generate vectors, which are then saved in the database (often using extensions like `pgvector` in PostgreSQL).
2. **Similarity Search / Blocking:** Calculate the mathematical distance (e.g., Cosine Similarity) between the vectors. Because comparing every single record to every other record is computationally expensive ($O(n^2)$), embeddings are often clustered into "blocks" of similar items.
3. **Clustering & Merging:** When vectors are extremely close (e.g., a similarity score > 0.95), a script flags them as duplicates. The system then merges them by picking one "Canonical Entity" and re-assigning all relationships (edges) from the duplicates to the canonical entity, before deleting the redundant records.

## Application to the Knowledge Graph Pipeline
If you are seeing variations like `Ante Pavelic`, `Ante Pavelich`, and `Ante Pavelitch` as separate entities in your SQL query results, it means the database is treating them as distinct strings. 

**Vector embeddings do not automatically normalize or merge data upon insertion.** If your pipeline has generated embeddings, it has successfully mapped these name variations to very close coordinates in vector space. However, to actually clean the database, a **Deduplication Job** must be run. This job queries the database for vectors that are grouped closely together and performs the SQL `UPDATE` and `DELETE` operations required to merge them into a single, unified entity record.
