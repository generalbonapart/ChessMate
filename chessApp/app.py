import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from lichess_api import launch_game
from read_board import init_board_control
from models import GameParams

LICHESS_HOST = os.getenv("LICHESS_HOST", "https://lichess.org")
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['LICHESS_CLIENT_ID'] =  os.getenv("LICHESS_CLIENT_ID")
app.config['LICHESS_AUTHORIZE_URL'] = f"{LICHESS_HOST}/oauth"
app.config['LICHESS_ACCESS_TOKEN_URL'] = f"{LICHESS_HOST}/api/token"

oauth = OAuth(app)
oauth.register('lichess', client_kwargs={"code_challenge_method": "S256"})
process = None

def handle_game_start(request):
    global process
    params = GameParams()
    params.side = request.form['color']
    params.time = int(request.form['time_limit']) * 60 # time in seconds
    params.time_inc = int(request.form['time_increment'])
    params.level = int(request.form['difficulty'])
    
    user_api_token = session.get('lichess_token')
    if user_api_token:
        
        init_board_control()
        # Launch lichess game via API
        launch_game(params, user_api_token)
        # Run the C binary
        with open("trolley_log.txt", 'w') as log:
            process = subprocess.Popen(['./build/trolley'],
                                    text=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        redirect_uri = url_for("authorize", _external=True)
        scopes = ("preference:read preference:write email:read challenge:read"
            " challenge:write tournament:write board:play bot:play team:write puzzle:read msg:write" 
            " study:write study:read")
        return oauth.lichess.authorize_redirect(redirect_uri, scope=scopes)
    return render_template('login.html') 

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'lichess_token' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        handle_game_start(request)

    colors = ['white', 'black']
    difficulties = list(range(1, 9))

    return render_template('index.html', colors=colors, difficulties=difficulties)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('lichess_token', None)
    return redirect(url_for('login'))

@app.route('/authorize')
def authorize():
    token = oauth.lichess.authorize_access_token()
    session['lichess_token'] = token['access_token']
    return redirect(url_for('index'))
    # token = oauth.lichess.authorize_access_token()
    # bearer = token['access_token']
    # headers = {'Authorization': f'Bearer {bearer}'}
    # response = requests.get(f"{LICHESS_HOST}/api/account", headers=headers)
    # return jsonify(**response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
