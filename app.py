import os
import re
import json
from flask import Flask, render_template, jsonify, request
from config import CARD_CONFIG

app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static', 'cards')

def build_attr_map():
    attr_map = {}
    for attr, rarity_groups in CARD_CONFIG.items():
        for rarity, ids in rarity_groups.items():
            for card_id in ids:
                attr_map[(str(rarity), str(card_id))] = attr
    return attr_map

ATTR_LOOKUP = build_attr_map()

def get_data_path(uid):
    clean_uid = re.sub(r'\D', "", str(uid)) or "0000"
    return f"data_{clean_uid}.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init')
def init_cards():
    global ATTR_LOOKUP
    ATTR_LOOKUP = build_attr_map()

    uid = request.args.get('uid', '0000') 
    data_file = get_data_path(uid)
    
    saved_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
        except:
            saved_data = {}
            
    files = os.listdir(IMAGE_FOLDER)
    cards = []
    pattern = re.compile(r's_card-(\d)-(\d+)')

    for filename in files:
        match = pattern.search(filename)
        if match:
            rarity = match.group(1)
            card_id = match.group(2)
            
            attr = ATTR_LOOKUP.get((rarity, card_id))
            
            cards.append({
                'id': card_id,
                'rarity': rarity,
                'filename': filename,
                'breakLevel': saved_data.get(card_id, -1),
                'attribute': attr
            })
    
    cards.sort(key=lambda x: (int(x['rarity']), int(x['id'])), reverse=True)
    return jsonify(cards)

@app.route('/api/save', methods=['POST'])
def save_data():
    payload = request.json
    uid = payload.get('uid', '0000')
    cards_data = payload.get('cards', [])
    data_file = get_data_path(uid)
    storage = {item['id']: item['breakLevel'] for item in cards_data}
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(storage, f, ensure_ascii=False, indent=4)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)