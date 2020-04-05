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


def generate_board(path):
    """
    Create a game board
    """
    try:
        d = np.load(path, allow_pickle=True).item()
        all_urls = list(d.keys())
    except FileNotFoundError:
        raise Exception("Make sure that the path exists")

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
        picture = {"url": url, "type": type, "active": False, "colour": colour}
        board.append(picture)

    np.random.shuffle(board)

    # Assign ids (+1 because of the header)
    for i in range(25):
        board[i]["id"] = i+1

    return board


if __name__ == "__main__":
    path = '../static/data/url_to_vec.npy'
    board = generate_board(path)
    display_board(board)
    print(board)