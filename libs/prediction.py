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

    def guess_scores(self, guess):
        """
        Generate the scores for a guess
        """
        blue, red, neutral = 0, 0, 0
        scores = [0 for _ in range(len(self.board))]

        distances = [self.ids_to_dist[guess][p['pic_id']] for p in self.board]
        sorted_idx = np.argsort(np.array(distances))
        for i in sorted_idx:
            if self.board[i]['type'] == 'blue':
                scores[i] = (self.alpha**blue)*np.exp(-distances[i])
                blue += 1
            elif self.board[i]['type'] == 'red':
                scores[i] = -(self.beta**red)*np.exp(-distances[i])
                red += 1
            elif self.board[i]['type'] == 'neutral':
                scores[i] = -(self.gamma**neutral)*np.exp(-distances[i])
                neutral += 1
            else:
                scores[i] = -np.exp(-distances[i])

        return scores

    def get_best_guess_and_scores(self):
        """
        Get the best guess and its scores
        """
        best_guess = ''
        best_scores = []
        best_total_score = -float('inf')
        for guess in self.valid_guesses:
            scores = self.guess_scores(guess)
            total_score = sum(scores)
            if total_score > best_total_score:
                best_guess = guess
                best_scores = scores
                best_total_score = total_score

        return best_guess, best_scores

    def display_board(self, best_guess, best_scores, shape=(5, 5)):
        pic_ids = [picture['pic_id'] for picture in self.board] + [best_guess]
        fig, ax = plt.subplots(shape[0] + 1, shape[1], figsize=(24, 24))
        for i in range(shape[0] + 1):
            for j in range(shape[1]):
                if i != shape[0]:
                    idx = shape[0]*i + j
                    path = f'../static/pictures/{pic_ids[idx]}.jpg'
                    image = imread(path)
                    ax[i][j].set_title(best_scores[idx], size=8)
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
    best_guess, best_scores = predictor.get_best_guess_and_scores()

    scaled_scores = [int(100*s) for s in best_scores]
    board_types = [b['type'] for b in board]
    for t, s in zip(board_types, scaled_scores):
        print(f'Type:{t} || Score:{s}')
    predictor.display_board(best_guess, scaled_scores, shape=(5, 5))


if __name__ == "__main__":
    main()











