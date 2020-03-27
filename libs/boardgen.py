import numpy as np
import argparse


class Boardgen:
    """
    Generate a random board
    """
    def __init__(self, in_file):
        """
        Parameters
        ----------
        in_file: str
            The path to the possible image ids
        """
        self.in_file = in_file
        self.board = self.generate_board()

    def generate_board(self):
        """
        Create a game board
        """
        try:
            all_urls = [word.strip().lower() for word in open(self.in_file)]
        except UnicodeDecodeError:
            raise Exception("Make sure that in_file is a text file")
        except FileNotFoundError:
            raise Exception("Make sure that in_file exists")

        permutation = np.random.permutation(len(all_urls))
        urls = np.array(all_urls)[permutation][:25]

        # 9 Blue, 8 Red, 7 Neutral, 1 Assassin
        board = []
        for i, url in enumerate(urls):
            if i < 9:
                type = "blue"
                colour = "#0080FF"
            elif i < 17:
                type = "red"
                colour = "#FF0000"
            elif i < 24:
                type = "neutral"
                colour = "#D0D0D0"
            else:
                type = "assassin"
                colour = "#202020"
            picture = {"url": url, "type": type, "colour": colour, "active": False}
            board.append(picture)

        np.random.shuffle(board)

        # Assign ids (+1 because of the header)
        for i in range(25):
            board[i]["id"] = i+1

        return board


def main():
    parser = argparse.ArgumentParser(description='Create a Codenames board from a set of words')
    parser.add_argument('codenames_words', type=str,
                        help='The file location of Codenames words')
    args = parser.parse_args()
    board = Boardgen(args.codenames_words).board
    print(board)


if __name__ == "__main__":
    main()