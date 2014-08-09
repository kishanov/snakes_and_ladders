import json

from flask import Flask, render_template

import game_engine


app = Flask(__name__)


@app.route('/')
def index():
    boards = game_engine.get_all_boards()
    return render_template('games_list.html', boards=boards)


@app.route('/boards/<int:board_id>')
def board_page(board_id):
    return json.dumps({"board": game_engine.get_board(board_id),
                       "id": board_id})


if __name__ == '__main__':
    app.run()
