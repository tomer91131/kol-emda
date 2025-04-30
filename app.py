from flask import Flask, render_template, jsonify
from controllers.news_controller import NewsController

app = Flask(__name__)
controller = NewsController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/triplets')
def get_game_triplets():
    triplets = controller.get_game_triplets()
    return jsonify(triplets)

@app.route('/api/comparison/triplets')
def get_comparison_triplets():
    triplets = controller.get_news_comparison()
    return jsonify(triplets)

if __name__ == '__main__':
    app.run(debug=True) 

