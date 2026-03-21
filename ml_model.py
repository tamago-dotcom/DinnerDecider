"""機械学習モデルモジュール。

scikit-learnの決定木（DecisionTreeClassifier）を用いて
7カテゴリスコアから10の夕食グループを分類する。
初回起動時は合成訓練データで学習し、model.pkl に保存する。
ユーザーデータが50件以上蓄積されると再学習が可能になる。
"""
import numpy as np
import pickle
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

# DATABASE_URL のディレクトリに model.pkl を保存する（本番環境対応）
_data_dir = os.path.dirname(
    os.environ.get(
        'DATABASE_URL',
        os.path.join(os.path.dirname(__file__), 'dinner.db'),
    )
)
MODEL_PATH = os.path.join(_data_dir, 'model.pkl')

CATEGORY_NAMES = ['ストレス', '疲労', '緊張', '活気', '社会性', '欲求', '混乱']

# カテゴリインデックスの定数（可読性向上のため）
STRESS, FATIGUE, TENSION, VITALITY, SOCIAL, DESIRE, CONFUSION = range(7)

GROUP_INFO = {
    1: {
        'name': '限界戦士',
        'emoji': '💪',
        'description': (
            '今日は本当によく頑張りました！ストレスと疲れがたまっていますね。'
            'しっかり食べて英気を養いましょう。明日また戦えるように！'
        ),
        'foods': ['こってりラーメン', '牛丼', '唐揚げ定食', '焼肉'],
    },
    2: {
        'name': 'ご褒美モード',
        'emoji': '🎉',
        'description': (
            '自分を褒めてあげたい気分ですね！今夜は少し特別な食事で、'
            '自分へのご褒美を。頑張ったあなたにはそれだけの価値があります。'
        ),
        'foods': ['寿司', '焼肉', 'ステーキ', '豪華な鍋'],
    },
    3: {
        'name': '癒しが欲しい',
        'emoji': '🍵',
        'description': (
            '心も体も疲れていて、優しい食事が恋しい気分。'
            '温かくてほっとする料理で、ゆっくり自分を癒してあげましょう。'
        ),
        'foods': ['おでん', '鍋', '茶碗蒸し', 'うどん'],
    },
    4: {
        'name': '健康意識モード',
        'emoji': '🥗',
        'description': (
            '体に良いものを食べたい気分！バランスの取れた食事で心も体も整えましょう。'
            '今の意識の高さを食事にも活かして。'
        ),
        'foods': ['和定食', 'サラダチキン', '野菜炒め', '刺身定食'],
    },
    5: {
        'name': '省エネモード',
        'emoji': '😴',
        'description': (
            '今夜は手軽に済ませたい気分。シンプルで温かい食事でゆっくり休んでください。'
            '頑張った体に優しいものを。'
        ),
        'foods': ['お茶漬け', 'そば', 'おにぎり', '雑炊'],
    },
    6: {
        'name': '発散したい',
        'emoji': '🌶️',
        'description': (
            'モヤモヤを吹き飛ばしたい！刺激的な食事でスッキリしましょう。'
            '辛さとパワーで今日のストレスをやっつけて！'
        ),
        'foods': ['豚キムチ', '激辛ラーメン', '麻婆豆腐', 'ビビンバ'],
    },
    7: {
        'name': '社交モード',
        'emoji': '🍻',
        'description': (
            '誰かと一緒に楽しく食べたい気分！賑やかな食事で盛り上がりましょう。'
            '今夜は人とのつながりを大切に。'
        ),
        'foods': ['居酒屋系', '鍋', 'たこ焼き', '焼き鳥'],
    },
    8: {
        'name': 'しんみりモード',
        'emoji': '🥹',
        'description': (
            '今夜は落ち着いてゆっくりしたい気分。'
            '懐かしくて心に染みる料理が合います。自分と向き合う夜に。'
        ),
        'foods': ['肉じゃが', '親子丼', '味噌汁定食', '卵かけご飯'],
    },
    9: {
        'name': 'チャレンジャー',
        'emoji': '🌍',
        'description': (
            '今夜はいつもと違うものを食べてみたい！'
            '冒険心旺盛なあなたに、新しい味の世界を。好奇心のままに。'
        ),
        'foods': ['エスニック料理', 'イタリアン', 'タイ料理', 'インドカレー'],
    },
    10: {
        'name': '普通の日',
        'emoji': '🍽️',
        'description': (
            '今日は穏やかな一日でしたね。ほっとする定番料理でのんびり過ごしましょう。'
            '今夜のおすすめはこれ！'
        ),
        'foods': ['カレー', 'ハンバーグ', '生姜焼き', 'パスタ'],
    },
}


def food_to_group(food_name):
    """料理名からグループIDを返す。

    GROUP_INFO の各グループの foods リストを検索し、
    完全一致または前方一致するグループIDを返す。
    複数のグループに同じ料理名が存在する場合は最初に見つかった
    グループのIDを返す（既知の課題: 焼肉・鍋が複数グループに存在）。

    Args:
        food_name (str | None): 検索する料理名。
            None または空文字の場合は None を返す。

    Returns:
        int | None: 一致したグループID（1〜10）。
            見つからない場合は None。
    """
    if not food_name:
        return None
    food_lower = food_name.lower()
    for group_id, info in GROUP_INFO.items():
        for food in info['foods']:
            # 完全一致・前方一致（どちらの方向も）で検索
            if (food == food_name
                    or food.lower().startswith(food_lower)
                    or food_lower.startswith(food.lower())):
                return group_id
    return None


def _rand(lo, hi, n):
    """整数の一様乱数を float 配列で生成する。

    Args:
        lo (int): 乱数の最小値（含む）。
        hi (int): 乱数の最大値（含む）。
        n (int): 生成する要素数。

    Returns:
        numpy.ndarray: shape=(n,) の float64 配列。
    """
    return np.random.randint(lo, hi + 1, size=n).astype(float)


def _generate_training_data():
    """決定木の初期学習用に合成訓練データを生成する。

    各グループの典型的なカテゴリスコアパターンに基づき、
    グループごとに n=120 サンプルを生成する。
    乱数シードを固定（42）することで再現性を保証する。

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]:
            X: shape=(n_samples, 7) の特徴量行列。
               列順: [stress, fatigue, tension, vitality,
                      social, desire, confusion]
            y: shape=(n_samples,) のラベル配列（グループID 1〜10）。
    """
    np.random.seed(42)  # 再現性のためシードを固定
    X, y = [], []
    n = 120  # グループあたりのサンプル数

    def add(group_id, s, f, t, v, so, d, c):
        """1グループ分のサンプルをX・yに追加する内部関数。

        Args:
            group_id (int): グループID（1〜10）。
            s, f, t, v, so, d, c (numpy.ndarray): 各カテゴリのスコア配列。
        """
        for i in range(n):
            X.append([s[i], f[i], t[i], v[i], so[i], d[i], c[i]])
            y.append(group_id)

    # G1 限界戦士: high stress + high fatigue
    add(1,
        _rand(2, 3, n), _rand(2, 3, n), _rand(1, 2, n),
        _rand(0, 1, n), _rand(0, 2, n), _rand(0, 2, n), _rand(0, 2, n))

    # G2 ご褒美モード: high desire + high vitality
    add(2,
        _rand(0, 2, n), _rand(0, 1, n), _rand(0, 1, n),
        _rand(2, 3, n), _rand(0, 2, n), _rand(2, 3, n), _rand(0, 1, n))

    # G3 癒しが欲しい: high tension + fatigue, low stress
    add(3,
        _rand(0, 1, n), _rand(1, 3, n), _rand(2, 3, n),
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n), _rand(1, 2, n))

    # G4 健康意識モード: high vitality, low stress/fatigue/desire
    add(4,
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n),
        _rand(2, 3, n), _rand(1, 2, n), _rand(0, 1, n), _rand(0, 1, n))

    # G5 省エネモード: high fatigue, low vitality/desire
    add(5,
        _rand(0, 1, n), _rand(2, 3, n), _rand(1, 2, n),
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n), _rand(1, 2, n))

    # G6 発散したい: high stress, low tension
    add(6,
        _rand(2, 3, n), _rand(0, 1, n), _rand(0, 1, n),
        _rand(1, 2, n), _rand(0, 1, n), _rand(1, 2, n), _rand(1, 2, n))

    # G7 社交モード: high social + vitality
    add(7,
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n),
        _rand(2, 3, n), _rand(2, 3, n), _rand(1, 2, n), _rand(0, 1, n))

    # G8 しんみりモード: high confusion, low social/vitality
    add(8,
        _rand(0, 1, n), _rand(1, 2, n), _rand(1, 2, n),
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n), _rand(2, 3, n))

    # G9 チャレンジャー: high vitality + desire, low fatigue/tension
    add(9,
        _rand(0, 1, n), _rand(0, 1, n), _rand(0, 1, n),
        _rand(2, 3, n), _rand(1, 2, n), _rand(2, 3, n), _rand(0, 1, n))

    # G10 普通の日: balanced (all 1-2)
    add(10,
        _rand(1, 2, n), _rand(1, 2, n), _rand(1, 2, n),
        _rand(1, 2, n), _rand(1, 2, n), _rand(1, 2, n), _rand(1, 2, n))

    return np.array(X), np.array(y)


class MLModel:
    """決定木による夕食グループ分類モデル。

    インスタンス化時に model.pkl が存在すればロードし、
    なければ合成訓練データで初期学習を行う。
    """

    def __init__(self):
        """モデルを初期化する。

        model.pkl が存在する場合はロードして再利用する。
        ロードに失敗した場合（破損・非互換など）は
        初期学習を実行して新規モデルを作成する。
        """
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    self.clf = pickle.load(f)
                return  # ロード成功時はここで終了
            except Exception:
                pass  # ロード失敗時は初期学習にフォールバック
        self.clf = self._train_initial()
        self._save()

    def _train_initial(self):
        """合成訓練データで決定木を初期学習する。

        max_depth=6, min_samples_leaf=5 で過学習を抑制する。

        Returns:
            DecisionTreeClassifier: 学習済みの決定木モデル。
        """
        X, y = _generate_training_data()
        clf = DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=5, random_state=42,
        )
        clf.fit(X, y)
        return clf

    def predict(self, category_scores):
        """7カテゴリスコアからグループIDを予測する。

        Args:
            category_scores (list[float]): 7カテゴリのスコアリスト。
                順序: [stress, fatigue, tension, vitality,
                       social, desire, confusion]
                各値は 0.0〜3.0 の範囲を想定。

        Returns:
            int: 予測されたグループID（1〜10）。
        """
        X = np.array(category_scores, dtype=float).reshape(1, -1)
        return int(self.clf.predict(X)[0])

    def retrain(self, training_data, feedback_data=None):
        """実ユーザーデータとフィードバックデータで決定木を再学習する。

        合成データ（1200件）+ 実データ + フィードバック変換データを
        マージして学習する。満足度4以上のフィードバックは
        重みづけとして2回追加する。

        Args:
            training_data (list[dict]): quiz_results の全件データ。
                各辞書に stress〜confusion と group_id を含む。
            feedback_data (list[dict] | None): フィードバックデータ。
                各辞書に stress〜confusion・actual_food・satisfaction
                を含む。None の場合はフィードバックを使用しない。

        Returns:
            dict: 以下のキーを持つ辞書。
                accuracy (float | None): 交差検証の平均精度。
                    計算に失敗した場合は None。
                n_samples (int): 実ユーザーデータの件数。
        """
        X_syn, y_syn = _generate_training_data()  # 合成データ（再現性あり）

        X_real = np.array([
            [d['stress'], d['fatigue'], d['tension'],
             d['vitality'], d['social'], d['desire'], d['confusion']]
            for d in training_data
        ], dtype=float)
        y_real = np.array([d['group_id'] for d in training_data])

        X_parts = [X_syn, X_real]
        y_parts = [y_syn, y_real]

        if feedback_data:
            for fb in feedback_data:
                # 料理名をグループIDに変換（未登録料理はスキップ）
                group_id = food_to_group(fb['actual_food'])
                if group_id is None:
                    continue
                row = [
                    fb['stress'], fb['fatigue'], fb['tension'],
                    fb['vitality'], fb['social'], fb['desire'], fb['confusion'],
                ]
                # 高満足度（4以上）は重みづけとして2回追加
                repeat = 2 if fb['satisfaction'] >= 4 else 1
                for _ in range(repeat):
                    X_parts.append(np.array([row]))
                    y_parts.append(np.array([group_id]))

        X = np.vstack(X_parts)
        y = np.concatenate(y_parts)

        clf = DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=5, random_state=42,
        )
        try:
            # fold数はユニーク classes 数と5の小さい方に制限
            scores = cross_val_score(
                clf, X, y, cv=min(5, len(np.unique(y)))
            )
            accuracy = float(scores.mean())
        except Exception:
            accuracy = None  # サンプル数不足などで失敗した場合

        clf.fit(X, y)
        self.clf = clf
        self._save()
        return {'accuracy': accuracy, 'n_samples': len(X_real)}

    def _save(self):
        """学習済みモデルを model.pkl にpickle形式で保存する。"""
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.clf, f)
