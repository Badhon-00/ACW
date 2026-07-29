---
name: arrowspace
description: Spectral vector search using graph Laplacian eigenstructure. Use when cosine/L2 similarity misses latent structure in your embeddings.
---

# ArrowSpace

Spectral vector search that augments nearest-neighbour search with graph Laplacian features. Computes a Laplacian over the item graph and uses the Rayleigh quotient to produce a λτ (lambda-tau) score per item, enabling search that respects both semantic similarity and structural role.

## When to Use This Skill

- Cosine or L2 similarity misses latent structure in your embeddings
- You want graph-based retrieval with spectral awareness
- You need to characterise the spectral properties of an embedding space
- You are building RAG pipelines where contextual role matters alongside semantic content

## What This Skill Does

1. **Spectral Graph Construction**: Builds a weighted graph over your embedding vectors using Minkowski distance with configurable kernel width.
2. **Laplacian Eigenanalysis**: Computes the graph Laplacian and its Rayleigh quotient to produce per-item λτ scores.
3. **Spectral Retrieval**: Ranks items by λτ score, surfacing results that are both semantically close and structurally central.

## How to Use

### Basic Usage

```bash
pip install arrowspace
```

```python
from arrowspace import ArrowSpaceBuilder
import numpy as np

items = np.array([[0.1, 0.2, 0.3],
                  [0.0, 0.5, 0.1],
                  [0.9, 0.1, 0.0]], dtype=np.float64)

graph_params = {"eps": 0.2, "k": 6, "topk": 3, "p": 2.0, "sigma": 1.0}
aspace = ArrowSpaceBuilder(items, graph_params=graph_params).build()

lambdas = aspace.lambdas()           # scores indexed by insertion order
sorted_res = aspace.lambdas_sorted()  # (score, index) pairs ascending
```

### Advanced Usage

Tune graph parameters for your specific dataset:

```python
# For high-dimensional embeddings (e.g., 768-dim BERT):
graph_params = {"eps": 0.5, "k": 15, "topk": 10, "p": 2.0, "sigma": None}

# For low-dimensional embeddings (e.g., 2-d UMAP):
graph_params = {"eps": 0.1, "k": 5, "topk": 3, "p": 2.0, "sigma": None}
```

## Example

**User**: "Find the most structurally central items in this embedding space"

```python
scores = aspace.lambdas()
top5 = np.argsort(scores)[-5:]
```

**Output**: Returns indices of the 5 items with highest λτ scores — items that are both semantically relevant and structurally central to the graph.

## Tips

- Normalise embeddings to unit norm before passing to ArrowSpace
- Start with eps proportional to 1/sqrt(dim)
- Use k between 3 and 25; default heuristic is N/50
- Set sigma=None for automatic kernel width selection
- Higher λτ = more structurally central + semantically aligned

## Common Use Cases

- RAG retrieval where contextual role matters alongside content similarity
- Scientific data analysis of embedding space topology
- Outlier detection via low λτ scores (structurally peripheral items)
- Dataset deduplication through spectral clustering
