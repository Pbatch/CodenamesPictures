from utils import generate_board
import numpy as np
# import matplotlib.pyplot as plt
from skimage.io import imread


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self, board, ids_to_score_path, invalid_guesses, params=None):
        """
        Parameters
        ----------
        board: json
            The current board state
        ids_to_score_path: str
            The path to the ids_to_score nd-array
        invalid_guesses: set
            Guesses which can't be used
        params: dict
            The parameters for the score function
        """
        self.board = [p for p in board if not p['active']]
        self.params = self.set_params(params)
        self.ids_to_score = np.load(ids_to_score_path, allow_pickle=True)
        self.valid_guesses = list(set(range(self.ids_to_score.shape[0])).difference(invalid_guesses))

    @staticmethod
    def set_params(params):
        if params is None:
            params = {'blue': 1.0,
                      'red': 1.0,
                      'neutral': 1.0,
                      'assassin': 1.0,
                      'decay': 0.7}
        else:
            for key in ['blue', 'red', 'neutral', 'assassin', 'decay']:
                if key not in params:
                    raise ValueError(f'Score params needs a value for key {key}')
        return params

    def guess_scores(self, guess):
        """
        Generate the scores for a guess
        """
        blue, red, neutral = 0, 0, 0

        scores = [self.ids_to_score[guess][p['pic_id']] for p in self.board]
        sorted_idx = np.argsort(-np.array(scores))
        for i in sorted_idx:
            if self.board[i]['type'] == 'blue':
                scores[i] *= self.params['blue']*(self.params['decay']**blue)
                blue += 1
            elif self.board[i]['type'] == 'red':
                scores[i] *= -self.params['red']*(self.params['decay']**red)
                red += 1
            elif self.board[i]['type'] == 'neutral':
                scores[i] *= -self.params['neutral']*(self.params['decay']**neutral)
                neutral += 1
            else:
                scores[i] *= -self.params['assassin']

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
    ids_to_score_path = '../static/numpy/ids_to_score.npy'
    board = generate_board(n_ids)
    invalid_guesses = set([picture['pic_id'] for picture in board])
    predictor = Predictor(board, ids_to_score_path, invalid_guesses)
    best_guess, best_scores = predictor.get_best_guess_and_scores()

    round_scores = [round(s) for s in best_scores]
    board_types = [b['type'] for b in board]
    for t, s in zip(board_types, round_scores):
        print(f'Type:{t} || Score:{s}')
    predictor.display_board(best_guess, round_scores, shape=(5, 5))


if __name__ == "__main__":
    main()











