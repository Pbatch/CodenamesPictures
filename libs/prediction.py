from itertools import combinations, chain
import argparse
from boardgen import Boardgen
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self, board, path, target, invalid_guesses):
        """
        Parameters
        ----------
        board: json
            The current board state
        path: str
            The path to the dictionary; the keys are urls and the values are vectors
        target: int
            The number of pictures to try and link
        invalid_guesses: set
            Urls which have already been given as clues
        """
        self.board = board
        self.path = path
        self.target = target
        self.invalid_guesses = invalid_guesses

        self.blue, self.red, self.neutral, self.assassin = self.get_types()
        self.pairwise_scores = self.calculate_pairwise_scores()
        self.valid_guesses = self.get_valid_guesses()

    def get_types(self):
        """
        Extract the types from the cards
        """
        blue = []
        red = []
        neutral = []
        assassin = ""
        for picture in self.board:
            url = picture["url"].replace(" ", "")
            if picture["type"] == "blue" and not picture["active"]:
                blue.append(url)
            if picture["type"] == "red" and not picture["active"]:
                red.append(url)
            if picture["type"] == "neutral" and not picture["active"]:
                neutral.append(url)
            if picture["type"] == "assassin" and not picture["active"]:
                assassin = url
        return blue, red, neutral, assassin

    def get_valid_guesses(self):
        """
        Get the relevant valid guesses
        """
        d = np.load(self.path, allow_pickle=True).item()
        potential_guesses = set(chain.from_iterable(d[url] for url in self.blue))
        valid_guesses = potential_guesses.difference(self.invalid_guesses)

        return valid_guesses

    def earthmover(self, u, v):
        dist_matrix = cdist(u, v, metric='cosine')
        assignment = linear_sum_assignment(dist_matrix)
        score = np.mean(dist_matrix[assignment])
        return score

    def calculate_pairwise_scores(self):
        """
        Generate the pairwise scores

        This dictionary will save unnecessary computation time later on
        """
        pairwise_scores = {}
        for pair in combinations(self.blue, 2):
            u, v = self.ve
            pairwise_scores[pair] = self.earthmover(pair[0], pair[1])
        return pairwise_scores

    def guess_score(self, guess):
        """
        Generate a score for a guess

        The first component is the number of relevant red + neutral + assassin words
        The second component is the number of relevant blue words
        The final component is a measure of how well the clue and the relevant blue words link
        """

        if guess in self.words:
            return [[float('-inf'), float('-inf'), float('-inf')], guess, []]

        score = [0, 0, 0]

        bad_similarities = [(w, self.similarity(guess, w)) for w in self.red + self.neutral + [self.assassin]]
        relevant_bad_words = [w for w, s in bad_similarities if s != 0]

        score[0] = -len(relevant_bad_words)

        blue_similarities = [(w, self.similarity(guess, w)) for w in self.blue]
        relevant_blue_words = {w: s for w, s in blue_similarities if s != 0}

        score[1] = min(self.target, len(relevant_blue_words))

        target_blue = []
        for blue_words in combinations(relevant_blue_words.keys(), score[1]):
            pairs = combinations(blue_words, 2)
            cluster_score = sum(self.pairwise_scores[(a, b)] for a, b in pairs)
            guess_score = sum(relevant_blue_words[w] for w in blue_words)
            total_score = cluster_score + guess_score
            if total_score >= score[2]:
                target_blue = blue_words
                score[2] = total_score

        target_blue = [self.all_words.index(w)+1 for w in target_blue]

        return score, guess, target_blue

    def get_best_guess_and_score(self):
        """
        Get the best guess and its score
        """
        guess_scores = (self.guess_score(g) for g in self.valid_guesses)
        best_score, best_guess, target_blue = max(guess_scores, key=lambda x: x[0])

        return best_score, best_guess, target_blue


def main():
    parser = argparse.ArgumentParser(description='Create a Picture Codenames board')
    parser.add_argument('path', type=str, help='The location of the dictionary')
    args = parser.parse_args()
    board = Boardgen(args.path).board
    predictor = Predictor(board, args.path, 2, {})


if __name__ == "__main__":
    main()











