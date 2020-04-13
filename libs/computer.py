import numpy as np


class Computer:
    """
    Generate a random sequence of computer moves
    """
    def __init__(self, board, params=None):
        """
        Parameters
        ----------
        board: json
            The current board state
        """
        self.board = board
        self.params = self.set_params(params)
        self.blue, self.red, self.neutral = self.get_types()

    @staticmethod
    def set_params(params):
        if params is None:
            params = {"blue": 0, "red": 5, "neutral": 1, "none": 1, 'decay': 0.2}
        else:
            for key in ['blue', 'red', 'neutral', 'none', 'decay']:
                if key not in params:
                    raise ValueError(f'Params needs a value for key {key}')
        return params

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
            weights = [self.params["red"]*decay if len(self.red) > 0 else 0,
                       self.params["blue"] if len(self.blue) > 0 else 0,
                       self.params["neutral"] if len(self.neutral) > 0 else 0,
                       self.params["none"] if len(sequence) != 0 else 0]
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

            sequence.append(int(pic_id))
            decay *= self.params['decay']

        return sequence


if __name__ == "__main__":
    print('Insert testing here')

