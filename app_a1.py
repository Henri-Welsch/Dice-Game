import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import sys
import logging
from datetime import datetime, timedelta
import csv
import os

# Flask-Anwendung und SocketIO initialisieren
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, async_mode='eventlet')

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Spielparameter
SPIELER_LATENZ = 2  # Sekunden, zufällige Verzögerung für Spieler
DAUER_DER_RUNDE = 5  # Sekunden, Dauer der Runde
WAIT_TIME_BETWEEN_ROUNDS = 5  # Sekunden, Wartezeit zwischen den Runden

players = 0
player_scores = {}
current_round = 0
round_active = False
start_time = None
stop_time = None

# CSV-Datei initialisieren
csv_file = 'game_results.csv'
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Round', 'Name', 'Score', 'Duration of the round', 'Max Player latency', 
            'Server Start Time', 'Server End Time', 'Client Start Time', 'Client Latency', 
            'Client Send Time', 'Server Receive Time', 'Too Late', 'Winner'
        ])

@app.route('/')
def index():
    return render_template('index_a1.html', spieler_latenz=SPIELER_LATENZ, dauer_der_runde=DAUER_DER_RUNDE)

@socketio.on('player_data')
def handle_player_data(data):
    global players
    try:
        players += 1
        logger.info(f'Player Data Received: {data}')
        player_scores[data['name']] = {'score': 0, 'client_info': {}, 'too_late': False}
        emit('update_player_count', {'count': players}, namespace='/')
        
        if players >= 3 and not round_active:
            socketio.start_background_task(start_game)
    except Exception as e:
        logger.error(f"Error handling player data: {e}")

def start_game():
    global current_round, round_active, start_time, stop_time
    try:
        round_active = True
        current_round += 1
        start_time = datetime.now()
        formatted_start_time = start_time.strftime('%H:%M:%S:%f')
        
        logger.info(f"Starting round {current_round} at {formatted_start_time}")
        socketio.emit('start', {'start_time': formatted_start_time}, namespace='/')
        logger.info("START message sent to all players")
        
        eventlet.sleep(DAUER_DER_RUNDE)
        
        stop_time = datetime.now()
        formatted_stop_time = stop_time.strftime('%H:%M:%S:%f')
        stop_game(formatted_stop_time)
    except Exception as e:
        logger.error(f"Error starting game: {e}")

def stop_game(stop_time):
    global round_active
    try:
        logger.info(f"Stopping round {current_round} at {stop_time}")
        round_active = False
        socketio.emit('stop', namespace='/')
        logger.info("STOP message sent to all players")
        
        if player_scores:
            winner = max(
                (player for player in player_scores if not player_scores[player]['too_late']),
                key=lambda k: player_scores[k]['score'],
                default=None
            )
            winner_score = player_scores[winner]['score'] if winner else 0
            
            logger.info(f"Winner of round {current_round}: {winner} with score {winner_score}")
            
            for player, data in player_scores.items():
                client_info = data['client_info']
                too_late = data['too_late']
                is_winner = 'Yes' if player == winner else 'No'
                
                with open(csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        current_round, player, data['score'], DAUER_DER_RUNDE, SPIELER_LATENZ,
                        client_info.get('server_start_time', ''), stop_time,
                        client_info.get('client_start_time', ''), client_info.get('client_latency', ''),
                        client_info.get('client_send_time', ''), client_info.get('server_receive_time', ''),
                        'Yes' if too_late else 'No', is_winner
                    ])
            
            socketio.emit('round_result', {'winner': winner, 'score': winner_score}, namespace='/')
            logger.info("Round result sent to all players")
        
        for player in player_scores:
            player_scores[player] = {'score': 0, 'client_info': {}, 'too_late': False}
        
        eventlet.sleep(WAIT_TIME_BETWEEN_ROUNDS)
        start_game()
    except Exception as e:
        logger.error(f"Error stopping game: {e}")

@socketio.on('player_throw')
def handle_player_throw(data):
    try:
        name = data['name']
        throw = data['throw']
        client_start_time = data['client_start_time']
        client_latency = data['client_latency']
        client_send_time = data['client_send_time']
        server_receive_time = datetime.now()
        server_receive_time_str = server_receive_time.strftime('%H:%M:%S:%f')
        
        logger.info(f"Received throw from {name}: {throw} at {server_receive_time_str}")
        
        if round_active:
            too_late = server_receive_time > (start_time + timedelta(seconds=DAUER_DER_RUNDE))
            player_scores[name] = {
                'score': throw if not too_late else 0,
                'client_info': {
                    'server_start_time': start_time.strftime('%H:%M:%S:%f'),
                    'client_start_time': client_start_time,
                    'client_latency': client_latency,
                    'client_send_time': client_send_time,
                    'server_receive_time': server_receive_time_str
                },
                'too_late': too_late
            }
        else:
            logger.warning(f"Throw from {name} received after round ended: {throw}")
    except Exception as e:
        logger.error(f"Error handling player throw: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        SPIELER_LATENZ = int(sys.argv[1])
    if len(sys.argv) > 2:
        DAUER_DER_RUNDE = int(sys.argv[2])
    
    socketio.run(app, host='0.0.0.0', port=8080)
