from flask import Flask, render_template, jsonify, request, redirect
from flask.ext.wtf import Form
from wtforms import SelectField

import game_engine


app = Flask(__name__)
app.config.from_object('config')


class NewGameForm(Form):
    ladders_count = SelectField('ladders_count', choices=[(i, i) for i in range(1, 16)])
    snakes_count = SelectField('snakes_count', choices=[(i, i) for i in range(1, 16)])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NewGameForm()

    if request.method == "POST":
        jumps = game_engine.generate_board(int(form.ladders_count.data),
                                           int(form.snakes_count.data))

        board_id = game_engine.save_board_to_db(jumps["ladders"], jumps["snakes"])
        return redirect("/boards/{0}".format(board_id))

    boards = game_engine.get_all_boards()
    return render_template('games_list.html', boards=boards, form=form)


@app.route('/api/boards/<int:board_id>')
def get_board(board_id):
    return jsonify(game_engine.get_board(board_id))


@app.route('/boards/generate', methods=["POST"])
def generate_board(board_id):
    return jsonify(game_engine.get_board(board_id))


@app.route('/boards/<int:board_id>')
def board_page(board_id):
    moves = game_engine.solve_board(board_id)
    return render_template('board_page.html', moves=moves)


if __name__ == '__main__':
    app.run()
