from flask import Flask, render_template, request, redirect, url_for
import random
import os
import json

app = Flask(__name__)
app.secret_key = '759e6990bc49cb50b857bdc76b7d8ee3d3e3f52c5ae2fddb7b3b3b980d381c0a'

STATE_FILE = 'game_state.json'
PARTICIPANTS_FILE = 'participants.json'

def load_participants():
    if not os.path.exists(PARTICIPANTS_FILE):
        # Tạo mẫu nếu chưa có
        sample = [
            {"name": "Phương Thuỵ", "image": "phuong-thuy.jpg"},
            {"name": "Ngọc Như", "image": "ngoc-nhu.jpg"},
            {"name": "Lam Ngọc", "image": "lam-ngoc.jpg"},
            {"name": "Linh Nhi", "image": "linh-nhi.jpg"},
            {"name": "Minh Tuyết", "image": "minh-tuyet.jpg"},
            {"name": "Vinh Hoàng", "image": "vinh-hoang.jpg"},
            {"name": "Tài Phạm", "image": "tai-pham.jpg"}
        ]
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        return sample
    
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_derangement(participants):
    names = [p['name'] for p in participants]
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
    
    participants = load_participants()
    name_to_info = {p['name']: p for p in participants}
    secret_cycle = create_derangement(participants)
    
    state = {
        'secret_cycle': secret_cycle,
        'name_to_info': name_to_info,
        'remaining': [p['name'] for p in participants],
        'played': []
    }
    save_state(state)
    return state

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        # Chỉ lưu tên, không lưu ảnh (ảnh lấy từ file participants)
        saveable = {
            'secret_cycle': state['secret_cycle'],
            'remaining': state['remaining'],
            'played': state['played']
        }
        json.dump(saveable, f, ensure_ascii=False, indent=2)

def load_state():
    if not os.path.exists(STATE_FILE):
        return init_game()
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        saved = json.load(f)
    
    participants = load_participants()
    name_to_info = {p['name']: p for p in participants}
    
    state = {
        'secret_cycle': saved['secret_cycle'],
        'name_to_info': name_to_info,
        'remaining': saved['remaining'],
        'played': saved.get('played', [])
    }
    return state

@app.route('/', methods=['GET', 'POST'])
def index():
    state = load_state()
    remaining = state['remaining']
    
    if not remaining:
        return render_template('result.html', message="Trò chơi đã kết thúc! 🎄", is_end=True)
    
    if request.method == 'POST':
        player_name = request.form['player_name'].strip()
        
        if not player_name or player_name not in remaining:
            return render_template('index.html', remaining=remaining, 
                                 error="Tên không hợp lệ hoặc đã bốc thăm!")
        
        secret_child_name = state['secret_cycle'][player_name]
        secret_child = state['name_to_info'][secret_child_name]
        
        # Cập nhật trạng thái
        state['remaining'].remove(player_name)
        state['played'].append(player_name)
        save_state(state)
        
        return render_template('result.html',
                             player=player_name,
                             secret_child=secret_child)  # Trả cả tên + ảnh
    
    # Hiển thị danh sách còn lại (có ảnh nhỏ)
    remaining_info = [state['name_to_info'][name] for name in remaining]
    return render_template('index.html', remaining=remaining_info)

@app.route('/reset-secret-santa-2025')
def reset():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)