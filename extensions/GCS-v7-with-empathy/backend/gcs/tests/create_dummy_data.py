import numpy as np

def create_test_graph(path):
    adj = np.eye(4, dtype=np.float32)
    np.savez(path, adjacency_matrix=adj)

def create_test_deap(path):
    eeg = np.random.randn(5, 4, 10)       # 5 samples, 4 nodes, 10 timesteps
    physio = np.random.randn(5, 3)        # 5 samples, 3 physio features
    voice = np.random.randn(5, 128)       # 5 samples, 128 voice features
    valence = np.random.uniform(0, 1, (5,))
    arousal = np.random.uniform(0, 1, (5,))
    np.savez(path, eeg=eeg, physio=physio, voice=voice, valence=valence, arousal=arousal)

if __name__ == "__main__":
    import os
    os.makedirs("tests", exist_ok=True)
    create_test_graph("tests/test_graph.npz")
    create_test_deap("tests/test_deap.npz")
    print("Dummy test data created in tests/")
