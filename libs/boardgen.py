import numpy as np
import argparse


class Boardgen:
    """
    Generate a random board
    """
    def __init__(self, path):
        """
        Parameters
        ----------
        path: str
            The path to the possible urls
        """
        self.path = path
        self.board = self.generate_board()

    def generate_board(self):
        """
        Create a game board
        """
        try:
            d = np.load(self.path, allow_pickle=True).item()
            all_urls = list(d.keys())
        except UnicodeDecodeError:
            raise Exception("Make sure that the path is a text file")
        except FileNotFoundError:
            raise Exception("Make sure that the path exists")

        permutation = np.random.permutation(len(all_urls))
        urls = np.array(all_urls)[permutation][:25]

        # 9 Blue, 8 Red, 7 Neutral, 1 Assassin
        board = []
        for i, url in enumerate(urls):
            if i < 9:
                type = "blue"
            elif i < 17:
                type = "red"
            elif i < 24:
                type = "neutral"
            else:
                type = "assassin"
            picture = {"url": url, "type": type, "active": False}
            board.append(picture)

        np.random.shuffle(board)

        # Assign ids (+1 because of the header)
        for i in range(25):
            board[i]["id"] = i+1

        return board


def main():
    parser = argparse.ArgumentParser(description='Create a Picture Codenames board')
    parser.add_argument('path', type=str, help='The location of the dictionary')
    args = parser.parse_args()
    board = Boardgen(args.path).board
    print(board)


if __name__ == "__main__":
    main()