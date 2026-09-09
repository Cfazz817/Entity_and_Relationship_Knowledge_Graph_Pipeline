# SQLAlchemy 2.0 Architectural Querying Reference

This document provides a rigorous, step-by-step breakdown of the mechanics behind SQLAlchemy 2.0 querying. It details the internal translation from Python Abstract Syntax Trees (AST) to PostgreSQL execution, tailored specifically to the models defined in the `entity_pipeline` architecture.

---

## 1. The Core Paradigm: Statement Construction vs. Execution

The fundamental shift in SQLAlchemy 2.0 is the strict separation of statement construction from statement execution. In legacy SQLAlchemy (1.x), the `Session.query()` object conflated both concerns. In 2.0, you construct an immutable SQL representation (an AST) via `select()` and separately hand it to the `Session` for execution.

**Why is this necessary?** 
This architecture guarantees that the statement structure is completely database-agnostic until compilation. It allows statements to be cached efficiently, prevents implicit query execution, and standardizes the API across both asynchronous and synchronous database drivers.

---

## 2. Line-by-Line Breakdown: Basic Query Execution

To understand how queries interact with the database, we must trace the entire lifecycle of a basic fetch operation.

```python
1: from sqlalchemy import select
2: from app.models.entity import Entity
3:
4: stmt = select(Entity).where(Entity.primary_name == "Acme Corp")
5: result = session.execute(stmt)
6: entity = result.scalars().first()
```

### Step-by-Step Analysis

*   **Line 4: Statement Construction**
    *   `select(Entity)`: The `select()` function initializes a `Select` object. The ORM mapper inspects the `Entity` class, identifies its mapped `__tablename__` (`entities`), and prepares the internal structure to select all mapped columns.
    *   `Entity.primary_name == "Acme Corp"`: The `primary_name` attribute on the `Entity` class is an `InstrumentedAttribute`. When the Python `__eq__` operator (`==`) is evaluated, it does not compare strings. Instead, it triggers a Python operator overload that generates a `BinaryExpression` AST node representing the equality condition.
    *   `.where(...)`: This method appends the generated `BinaryExpression` to the `Select` object's internal WHERE clause collection.

*   **Line 5: Compilation and Execution**
    *   `session.execute(stmt)`: The `Session` takes the `Select` AST and passes it to the dialect compiler (in this project, the PostgreSQL compiler). 
    *   The compiler traverses the AST and generates a parameterized SQL string: `SELECT entities.id, entities.primary_name, ... FROM entities WHERE entities.primary_name = %s`.
    *   The `Session` checks out an active connection from the engine's connection pool.
    *   The compiled string and the parameter `("Acme Corp",)` are passed to the underlying DBAPI driver (e.g., `psycopg2`). The database processes the query and returns raw rows.
    *   `execute()` returns a `Result` object, which encapsulates a database cursor pointing to the unconsumed rows.

*   **Line 6: ORM Hydration and Result Extraction**
    *   `result.scalars()`: A raw `Result` yields tuples (e.g., `(EntityObject,)`). The `scalars()` method instructs the result cursor to extract the first element of each tuple, effectively stripping the tuple wrapping.
    *   **The Hydration Process:** Because the query targeted an ORM entity, SQLAlchemy intercepts the raw database row. It instantiates a new Python `Entity` object, populates its attributes with the row data, and places the instance into the `Session`'s Identity Map (a cache of all active objects in the transaction).
    *   `.first()`: This consumes exactly one row from the cursor. Once the row is consumed and hydrated, the underlying database cursor is closed to free server-side resources. If no rows exist, it safely returns `None`.

---

## 3. PostgreSQL Dialect Integration: JSONB Querying

The `Entity` model utilizes a `metadata_` column mapped to PostgreSQL's native `JSONB` data type. Querying JSONB requires specialized operator compilation to leverage PostgreSQL's binary JSON capabilities.

```python
1: stmt = select(Entity).where(
2:     Entity.metadata_["source"].astext == "wikipedia"
3: )
```

### Step-by-Step Analysis

*   **Line 2: JSONB Operator Compilation**
    *   `Entity.metadata_["source"]`: The bracket notation triggers the `__getitem__` operator overload on the SQLAlchemy JSON column element. The compiler translates this into the PostgreSQL JSON extraction operator: `metadata_ -> 'source'`.
    *   `.astext`: In PostgreSQL, the `->` operator returns a JSON primitive (which requires explicit type casting for string comparison). The `.astext` property alters the AST to compile using the `->>` operator, which extracts the JSON element directly as a PostgreSQL `text` type.
    *   `== "wikipedia"`: This generates the final equality condition. 
    *   **The Why:** This specific AST construction (`entities.metadata_ ->> 'source' = 'wikipedia'`) ensures that the query can utilize Generalized Inverted Indexes (GIN) on the PostgreSQL server, enabling extremely rapid document searches without requiring sequential table scans.

---

## 4. Eager Loading Mechanics: Mitigating the N+1 Problem

By default, relationships (like `Entity.outgoing_relationships`) are mapped as lazy loads. Accessing a lazy-loaded collection on an entity generates a new SQL query synchronously. If you query 100 entities and access their relationships, you generate 101 queries—the N+1 problem.

To solve this, you must specify eager loading strategies at the time of statement construction.

### `selectinload` for Collections (One-to-Many)

```python
1: from sqlalchemy.orm import selectinload
2:
3: stmt = select(Entity).options(selectinload(Entity.outgoing_relationships))
4: entities = session.scalars(stmt).all()
```

*   **The Mechanics of `selectinload`:**
    1.  **Primary Query Execution:** The `Session` executes the base `SELECT * FROM entities` query.
    2.  **Primary Key Collection:** As the `Entity` instances are hydrated, the ORM collects all of their primary keys (the UUIDs).
    3.  **Secondary Query Construction:** Before returning control to the caller, the ORM constructs a secondary query utilizing an `IN` clause: `SELECT * FROM relationships WHERE source_entity_id IN (<collected_uuids>)`.
    4.  **In-Memory Population:** The secondary query is executed. The ORM hydrates the resulting `Relationship` instances and routes them into the `outgoing_relationships` list of the correct parent `Entity` instances in memory.
*   **The Why:** Why use `selectinload` instead of a SQL `JOIN`? If an `Entity` has 50 relationships, a `JOIN` will return 50 rows from the database. The `Entity` data is duplicated across all 50 rows, drastically inflating network payload size and forcing the Python interpreter to deduplicate the data. `selectinload` retrieves the exact data required in two highly optimized queries, minimizing memory and bandwidth overhead.

### `joinedload` for Single Items (Many-to-One)

```python
1: from sqlalchemy.orm import joinedload
2: from app.models.relationship import Relationship
3:
4: stmt = select(Relationship).options(joinedload(Relationship.source_entity))
5: relationships = session.scalars(stmt).all()
```

*   **The Mechanics of `joinedload`:**
    *   When applied, `joinedload` modifies the primary AST. The compiler appends a `LEFT OUTER JOIN` clause to the statement: `SELECT relationships.*, entities.* FROM relationships LEFT OUTER JOIN entities ON relationships.source_entity_id = entities.id`.
    *   As the DBAPI returns the wide row containing both tables, the ORM hydration process simultaneously builds the `Relationship` instance and the `Entity` instance, linking them in memory.
*   **The Why:** Because a `Relationship` has exactly one `source_entity`, there is zero data duplication in the result set. The data is retrieved in a single round-trip without the overhead of tracking primary keys and issuing a secondary query.

---

## 5. Vector Similarity Search Compilation (pgvector)

The `Entity` model includes an `embedding` column defined as `Vector(3072)`. Searching this space requires interfacing with specialized extension operators.

```python
1: target_vector = [0.1, 0.2, ...] # 3072 dimensional vector
2: 
3: stmt = (
4:     select(Entity)
5:     .order_by(Entity.embedding.cosine_distance(target_vector))
6:     .limit(10)
7: )
8: nearest_entities = session.scalars(stmt).all()
```

### Step-by-Step Analysis

*   **Line 5: Operator Generation**
    *   `.cosine_distance(target_vector)`: This method is provided by the `pgvector.sqlalchemy` extension. It generates a specialized AST node that compiles into the PostgreSQL cosine distance operator: `<=>`.
    *   The parameter `target_vector` is serialized from a Python list into a PostgreSQL vector string format (e.g., `'[0.1, 0.2, ...]'`) by the DBAPI type caster.
    *   The final compiled ORDER BY clause becomes: `ORDER BY entities.embedding <=> %s`.
*   **The Why:** Relational databases utilize B-Tree indexes, which fundamentally cannot process high-dimensional spatial similarity. `pgvector` introduces Hierarchical Navigable Small World (HNSW) and Inverted File with Flat Compression (IVFFlat) indexes. By placing the `<=>` operator directly in the `ORDER BY` clause, you explicitly instruct the PostgreSQL query planner to traverse the HNSW graph index rather than executing a sequential table scan. This drops the search time complexity from $O(N)$ to $O(\log N)$, allowing real-time similarity resolution across millions of entities.
