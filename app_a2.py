import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from collections import defaultdict
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, async_mode='eventlet')

players = 0
current_round = 0
vector_clocks = defaultdict(lambda: [0, 0, 0])  # Default vector clock for 3 players
player_ids = {}
round_active = False
delayed_messages = []

csv_file_path = 'output.csv'

# Function to append output to the CSV file
def append_to_csv_file(round_number, name, throw, vector_clock):
    with open(csv_file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([round_number, name, throw, vector_clock])

@app.route('/')
def index():
    return render_template('index_a2.html', spieler_latenz=3, dauer_der_runde=2)

@socketio.on('player_data')
def handle_player_data(data):
    global players
    players += 1
    player_id = players - 1
    player_name = data['name']
    player_ids[player_name] = player_id

    output = f'Player Data Received: {data}'
    print(output)
    emit('player_id', {'player_id': player_id})  # Send player ID to the client

    if players >= 3:
        socketio.start_background_task(start_game)

def start_game():
    global current_round, round_active
    current_round += 1
    round_active = True
    
    output = f"Starting round {current_round}"
    print(output)
    socketio.emit('start', namespace='/')
    eventlet.sleep(3)

    stop_game()

def stop_game():
    global round_active
    round_active = False
    socketio.emit('stop', namespace='/')
    
    # Process delayed messages
    for message in delayed_messages:
        handle_player_throw(message)
    delayed_messages.clear()
    
    start_game()

@socketio.on('player_throw')
def handle_player_throw(data):
    player_name = data['name']
    player_throw = data['throw']
    player_vector_clock = data['vector_clock']
    player_id = player_ids[player_name]

    output = f"Received throw from {player_name}: {player_throw}\nVector clock: {player_vector_clock}"
    print(output)
    append_to_csv_file(current_round, player_name, player_throw, player_vector_clock)

    # If the round is not active, add the message to delayed messages
    if not round_active:
        delayed_messages.append(data)
        output = f"Message from {player_name} delayed."
        print(output)
        append_to_csv_file(current_round, player_name, player_throw, "delayed")
        return

    # Update the server's vector clock for this player
    vector_clocks[player_name] = player_vector_clock

    # Prepare an acknowledgement with the server's vector clock
    server_vector_clock = [max(vector_clocks[p][i] for p in vector_clocks) for i in range(3)]
    socketio.emit('ack', {'server_vector_clock': server_vector_clock}, namespace='/')

if __name__ == '__main__':    
    # Ensure the CSV file is empty when the server starts
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['round', 'name', 'throw', 'vector_clock'])
    
    socketio.run(app, host='0.0.0.0', port=8080)
