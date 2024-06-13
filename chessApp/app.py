from flask import Flask, render_template, request
from lichess_api import launch_game
from read_board import init_board_control
from models import GameParams
import time

def handle_game_start(request):
    global process
    params = GameParams()
    params.side = request.form['color']
    params.time = int(request.form['time_limit']) * 60 # time in seconds
    params.time_inc = int(request.form['time_increment'])
    params.level = int(request.form['difficulty'])
    
    launch_game(params)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'lichess_token' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        handle_game_start(request)

    colors = ['white', 'black']
    difficulties = list(range(1, 9))

    return render_template('index.html', colors=colors, difficulties=difficulties)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
