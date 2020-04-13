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
                     'blue': 1.0,
                     'red': 1.0,
                     'neutral': 1.0
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
    ids_to_score_path = 'static/numpy/ids_to_score.npy'
    invalid_guesses = set(board[0]['invalid_guesses'])

    score_params = {'blue': board[0]['blue'],
                    'red': board[0]['red'],
                    'neutral': board[0]['neutral'],
                    'assassin': 1,
                    'decay': 0.7}

    predictor = Predictor(board[1:], ids_to_score_path, invalid_guesses, score_params)
    clue, scores = predictor.get_best_guess_and_scores()
    scaled_scores = [round(s) for s in scores]
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
    # USE THIS FOR THE EC2
    # app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='127.0.0.1', port=8080, debug=True)