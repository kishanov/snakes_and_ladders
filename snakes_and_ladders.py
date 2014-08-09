from flask import Flask, render_template, jsonify

import game_engine


app = Flask(__name__)


@app.route('/')
def index():
    boards = game_engine.get_all_boards()
    return render_template('games_list.html', boards=boards)


@app.route('/api/boards/<int:board_id>')
def get_board(board_id):
    return jsonify(game_engine.get_board(board_id))


@app.route('/api/boards/sample_board_1.json')
def sample_board():
    return jsonify({"board": game_engine.sample_board_1(),
                    "id": 1})


@app.route('/boards/<int:board_id>')
def board_page(board_id):
    moves = game_engine.win_game(board_id)
    return render_template('board_page.html', moves=moves)


if __name__ == '__main__':
    app.run()
