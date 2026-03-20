import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'dinner.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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
        conn.commit()


class Database:
    def __init__(self):
        init_db()

    def save_result(self, category_scores, group_id, group_name, foods, highlight=None):
        s, f, t, v, so, d, c = category_scores
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            cur = conn.execute(
                '''INSERT INTO quiz_results
                   (created_at, stress, fatigue, tension, vitality, social, desire, confusion,
                    group_id, group_name, foods, highlight)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (now, s, f, t, v, so, d, c, group_id, group_name,
                 json.dumps(foods, ensure_ascii=False), highlight)
            )
            conn.commit()
            return cur.lastrowid

    def get_result(self, result_id):
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM quiz_results WHERE id = ?', (result_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_all_results(self, limit=100):
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT * FROM quiz_results ORDER BY id DESC LIMIT ?', (limit,)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_results_paginated(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT * FROM quiz_results ORDER BY id DESC LIMIT ? OFFSET ?',
                (per_page, offset)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_result_count(self):
        with get_conn() as conn:
            return conn.execute('SELECT COUNT(*) FROM quiz_results').fetchone()[0]

    def get_training_data(self):
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT stress, fatigue, tension, vitality, social, desire, confusion, group_id'
                ' FROM quiz_results'
            ).fetchall()
        return [dict(r) for r in rows]

    def get_group_distribution(self):
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT group_id, group_name, COUNT(*) as cnt'
                ' FROM quiz_results GROUP BY group_id ORDER BY group_id'
            ).fetchall()
        return [dict(r) for r in rows]

    def _row_to_dict(self, row):
        d = dict(row)
        d['foods'] = json.loads(d['foods'])
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
