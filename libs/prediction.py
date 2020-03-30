from utils import generate_board, ctimer
import numpy as np
from numba import njit
from scipy.spatial.distance import cdist
from lapsolver import solve_dense
import matplotlib.pyplot as plt
from skimage.io import imread
from tqdm import tqdm


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self, board, url_to_vec_path, pair_to_dist_path, invalid_guesses, alpha=0.9, beta=0.8, gamma=0.8, phi=1):
        """
        Parameters
        ----------
        board: json
            The current board state
        url_to_vec_path: str
            The path to the url_to_vec dictionary
        pair_to_dist_path: str
            The path to the pair_to_dist dictionary
        invalid_guesses: set
            Guesses which can't be used
        alpha: float
            The decay factor for the blue team
        beta: float
            The decay factor for the red team
        gamma: float
            The decay factor for the neutral team
        phi: float
            The decay factor for the assassin
        """
        self.board = board
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.phi = phi

        self.url_to_vec = np.load(url_to_vec_path, allow_pickle=True).item()
        self.pair_to_dist = np.load(pair_to_dist_path, allow_pickle=True)
        self.valid_guesses = list(set(self.url_to_vec.keys()).difference(invalid_guesses))

    @staticmethod
    @njit(fastmath=True)
    def calculate_dist_matrix(u, v, d):
        mat = np.zeros(shape=(u.shape[0], v.shape[0]), dtype=np.float32)
        for i in range(u.shape[0]):
            for j in range(v.shape[0]):
                mat[i][j] = d[u[i]][v[j]]
        return mat

    def earthmover(self, u, v):
        dist_matrix = self.calculate_dist_matrix(u, v, self.pair_to_dist)
        assignment = solve_dense(dist_matrix)
        score = np.mean(dist_matrix[assignment])
        return score

    def guess_score(self, guess):
        """
        Generate a score for a guess
        """
        blue, red, neutral = 1, 1, 1

        em_scores = []
        u = self.url_to_vec[guess]
        for picture in self.board:
            v = self.url_to_vec[picture['url']]
            # A bigger em score means a better connection
            em_scores.append(np.exp(-self.earthmover(u, v)))

        # Sort the scores in descending order
        sorted_idx = np.argsort(-np.array(em_scores))
        score = 0
        for i in sorted_idx:
            if self.board[i]['type'] == 'blue':
                delta = (self.alpha**blue)*em_scores[i]
                blue += 1
            elif self.board[i]['type'] == 'red':
                delta = -(self.beta**red)*em_scores[i]
                red += 1
            elif self.board[i]['type'] == 'neutral':
                delta = -(self.gamma**neutral)*em_scores[i]
                neutral += 1
            else:
                delta = -self.phi*em_scores[i]

            score += delta
            em_scores[i] = delta

        return score, em_scores

    def get_best_guess_and_scores(self):
        """
        Get the best guess and its scores
        """
        best_guess = ''
        best_em_scores = []
        best_score = -float('inf')
        for guess in tqdm(self.valid_guesses):
            score, em_scores = self.guess_score(guess)
            if score > best_score:
                best_guess = guess
                best_em_scores = em_scores
                best_score = score

        return best_guess, best_em_scores, best_score

    def display_board(self, best_guess, best_em_scores, shape=(5, 5)):
        urls = [picture['url'] for picture in self.board] + [best_guess]
        fig, ax = plt.subplots(shape[0] + 1, shape[1], figsize=(24, 24))
        for i in range(shape[0] + 1):
            for j in range(shape[1]):
                if i != shape[0]:
                    idx = shape[0]*i + j
                    image = imread(urls[idx])
                    ax[i][j].set_title(f'Score:{best_em_scores[idx]:.3f}', size=8)
                    ax[i][j].imshow(image)
                elif j == shape[1]//2:
                    image = imread(best_guess)
                    ax[i][j].imshow(image)
                ax[i][j].axis('off')
        fig.subplots_adjust(hspace=0.4)
        plt.show()


@ctimer
def main():
    url_to_vec_path = '../static/data/url_to_vec.npy'
    pair_to_dist_path = '../static/data/pair_to_dist.npy'
    board = generate_board(url_to_vec_path)
    invalid_guesses = set([picture['url'] for picture in board])
    predictor = Predictor(board, url_to_vec_path, pair_to_dist_path, invalid_guesses, alpha=0.4, beta=0.0, gamma=0.0, phi=0.0)
    best_guess, best_em_scores, best_score = predictor.get_best_guess_and_scores()

    sorted_idx = np.argsort(-np.abs(np.array(best_em_scores)))
    best_em_scores = np.array(best_em_scores)[sorted_idx]
    board_types = np.array([b['type'] for b in board])[sorted_idx]
    for t, s in zip(board_types, best_em_scores):
        print(f'Type:{t} || Score:{s:.3f}')
    predictor.display_board(best_guess, best_em_scores, shape=(5, 5))


if __name__ == "__main__":
    main()











