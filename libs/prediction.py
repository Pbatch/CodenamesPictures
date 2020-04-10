from utils import generate_board
import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self, board, ids_to_dist_path, invalid_guesses, alpha=0.9, beta=0.8, gamma=0.8):
        """
        Parameters
        ----------
        board: json
            The current board state
        ids_to_dist_path: str
            The path to the ids_to_dist nd-array
        invalid_guesses: set
            Guesses which can't be used
        alpha: float
            The decay factor for the blue team
        beta: float
            The decay factor for the red team
        gamma: float
            The decay factor for the neutral team
        """
        self.board = [p for p in board if not p['active']]
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.ids_to_dist = np.load(ids_to_dist_path, allow_pickle=True)
        self.valid_guesses = list(set(range(self.ids_to_dist.shape[0])).difference(invalid_guesses))

    def guess_score(self, guess):
        """
        Generate a score for a guess
        """
        blue, red, neutral = 0, 0, 0

        distances = [self.ids_to_dist[guess][p['pic_id']] for p in self.board]

        sorted_idx = np.argsort(np.array(distances))
        score = 0
        for i in sorted_idx:
            if self.board[i]['type'] == 'blue':
                delta = (self.alpha**blue)*np.exp(-distances[i])
                blue += 1
            elif self.board[i]['type'] == 'red':
                delta = -(self.beta**red)*np.exp(-distances[i])
                red += 1
            elif self.board[i]['type'] == 'neutral':
                delta = -0.5*(self.gamma**neutral)*np.exp(-distances[i])
                neutral += 1
            else:
                delta = -2*np.exp(-distances[i])

            score += delta

        return score, distances

    def get_best_guess_and_scores(self):
        """
        Get the best guess and its scores
        """
        best_guess = ''
        best_distances = []
        best_score = -float('inf')
        for guess in self.valid_guesses:
            score, distances = self.guess_score(guess)
            if score > best_score:
                best_guess = guess
                best_distances = distances
                best_score = score

        return best_guess, best_distances, best_score

    def display_board(self, best_guess, best_distances, shape=(5, 5)):
        pic_ids = [picture['pic_id'] for picture in self.board] + [best_guess]
        fig, ax = plt.subplots(shape[0] + 1, shape[1], figsize=(24, 24))
        for i in range(shape[0] + 1):
            for j in range(shape[1]):
                if i != shape[0]:
                    idx = shape[0]*i + j
                    path = f'../static/pictures/{pic_ids[idx]}.jpg'
                    image = imread(path)
                    ax[i][j].set_title(f'Distance:{best_distances[idx]:.3f}', size=8)
                    ax[i][j].imshow(image)
                elif j == shape[1]//2:
                    path = f'../static/pictures/{best_guess}.jpg'
                    image = imread(path)
                    ax[i][j].imshow(image)
                ax[i][j].axis('off')
        fig.subplots_adjust(hspace=0.4)
        plt.show()


def main():
    n_ids = 3242
    ids_to_dist_path = '../static/numpy/ids_to_dist.npy'
    board = generate_board(n_ids)
    invalid_guesses = set([picture['pic_id'] for picture in board])
    predictor = Predictor(board, ids_to_dist_path, invalid_guesses, alpha=0.9, beta=0.1, gamma=0.1)
    best_guess, best_distances, best_score = predictor.get_best_guess_and_scores()

    board_types = [b['type'] for b in board]
    for t, s in zip(board_types, best_distances):
        print(f'Type:{t} || Score:{s:.3f}')
    predictor.display_board(best_guess, best_distances, shape=(5, 5))


if __name__ == "__main__":
    main()











