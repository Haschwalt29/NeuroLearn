import numpy as np
from typing import List

# Minimal TF import, keep optional to avoid heavy deps during dev
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False


class TwinRLAgent:
    def __init__(self, state_dim: int, num_actions: int, lr: float = 1e-3):
        self.state_dim = state_dim
        self.num_actions = num_actions
        self.model = None
        if TF_AVAILABLE:
            self.model = self._build_model(state_dim, num_actions, lr)

    def _build_model(self, state_dim: int, num_actions: int, lr: float):
        inputs = keras.Input(shape=(state_dim,))
        x = keras.layers.Dense(64, activation='relu')(inputs)
        x = keras.layers.Dense(64, activation='relu')(x)
        outputs = keras.layers.Dense(num_actions, activation='linear')(x)
        model = keras.Model(inputs, outputs)
        model.compile(optimizer=keras.optimizers.Adam(lr), loss='mse')
        return model

    def select_action(self, state: np.ndarray, epsilon: float = 0.1) -> int:
        if not TF_AVAILABLE or self.model is None:
            return int(np.random.randint(0, self.num_actions))
        if np.random.rand() < epsilon:
            return int(np.random.randint(0, self.num_actions))
        q = self.model.predict(state[np.newaxis, :], verbose=0)[0]
        return int(np.argmax(q))

    def train_step(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, gamma: float = 0.95):
        if not TF_AVAILABLE or self.model is None:
            return
        q = self.model.predict(state[np.newaxis, :], verbose=0)
        q_next = self.model.predict(next_state[np.newaxis, :], verbose=0)
        target = q.copy()
        target[0, action] = reward + gamma * np.max(q_next)
        self.model.train_on_batch(state[np.newaxis, :], target)


