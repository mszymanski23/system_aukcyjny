from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

# Inicjalizacja danych
users = ['tel1', 'tel2', 'tel3', 'tel4']
logged_in_users = []
round_data = []
bids = {}
all_bids = []
current_round = 0
round_duration = 60  # czas trwania rundy w sekundach
break_duration = 30  # czas trwania przerwy technicznej w sekundach

@app.route('/')
def index():
    return render_template('index.html', users=users, logged_in_users=logged_in_users)

@app.route('/login/<user>')
def login(user):
    if user not in logged_in_users:
        logged_in_users.append(user)
    session['user'] = user
    if user == 'admin':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('user_panel', user=user))

@app.route('/admin')
def admin():
    return render_template('admin.html', logged_in_users=logged_in_users, round_data=round_data)

@app.route('/user/<user>')
def user_panel(user):
    if 'user' not in session or session['user'] != user:
        return redirect(url_for('index'))
    return render_template('user.html', user=user)

@socketio.on('start_auction')
def start_auction():
    global round_data, current_round, bids, all_bids
    current_round = 0
    bids = {user: [] for user in users}
    all_bids = []
    round_data = [
        {'round': 0, 'block': 'A', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'B', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'C', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'D', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'E', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'F', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
        {'round': 0, 'block': 'G', 'current_bid': 100, 'bid_increment': 100, 'highest_bidder': None},
    ]
    emit('round_data', round_data, broadcast=True)

@socketio.on('submit_bid')
def submit_bid(data):
    user = session.get('user')
    if not user:
        return False

    block = data['block']
    bid_amount = int(data['bid_amount'])

    # Sprawdzenie, czy użytkownik nie przekracza limitu dwóch bloków
    user_wins = [data['block'] for data in round_data if data['highest_bidder'] == user]
    if len(user_wins) >= 2 or (block in user_wins):
        return False

    bid = {'user': user, 'block': block, 'bid_amount': bid_amount, 'round': current_round, 'time': time.strftime('%Y-%m-%d %H:%M:%S')}
    bids[user].append(bid)
    all_bids.append(bid)
    emit('new_bid', bid, room='admin')

@socketio.on('end_round')
def end_round():
    global current_round
    process_bids()
    current_round += 1
    emit('round_data', round_data, broadcast=True)
    socketio.sleep(break_duration)
    emit('round_data', round_data, broadcast=True)

@socketio.on('join')
def on_join(data):
    user = data['user']
    join_room(user)
    if user == 'admin':
        join_room('admin')

def process_bids():
    global round_data, bids
    for data in round_data:
        block = data['block']
        highest_bid = data['current_bid']
        highest_bidder = None
        highest_bids = []
        for user, user_bids in bids.items():
            for bid in user_bids:
                if bid['block'] == block and bid['bid_amount'] > highest_bid:
                    highest_bid = bid['bid_amount']
                    highest_bids = [(user, bid['bid_amount'])]
                elif bid['block'] == block and bid['bid_amount'] == highest_bid:
                    highest_bids.append((user, bid['bid_amount']))
        if highest_bids:
            highest_bidder = random.choice(highest_bids)[0]
            data['current_bid'] = highest_bid
            data['highest_bidder'] = highest_bidder
    bids = {user: [] for user in users}

if __name__ == '__main__':
    socketio.run(app, debug=True)