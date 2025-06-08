from flask import Flask, request, render_template, jsonify
app = Flask(__name__)

# 초기 상태
book_locations = {
    'Section1': [],
    'Section2': [],
    'Section3': []
}

@app.route('/')
def index():
    return render_template('index.html', book_locations=book_locations)

@app.route('/add', methods=['POST'])
def add_book():
    global book_locations
    data = request.get_json()
    section = data.get("section")
    title = data.get("title")
    if section in book_locations and title:
        book_locations[section].append(title)
        print(f"{section}에 '{title}' 추가됨")
        return "OK"
    return "Invalid data", 400

@app.route('/data')
def data():
    return jsonify(book_locations)

@app.route('/update', methods=['POST'])
def update():
    global book_locations
    data = request.json
    if 'Section1' in data and 'Section2' in data and 'Section3' in data:
        book_locations = data
        return {'status': 'success'}
    else:
        return {'status': 'error', 'message': 'Invalid data'}, 400

if __name__ == '__main__':
    app.run(debug=True)
