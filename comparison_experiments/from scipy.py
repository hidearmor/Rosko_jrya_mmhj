import numpy as np
import scipy as scipy

# Generate a sparse matrix
N = 5
density = 0.3
sparse_matrix = scipy.sparse.random(N, N, density=density, format='coo', random_state=42)

# Convert to dense matrix
dense_matrix = sparse_matrix.toarray()
print(dense_matrix)