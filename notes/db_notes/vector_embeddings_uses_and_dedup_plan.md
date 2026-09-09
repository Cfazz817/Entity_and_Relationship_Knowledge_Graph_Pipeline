# Vector Embeddings: Alternative Uses and Deduplication Plan

## 1. What Else Can Vector Embeddings Be Used For?

Beyond entity resolution (deduplication), the 3072-dimensional embeddings stored in your database capture the semantic essence of your entities. This unlocks several advanced knowledge graph capabilities:

* **Semantic Search (RAG - Retrieval-Augmented Generation):** You can query your database by concept rather than keyword. A search for "mid-century medical researchers" will mathematically align with the vectors of people like "Albert Sabin" or "Louis Pasteur", even if those exact search terms don't exist in their entity descriptions.
* **Relationship Prediction (Link Prediction):** If two entities are clustered very closely together in vector space but lack an explicit edge in the `relationships` table, you can programmatically flag them as "likely related" or "missing connection."
* **Automated Classification:** By establishing the "average vector" of a known category (e.g., "Journalist"), you can scan your database to find all entities that fall within a certain distance of that average, automatically tagging them with the correct `entity_type_id`.
* **Visual Clustering:** Using dimensionality reduction tools (like UMAP), you can map your 3072D vectors down to 2D or 3D, creating a visual map of your entire knowledge graph where related entities naturally form visual neighborhoods.

---

## 2. Saved Implementation Plan: Safe Deduplication

To avoid disrupting the active data pipeline, deduplication should be run after the primary data ingestion is complete. We will use a safe, two-step approach.

### Prerequisites
Since the project uses `uv`, we will add `numpy` and/or `scikit-learn` to the environment when we are ready to build this, as doing vector math in memory via Python is much faster than running tens of thousands of cross-joins in the database.

### Step 1: `scripts/find_duplicates.py` (Dry Run / Discovery)
1. **Fetch:** Pulls all `Entity.id`, `Entity.primary_name`, and `Entity.embedding` from the database into memory using `app.database.SessionLocal`.
2. **Calculate Similarity:** Uses a fast pairwise cosine similarity matrix on the vectors to find entities that are extremely close (e.g., > 0.95 similarity).
3. **Cluster:** Groups these highly similar entities together (e.g., `["Ante Pavelic", "Ante Pavelich", "Ante Pavelitch"]`).
4. **Canonical Selection:** Accepts a command-line flag at runtime (e.g., `--strategy=frequent` or `--strategy=oldest`) to automatically select the "winner" (the canonical entity to keep).
5. **Export:** Saves the proposed groups and canonical selections to `data/proposed_merges.json` so you can manually review and edit them before any destructive operations occur.

### Step 2: `scripts/apply_merges.py` (Execution)
1. **Load:** Reads the `proposed_merges.json` file.
2. **Update Relationships:** For each merge group, runs an `UPDATE relationships` SQL command to change any `source_entity_id` or `target_entity_id` that points to a duplicate, re-pointing it to the canonical entity ID.
3. **Delete Duplicates:** Safely `DELETE`s the duplicate entity records from the `entities` table.
4. **Transaction Safety:** Wraps the update and delete operations in a strict database transaction so that if anything fails, it automatically rolls back, preventing orphaned relationships.
