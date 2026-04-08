"""気分メシ！ Flaskアプリケーション。

ルーティング・APIエンドポイントの定義。
診断・結果表示・履歴・フィードバック・ML再学習の各機能を提供する。
"""
import random
import json
import os
import uuid
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, send_from_directory,
)

from database import Database
from ml_model import MLModel, GROUP_INFO, CATEGORY_NAMES
from questions_data import QUESTIONS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dinner_decider_2024_secret')

db = Database()
model = MLModel()

NUM_QUESTIONS = 5   # 1回の診断で出題する問数
NUM_CATEGORIES = 7  # 気分カテゴリの総数


@app.before_request
def ensure_session_id():
    """リクエストごとにブラウザセッションIDを保証する。

    Flaskセッションに 'sid' キーが存在しない場合、
    UUID4 で一意のIDを生成して設定する。
    ブラウザを閉じると session が破棄されるため、
    IDは自動的にリセットされる。
    """
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())


@app.route('/sw.js')
def service_worker():
    """Service Worker スクリプトをルートスコープで配信する。

    PWA の Service Worker はスコープの都合上、/sw.js として
    提供する必要があるため、static/js/sw.js を専用ルートで返す。

    Returns:
        Response: sw.js ファイル（Cache-Control: no-cache）。
    """
    response = send_from_directory('static/js', 'sw.js')
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/')
def index():
    """トップページを返す。

    全ユーザーの診断総件数をカウントして表示する。

    Returns:
        Response: index.html のレンダリング結果。
    """
    count = db.get_result_count()  # 全ユーザー合計の診断件数
    return render_template('index.html', count=count)


@app.route('/quiz')
def quiz():
    """クイズ（診断）画面を返す。

    Returns:
        Response: quiz.html のレンダリング結果。
    """
    return render_template('quiz.html')


@app.route('/api/questions')
def api_questions():
    """ランダムに選んだ5問をJSON形式で返す。

    7カテゴリからランダムに5カテゴリを選び、
    各カテゴリから1問をランダムに選択する。
    最後に出題順をシャッフルしてカテゴリの偏りを隠す。

    Returns:
        Response: 以下の構造のJSONレスポンス。
            {
                "questions": [
                    {
                        "id": int,
                        "category": int,
                        "text": str,
                        "options": list[dict]
                    },
                    ...
                ]
            }
    """
    # 7カテゴリからNUM_QUESTIONS個を重複なしで選択
    selected_cats = random.sample(range(NUM_CATEGORIES), NUM_QUESTIONS)
    questions = []
    for cat_idx in selected_cats:
        # 該当カテゴリの問題プールから1問ランダム選択
        pool = [q for q in QUESTIONS if q['category'] == cat_idx]
        q = random.choice(pool)
        questions.append({
            'id': q['id'],
            'category': q['category'],
            'text': q['text'],
            'options': q['options'],
        })
    random.shuffle(questions)  # カテゴリ順を隠すためシャッフル
    return jsonify({'questions': questions})


@app.route('/api/submit', methods=['POST'])
def api_submit():
    """診断回答を受け取り、グループ判定と結果保存を行う。

    回答から7カテゴリスコアを計算し、決定木モデルで
    10グループのいずれかに分類する。G10（普通の日）は
    提案料理をランダムに1品ハイライトする。

    リクエストボディ:
        {
            "answers": {
                "<question_id>": {
                    "value": int,      # 回答の得点 (0-3)
                    "category": int    # カテゴリインデックス (0-6)
                },
                ...
            }
        }

    Returns:
        Response: 以下の構造のJSONレスポンス。
            {"result_id": int}
    """
    data = request.get_json()
    answers = data.get('answers', {})

    # 未回答カテゴリはニュートラル値 1.0 で初期化
    category_scores = [1.0] * NUM_CATEGORIES
    for q_id_str, ans in answers.items():
        cat = ans['category']
        category_scores[cat] = float(ans['value'])

    group_id = model.predict(category_scores)
    info = GROUP_INFO[group_id]

    foods = info['foods'][:]  # リストをコピーして元データを保護
    highlight = None
    if group_id == 10:  # G10のみ提案料理をランダムに1品強調表示
        highlight = random.choice(foods)

    session_id = session.get('sid', '')
    result_id = db.save_result(
        category_scores=category_scores,
        group_id=group_id,
        group_name=info['name'],
        foods=foods,
        highlight=highlight,
        session_id=session_id,
    )
    return jsonify({'result_id': result_id})


@app.route('/result/<int:result_id>')
def result(result_id):
    """指定IDの診断結果ページを返す。

    存在しない result_id が指定された場合はトップへリダイレクトする。

    Args:
        result_id (int): 診断結果のID（URLパスパラメータ）。

    Returns:
        Response: result.html のレンダリング結果。
            存在しない場合は index へのリダイレクト。
    """
    data = db.get_result(result_id)
    if not data:
        return redirect(url_for('index'))
    group_info = GROUP_INFO[data['group_id']]
    return render_template(
        'result.html',
        result=data,
        group_info=group_info,
        category_names=CATEGORY_NAMES,
    )


@app.route('/history')
def history():
    """現在のセッションの履歴一覧ページを返す。

    Flaskセッションの 'sid' に紐づく診断結果のみを表示する。
    他ユーザーの結果は表示されない。
    再学習ボタンは廃止し、開発者がClaude Code経由で
    POST /api/retrain を直接呼び出す運用とする。

    クエリパラメータ:
        page (int): ページ番号（デフォルト: 1）。

    Returns:
        Response: history.html のレンダリング結果。
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sid = session.get('sid', '')
    results = db.get_results_paginated(
        page=page, per_page=per_page, session_id=sid,
    )
    total = db.get_result_count(session_id=sid)
    total_pages = (total + per_page - 1) // per_page  # 切り上げ除算
    return render_template(
        'history.html',
        results=results,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """フィードバック（実際に食べた料理・満足度）を保存する。

    同一 result_id へのフィードバックは上書き保存される。

    リクエストボディ:
        {
            "result_id": int,       # 対象の診断結果ID
            "actual_food": str,     # 実際に食べた料理名（空文字不可）
            "satisfaction": int     # 満足度 1〜5 の整数
        }

    Returns:
        Response: 以下の構造のJSONレスポンス。
            成功: {"success": true}
            失敗: {"success": false, "message": str}

    Raises:
        なし（エラーはJSONレスポンスで返す）
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'リクエストが不正です'})

    result_id = data.get('result_id')
    actual_food = data.get('actual_food', '').strip()
    satisfaction = data.get('satisfaction')

    if not actual_food:
        return jsonify(
            {'success': False, 'message': '食べた料理を入力してください'}
        )
    # isinstance チェックで文字列 '5' などの型違いを弾く
    if (satisfaction is None
            or not isinstance(satisfaction, int)
            or not (1 <= satisfaction <= 5)):
        return jsonify({
            'success': False,
            'message': '満足度は1〜5の整数で入力してください',
        })

    result_row = db.get_result(result_id)
    if not result_row:
        return jsonify(
            {'success': False, 'message': '対応する診断結果が見つかりません'}
        )

    db.save_feedback(result_id, actual_food, satisfaction)
    return jsonify({'success': True})


@app.route('/api/feedback/count')
def api_feedback_count():
    """フィードバックの総件数をJSON形式で返す。

    Returns:
        Response: {"count": int} の形式のJSONレスポンス。
    """
    return jsonify({'count': db.get_feedback_count()})


@app.route('/api/retrain', methods=['POST'])
def api_retrain():
    """決定木モデルをユーザーデータで再学習する。

    quiz_results のデータが50件未満の場合は再学習を拒否する。
    50件以上の場合、フィードバックデータも組み合わせて再学習する。

    Returns:
        Response: 以下の構造のJSONレスポンス。
            成功: {"success": true, "message": str}
            失敗: {"success": false, "message": str}
    """
    training_data = db.get_training_data()
    count = len(training_data)
    if count < 50:  # 再学習に必要な最低件数
        return jsonify({
            'success': False,
            'message': f'再学習にはデータが50件必要です（現在 {count} 件）',
        })
    feedback_data = db.get_feedback_for_training()
    result = model.retrain(training_data, feedback_data=feedback_data)
    acc = result.get('accuracy')
    acc_str = f'{acc:.1%}' if acc is not None else '不明'
    return jsonify({
        'success': True,
        'message': f'{count} 件のデータで再学習しました（精度: {acc_str}）',
    })


@app.route('/api/stats')
def api_stats():
    """診断統計情報をJSON形式で返す。

    全ユーザーの診断件数とグループ別の分布を返す。

    Returns:
        Response: 以下の構造のJSONレスポンス。
            {
                "count": int,
                "distribution": list[dict]
            }
    """
    return jsonify({
        'count': db.get_result_count(),
        'distribution': db.get_group_distribution(),
    })


if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
    )
