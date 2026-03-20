import random
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for

from database import Database
from ml_model import MLModel, GROUP_INFO, CATEGORY_NAMES
from questions_data import QUESTIONS

app = Flask(__name__)
app.secret_key = 'dinner_decider_2024_secret'

db = Database()
model = MLModel()

NUM_QUESTIONS = 5
NUM_CATEGORIES = 7


@app.route('/')
def index():
    count = db.get_result_count()
    return render_template('index.html', count=count)


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


@app.route('/api/questions')
def api_questions():
    selected_cats = random.sample(range(NUM_CATEGORIES), NUM_QUESTIONS)
    questions = []
    for cat_idx in selected_cats:
        pool = [q for q in QUESTIONS if q['category'] == cat_idx]
        q = random.choice(pool)
        questions.append({
            'id': q['id'],
            'category': q['category'],
            'text': q['text'],
            'options': q['options'],
        })
    random.shuffle(questions)
    return jsonify({'questions': questions})


@app.route('/api/submit', methods=['POST'])
def api_submit():
    data = request.get_json()
    # data = {'answers': {str(q_id): {'value': int, 'category': int}, ...}}
    answers = data.get('answers', {})

    category_scores = [1.0] * NUM_CATEGORIES
    for q_id_str, ans in answers.items():
        cat = ans['category']
        category_scores[cat] = float(ans['value'])

    group_id = model.predict(category_scores)
    info = GROUP_INFO[group_id]

    foods = info['foods'][:]
    highlight = None
    if group_id == 10:
        highlight = random.choice(foods)

    result_id = db.save_result(
        category_scores=category_scores,
        group_id=group_id,
        group_name=info['name'],
        foods=foods,
        highlight=highlight,
    )
    return jsonify({'result_id': result_id})


@app.route('/result/<int:result_id>')
def result(result_id):
    data = db.get_result(result_id)
    if not data:
        return redirect(url_for('index'))
    group_info = GROUP_INFO[data['group_id']]
    return render_template('result.html', result=data, group_info=group_info,
                           category_names=CATEGORY_NAMES)


@app.route('/history')
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    results = db.get_results_paginated(page=page, per_page=per_page)
    total = db.get_result_count()
    total_pages = (total + per_page - 1) // per_page
    return render_template('history.html', results=results,
                           page=page, total_pages=total_pages, total=total)


@app.route('/api/retrain', methods=['POST'])
def api_retrain():
    training_data = db.get_training_data()
    count = len(training_data)
    if count < 50:
        return jsonify({
            'success': False,
            'message': f'再学習にはデータが50件必要です（現在 {count} 件）'
        })
    result = model.retrain(training_data)
    acc = result.get('accuracy')
    acc_str = f'{acc:.1%}' if acc is not None else '不明'
    return jsonify({
        'success': True,
        'message': f'{count} 件のデータで再学習しました（精度: {acc_str}）'
    })


@app.route('/api/stats')
def api_stats():
    return jsonify({
        'count': db.get_result_count(),
        'distribution': db.get_group_distribution(),
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
