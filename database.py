"""SQLiteデータベース操作モジュール。

quiz_results テーブルと feedback テーブルへの
CRUD操作・マイグレーション・集計クエリを提供する。
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.environ.get(
    'DATABASE_URL',
    os.path.join(os.path.dirname(__file__), 'dinner.db'),
)


def get_conn():
    """SQLiteコネクションを取得する。

    sqlite3.Row をrow_factoryに設定することで、
    カラム名でのアクセスを可能にする。

    Returns:
        sqlite3.Connection: row_factory 設定済みのコネクション。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """データベースとテーブルを初期化する。

    quiz_results・feedback テーブルを CREATE TABLE IF NOT EXISTS で作成する。
    既存DBへの session_id カラム追加マイグレーションも実行する。
    冪等性があるため、起動のたびに呼び出しても安全。
    """
    with get_conn() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT    NOT NULL,
                stress      REAL    NOT NULL,
                fatigue     REAL    NOT NULL,
                tension     REAL    NOT NULL,
                vitality    REAL    NOT NULL,
                social      REAL    NOT NULL,
                desire      REAL    NOT NULL,
                confusion   REAL    NOT NULL,
                group_id    INTEGER NOT NULL,
                group_name  TEXT    NOT NULL,
                foods       TEXT    NOT NULL,
                highlight   TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id    INTEGER NOT NULL REFERENCES quiz_results(id),
                actual_food  TEXT    NOT NULL,
                satisfaction INTEGER NOT NULL CHECK(satisfaction BETWEEN 1 AND 5),
                created_at   TEXT    NOT NULL
            )
        ''')
        # 既存DBに session_id カラムがない場合のみ追加する
        cols = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(quiz_results)"
            ).fetchall()
        ]
        if 'session_id' not in cols:
            conn.execute(
                "ALTER TABLE quiz_results "
                "ADD COLUMN session_id TEXT NOT NULL DEFAULT ''"
            )
        conn.commit()


class Database:
    """SQLiteデータベースへのアクセスを提供するクラス。

    インスタンス化時に init_db() を呼び出してテーブルを保証する。
    """

    def __init__(self):
        """データベースを初期化する。"""
        init_db()

    def save_result(
        self,
        category_scores,
        group_id,
        group_name,
        foods,
        highlight=None,
        session_id='',
    ):
        """診断結果をquiz_resultsテーブルに保存する。

        Args:
            category_scores (list[float]): 7カテゴリのスコアリスト。
                順序: [stress, fatigue, tension, vitality,
                       social, desire, confusion]
            group_id (int): 判定されたグループID（1〜10）。
            group_name (str): グループ名（例: '限界戦士'）。
            foods (list[str]): 提案料理のリスト（4品）。
            highlight (str | None): G10でランダム強調する料理名。
                G10以外は None。
            session_id (str): ブラウザセッションのUUID。
                デフォルトは空文字。

        Returns:
            int: 保存したレコードのID（AUTOINCREMENT値）。
        """
        s, f, t, v, so, d, c = category_scores  # 7カテゴリをアンパック
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            cur = conn.execute(
                '''INSERT INTO quiz_results
                   (created_at, stress, fatigue, tension, vitality,
                    social, desire, confusion,
                    group_id, group_name, foods, highlight, session_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (now, s, f, t, v, so, d, c, group_id, group_name,
                 json.dumps(foods, ensure_ascii=False), highlight, session_id)
            )
            conn.commit()
            return cur.lastrowid

    def get_result(self, result_id):
        """指定IDの診断結果を1件取得する。

        Args:
            result_id (int): 取得対象の診断結果ID。

        Returns:
            dict | None: 結果の辞書。該当レコードがない場合は None。
        """
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM quiz_results WHERE id = ?', (result_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_all_results(self, limit=100):
        """全ユーザーの診断結果を新しい順で取得する。

        ML再学習などセッションを問わず全件が必要な場面で使用する。

        Args:
            limit (int): 取得上限件数。デフォルトは100。

        Returns:
            list[dict]: 診断結果の辞書リスト（新しい順）。
        """
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT * FROM quiz_results ORDER BY id DESC LIMIT ?',
                (limit,)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_results_paginated(self, page=1, per_page=10, session_id=None):
        """診断結果をページネーションで取得する。

        session_id を指定した場合はそのセッションの結果のみ返す。
        None の場合は全ユーザーの結果を返す。

        Args:
            page (int): ページ番号（1始まり）。デフォルトは1。
            per_page (int): 1ページあたりの件数。デフォルトは10。
            session_id (str | None): フィルタするセッションID。
                None の場合は全件対象。

        Returns:
            list[dict]: 該当ページの診断結果辞書リスト（新しい順）。
        """
        offset = (page - 1) * per_page  # ページ番号をオフセットに変換
        with get_conn() as conn:
            if session_id is not None:
                rows = conn.execute(
                    'SELECT * FROM quiz_results'
                    ' WHERE session_id = ?'
                    ' ORDER BY id DESC LIMIT ? OFFSET ?',
                    (session_id, per_page, offset)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT * FROM quiz_results'
                    ' ORDER BY id DESC LIMIT ? OFFSET ?',
                    (per_page, offset)
                ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_result_count(self, session_id=None):
        """診断結果の件数を返す。

        Args:
            session_id (str | None): フィルタするセッションID。
                None の場合は全ユーザーの合計件数を返す。

        Returns:
            int: 診断結果の件数。
        """
        with get_conn() as conn:
            if session_id is not None:
                return conn.execute(
                    'SELECT COUNT(*) FROM quiz_results WHERE session_id = ?',
                    (session_id,)
                ).fetchone()[0]
            return conn.execute(
                'SELECT COUNT(*) FROM quiz_results'
            ).fetchone()[0]

    def get_training_data(self):
        """ML再学習用に全診断結果の7カテゴリスコアとグループIDを返す。

        session_id でフィルタせず、全ユーザーのデータを対象とする。

        Returns:
            list[dict]: 以下のキーを持つ辞書のリスト。
                stress, fatigue, tension, vitality,
                social, desire, confusion, group_id
        """
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT stress, fatigue, tension, vitality,'
                ' social, desire, confusion, group_id'
                ' FROM quiz_results'
            ).fetchall()
        return [dict(r) for r in rows]

    def get_group_distribution(self):
        """グループ別の診断件数を集計して返す。

        Returns:
            list[dict]: 以下のキーを持つ辞書のリスト（group_id昇順）。
                group_id (int), group_name (str), cnt (int)
        """
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT group_id, group_name, COUNT(*) as cnt'
                ' FROM quiz_results GROUP BY group_id ORDER BY group_id'
            ).fetchall()
        return [dict(r) for r in rows]

    def save_feedback(self, result_id, actual_food, satisfaction):
        """フィードバックをfeedbackテーブルに保存する。

        同一 result_id のレコードが既に存在する場合は UPDATE、
        存在しない場合は INSERT を実行する（Upsert相当）。

        Args:
            result_id (int): フィードバック対象の診断結果ID。
            actual_food (str): 実際に食べた料理名。
            satisfaction (int): 満足度（1〜5の整数）。
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            existing = conn.execute(
                'SELECT id FROM feedback WHERE result_id = ?', (result_id,)
            ).fetchone()
            if existing:  # 既存レコードを上書き
                conn.execute(
                    'UPDATE feedback'
                    ' SET actual_food = ?, satisfaction = ?, created_at = ?'
                    ' WHERE result_id = ?',
                    (actual_food, satisfaction, now, result_id)
                )
            else:  # 新規レコードを挿入
                conn.execute(
                    'INSERT INTO feedback'
                    ' (result_id, actual_food, satisfaction, created_at)'
                    ' VALUES (?,?,?,?)',
                    (result_id, actual_food, satisfaction, now)
                )
            conn.commit()

    def get_feedback_count(self):
        """フィードバックの総件数を返す。

        Returns:
            int: feedbackテーブルの行数。
        """
        with get_conn() as conn:
            return conn.execute(
                'SELECT COUNT(*) FROM feedback'
            ).fetchone()[0]

    def get_feedback_for_training(self):
        """ML再学習用にフィードバックと診断スコアを結合して返す。

        feedback テーブルと quiz_results テーブルを result_id で
        INNER JOIN し、7カテゴリスコアと実食料理・満足度を返す。

        Returns:
            list[dict]: 以下のキーを持つ辞書のリスト。
                stress, fatigue, tension, vitality, social,
                desire, confusion, actual_food, satisfaction
        """
        with get_conn() as conn:
            rows = conn.execute(
                '''SELECT qr.stress, qr.fatigue, qr.tension, qr.vitality,
                          qr.social, qr.desire, qr.confusion,
                          fb.actual_food, fb.satisfaction
                   FROM feedback fb
                   JOIN quiz_results qr ON fb.result_id = qr.id'''
            ).fetchall()
        return [dict(r) for r in rows]

    def _row_to_dict(self, row):
        """sqlite3.Row を辞書に変換し、foods と scores を追加する。

        foods カラムはJSON文字列のためデシリアライズする。
        scores キーに7カテゴリスコアの辞書（日本語キー）を追加する。

        Args:
            row (sqlite3.Row): quiz_resultsテーブルの1行。

        Returns:
            dict: 変換済みの辞書。foods はリスト、scores は辞書。
        """
        d = dict(row)
        d['foods'] = json.loads(d['foods'])  # JSON文字列をリストに復元
        d['scores'] = {
            'ストレス': d['stress'],
            '疲労':     d['fatigue'],
            '緊張':     d['tension'],
            '活気':     d['vitality'],
            '社会性':   d['social'],
            '欲求':     d['desire'],
            '混乱':     d['confusion'],
        }
        return d
