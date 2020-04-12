from flask import Flask, render_template, request, jsonify
import sys
import json
sys.path.insert(0, 'libs')
from utils import generate_board
from prediction import Predictor
import computer
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    """
    Homepage for the website.
    Create a random board.
    """
    n_ids = 3242
    board = generate_board(n_ids)
    invalid_guesses = [picture['pic_id'] for picture in board]
    board.insert(0, {"difficulty": "easy",
                     "invalid_guesses": invalid_guesses,
                     })
    return render_template('html/page.html', board=board)


@app.route("/update", methods=["POST"])
def update():
    """
    Update the page with the details from the current board
    """
    board = json.loads(request.data)
    return render_template('html/page.html', board=board)


@app.route("/computer_turn", methods=["POST"])
def computer_turn():
    """
    Get a series of computer moves
    """
    board = json.loads(request.data)
    sequence = computer.Computer(board).generate_computer_sequence()

    json_sequence = jsonify(sequence=sequence)
    return json_sequence


@app.route("/clue", methods=["POST"])
def clue():
    """
    Generate a clue
    """
    board = json.loads(request.data)
    ids_to_dist_path = 'static/numpy/ids_to_dist.npy'
    invalid_guesses = set(board[0]['invalid_guesses'])

    predictor = Predictor(board[1:], ids_to_dist_path, invalid_guesses, alpha=0.6, beta=0.1, gamma=0.1)
    clue, scores = predictor.get_best_guess_and_scores()
    scaled_scores = [int(100*s) for s in scores]
    print(sum(scores))
    clue_details = jsonify(clue=clue, scores=scaled_scores)

    return clue_details


@app.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the dialog box containing the instructions
    """
    return render_template('html/instructions.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', port=8080, debug=True)