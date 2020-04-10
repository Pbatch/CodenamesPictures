import numpy as np


class Computer:
    """
    Generate a random sequence of computer moves
    """
    def __init__(self, board):
        """
        Parameters
        ----------
        board: json
            The current board state
        """
        self.board = board
        self.distribution = {"blue": 1, "red": 6, "neutral": 1, "none": 1}
        self.blue, self.red, self.neutral = self.get_types()

    def get_types(self):
        """
        Extract the types from the pictures
        """
        blue = []
        red = []
        neutral = []
        for pic in self.board[1:]:
            pic_id = pic["id"]
            if pic["type"] == "blue" and not pic["active"]:
                blue.append(pic_id)
            if pic["type"] == "red" and not pic["active"]:
                red.append(pic_id)
            if pic["type"] == "neutral" and not pic["active"]:
                neutral.append(pic_id)
        return blue, red, neutral

    def generate_computer_sequence(self):
        """
        Generate a sequence for the computer
        """

        sequence = []
        pic_type = None
        decay = 1
        while pic_type not in {"blue", "neutral"}:
            if len(self.blue) + len(self.red) + len(self.neutral) == 0:
                break
            weights = [self.distribution["red"]*decay if len(self.red) > 0 else 0,
                       self.distribution["blue"] if len(self.blue) > 0 else 0,
                       self.distribution["neutral"] if len(self.neutral) > 0 else 0,
                       self.distribution["none"] if len(sequence) != 0 else 0]
            weights = np.array(weights) / sum(weights)

            pic_type = np.random.choice(["red", "blue", "neutral", "none"], p=weights)

            if pic_type == "red":
                pic_id = np.random.choice(self.red)
                self.red.remove(pic_id)

            elif pic_type == "blue":
                pic_id = np.random.choice(self.blue)
                self.blue.remove(pic_id)

            elif pic_type == "neutral":
                pic_id = np.random.choice(self.neutral)
                self.neutral.remove(pic_id)

            else:
                break

            print(pic_type)

            sequence.append(int(pic_id))
            decay *= 0.25

        return sequence


if __name__ == "__main__":
    print('Insert testing here')

