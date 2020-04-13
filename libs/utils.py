import numpy as np
import io
import pstats
import cProfile


def ctimer(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        out = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(10)
        print(s.getvalue())
        return out
    return wrapper


def generate_board(n_ids):
    """
    Create a game board
    """
    # Select 25 random pic_ids
    pic_ids = np.random.permutation(n_ids)[:25]

    # 9 Blue, 8 Red, 7 Neutral, 1 Assassin
    board = []
    for i in range(25):
        if i < 9:
            _type = "blue"
            colour = "#0080FF"
        elif i < 17:
            _type = "red"
            colour = "#FF0000"
        elif i < 24:
            _type = "neutral"
            colour = "#808080"
        else:
            _type = "assassin"
            colour = "#202020"
        picture = {"pic_id": int(pic_ids[i]), "type": _type, "active": False, "colour": colour}
        board.append(picture)

    # Stop colours being adjacent by default
    np.random.shuffle(board)

    # Assign ids (+1 because of the header)
    for i in range(25):
        board[i]["id"] = i+1

    return board


if __name__ == "__main__":
    n_ids = 3242
    board = generate_board(n_ids)
    print(board)