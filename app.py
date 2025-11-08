from flask import Flask, render_template, request, redirect, url_for, session
import random
import os
import json
from hashlib import sha256

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-this'  # ĐỔI THÀNH KEY RIÊNG

# File lưu trạng thái
STATE_FILE = 'game_state.json'

def create_derangement(names):
    """Tạo vòng bí mật: mỗi người tặng 1 người khác, không trùng, không tự tặng"""
    if len(names) < 2:
        return {}
    shuffled = names[:]
    while True:
        random.shuffle(shuffled)
        if all(shuffled[i] != names[i] for i in range(len(names))):
            break
    return {names[i]: shuffled[i] for i in range(len(names))}

def init_game():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # DANH SÁCH TÊN (bạn sửa ở đây)
    initial_names = [
        "Phuong Thuy", "Ngoc Nhu", "Lam Ngoc", "Minh Tuyet"
        "Linh Nhi", "Vinh Hoang", "Tai Pham"
    ]
    
    # Tạo vòng bí mật
    secret_cycle = create_derangement(initial_names)
    
    state = {
        'secret_cycle': secret_cycle,
        'remaining': initial_names.copy(),
        'played': []
    }
    
    save_state(state)
    return state

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_state():
    if not os.path.exists(STATE_FILE):
        return init_game()
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    state = load_state()
    remaining = state['remaining']
    
    if not remaining:
        return render_template('result.html', message="Tất cả đã bốc thăm xong! 🎄", is_end=True)
    
    if request.method == 'POST':
        player_name = request.form['player_name'].strip()
        
        if not player_name:
            return render_template('index.html', remaining=remaining, error="Nhập tên đi!")
        
        if player_name not in remaining:
            return render_template('index.html', remaining=remaining, 
                                 error="Tên không hợp lệ hoặc đã bốc thăm!")
        
        # Lấy người được tặng
        secret_child = state['secret_cycle'][player_name]
        
        # Cập nhật trạng thái
        state['remaining'].remove(player_name)
        state['played'].append(player_name)
        save_state(state)
        
        return render_template('result.html',
                             player=player_name,
                             secret_child=secret_child)
    
    return render_template('index.html', remaining=remaining)

# Reset game (chỉ bạn biết link này)
@app.route('/reset-game-please-dont-share')
def reset():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)