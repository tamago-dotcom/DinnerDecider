"""診断用質問バンク。

7カテゴリの質問を定義するデータモジュール（計34問）。
各カテゴリのインデックスは以下の通り:
    0: ストレス・怒り
    1: 疲労・無気力
    2: 緊張・不安
    3: 活気・ポジティブ
    4: 社会性・人間関係
    5: 欲求・ご褒美感
    6: 混乱・集中度

各質問の構造:
    id (int): 質問の一意ID（1〜35）。
    category (int): カテゴリインデックス（0〜6）。
    text (str): 質問文。
    options (list[dict]): 選択肢のリスト。
        各選択肢は {'value': int, 'label': str} の形式。
        value は回答得点（0〜3）。
"""

QUESTIONS = [
    # ===== ストレス・怒り (category=0) =====
    {
        'id': 1, 'category': 0,
        'text': '今日、思い通りにいかないことがありましたか？',
        'options': [
            {'value': 0, 'label': '全くない'},
            {'value': 1, 'label': '少しあった'},
            {'value': 2, 'label': 'かなりあった'},
            {'value': 3, 'label': 'すごくあった'},
        ]
    },
    {
        'id': 2, 'category': 0,
        'text': '今、誰かにイライラしていますか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': 'ちょっと'},
            {'value': 2, 'label': 'まあまあ'},
            {'value': 3, 'label': 'かなり'},
        ]
    },
    {
        'id': 3, 'category': 0,
        'text': '今日、声を荒げたくなる瞬間はありましたか？',
        'options': [
            {'value': 0, 'label': 'なかった'},
            {'value': 1, 'label': '1回くらい'},
            {'value': 2, 'label': '何度かあった'},
        ]
    },
    {
        'id': 4, 'category': 0,
        'text': '今夜、何かをぶつけたい・発散したい気分ですか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
        ]
    },
    {
        'id': 5, 'category': 0,
        'text': '今日の自分に点数をつけるなら？',
        'options': [
            {'value': 3, 'label': '20点以下...'},
            {'value': 2, 'label': '50点くらい'},
            {'value': 1, 'label': '80点'},
            {'value': 0, 'label': '満点！'},
        ]
    },

    # ===== 疲労・無気力 (category=1) =====
    {
        'id': 6, 'category': 1,
        'text': '今の体はどんな感じですか？',
        'options': [
            {'value': 3, 'label': 'ぐったり'},
            {'value': 2, 'label': 'ちょっと疲れた'},
            {'value': 1, 'label': '普通'},
            {'value': 0, 'label': '元気'},
        ]
    },
    {
        'id': 8, 'category': 1,
        'text': '今日、何時間くらい動き続けていましたか？',
        'options': [
            {'value': 0, 'label': '3時間以下'},
            {'value': 1, 'label': '5〜8時間'},
            {'value': 2, 'label': '8時間以上'},
            {'value': 3, 'label': 'ずっと動いてた'},
        ]
    },
    {
        'id': 9, 'category': 1,
        'text': '今、横になりたい気持ちはどのくらいですか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
            {'value': 3, 'label': '今すぐ寝たい'},
        ]
    },
    {
        'id': 10, 'category': 1,
        'text': '今日の疲れは体と心どちらが強いですか？',
        'options': [
            {'value': 0, 'label': 'どちらでもない'},
            {'value': 2, 'label': '体が疲れた'},
            {'value': 2, 'label': '心が疲れた'},
            {'value': 3, 'label': '両方'},
        ]
    },

    # ===== 緊張・不安 (category=2) =====
    {
        'id': 11, 'category': 2,
        'text': '今、何か心配なことがありますか？',
        'options': [
            {'value': 0, 'label': '特にない'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'まあまあ'},
            {'value': 3, 'label': 'かなり'},
        ]
    },
    {
        'id': 12, 'category': 2,
        'text': '明日のことを考えると気持ちはどうですか？',
        'options': [
            {'value': 0, 'label': '楽しみ'},
            {'value': 1, 'label': '普通'},
            {'value': 2, 'label': 'ちょっと不安'},
            {'value': 3, 'label': '憂鬱'},
        ]
    },
    {
        'id': 13, 'category': 2,
        'text': '今夜、静かな場所でひとりになりたいですか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
            {'value': 3, 'label': 'ぜひそうしたい'},
        ]
    },
    {
        'id': 14, 'category': 2,
        'text': '今、胃や胸のあたりがモヤモヤしていますか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
        ]
    },
    {
        'id': 15, 'category': 2,
        'text': '今日、深呼吸したくなる瞬間がありましたか？',
        'options': [
            {'value': 0, 'label': 'なかった'},
            {'value': 1, 'label': '1〜2回'},
            {'value': 2, 'label': '何度もあった'},
        ]
    },

    # ===== 活気・ポジティブ (category=3) =====
    {
        'id': 16, 'category': 3,
        'text': '今日、いいことはありましたか？',
        'options': [
            {'value': 0, 'label': '全くない'},
            {'value': 1, 'label': '小さなことが1つ'},
            {'value': 2, 'label': 'いくつかあった'},
            {'value': 3, 'label': '最高の1日！'},
        ]
    },
    {
        'id': 17, 'category': 3,
        'text': '今夜、何か新しいことに挑戦したい気分ですか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': 'まあまあ'},
            {'value': 2, 'label': 'かなり'},
        ]
    },
    {
        'id': 18, 'category': 3,
        'text': '今の気分を天気に例えると？',
        'options': [
            {'value': 0, 'label': '⛈ 嵐'},
            {'value': 1, 'label': '☁️ 曇り'},
            {'value': 2, 'label': '⛅ 晴れ時々曇り'},
            {'value': 3, 'label': '☀️ 快晴'},
        ]
    },
    {
        'id': 19, 'category': 3,
        'text': '今夜、誰かと一緒に食べたいですか？',
        'options': [
            {'value': 0, 'label': 'ひとりがいい'},
            {'value': 1, 'label': 'どちらでも'},
            {'value': 2, 'label': '誰かと食べたい'},
        ]
    },
    {
        'id': 20, 'category': 3,
        'text': '今日の自分をひと言で表すと？',
        'options': [
            {'value': 0, 'label': 'ぐったり'},
            {'value': 1, 'label': 'ぼんやり'},
            {'value': 2, 'label': 'まあまあ'},
            {'value': 3, 'label': 'いい感じ！'},
        ]
    },

    # ===== 社会性・人間関係 (category=4) =====
    {
        'id': 21, 'category': 4,
        'text': '今日、誰かに感謝されたり、ほめられましたか？',
        'options': [
            {'value': 0, 'label': 'なかった'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'けっこうあった'},
        ]
    },
    {
        'id': 22, 'category': 4,
        'text': '今夜、人と話したいですか？',
        'options': [
            {'value': 0, 'label': '完全にひとり'},
            {'value': 1, 'label': 'どちらでも'},
            {'value': 2, 'label': '誰かと話したい'},
        ]
    },
    {
        'id': 23, 'category': 4,
        'text': '今日、誰かに気を使いすぎて疲れましたか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
        ]
    },
    {
        'id': 24, 'category': 4,
        'text': '今夜は賑やかな場所と静かな場所、どちらで食べたいですか？',
        'options': [
            {'value': 0, 'label': '静かな場所'},
            {'value': 1, 'label': 'どちらでも'},
            {'value': 2, 'label': '賑やかな場所'},
        ]
    },
    {
        'id': 25, 'category': 4,
        'text': '今日、笑いましたか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり笑った'},
            {'value': 3, 'label': '大笑いした'},
        ]
    },

    # ===== 欲求・ご褒美感 (category=5) =====
    {
        'id': 26, 'category': 5,
        'text': '今夜、自分にご褒美をあげたい気分ですか？',
        'options': [
            {'value': 0, 'label': '全然'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなり'},
            {'value': 3, 'label': '絶対あげたい'},
        ]
    },
    {
        'id': 27, 'category': 5,
        'text': '今夜の食事、どのくらいお金をかけてもいいですか？',
        'options': [
            {'value': 0, 'label': 'できるだけ安く'},
            {'value': 1, 'label': '普通でいい'},
            {'value': 2, 'label': '少し奮発'},
            {'value': 3, 'label': 'がっつり奮発'},
        ]
    },
    {
        'id': 28, 'category': 5,
        'text': '今夜の食事、がっつり食べたいですか？',
        'options': [
            {'value': 0, 'label': '軽めがいい'},
            {'value': 1, 'label': '普通くらい'},
            {'value': 2, 'label': 'がっつり食べたい'},
        ]
    },
    {
        'id': 29, 'category': 5,
        'text': '今夜は体にいいものか好きなものか？',
        'options': [
            {'value': 0, 'label': 'ヘルシー重視'},
            {'value': 1, 'label': 'どちらでも'},
            {'value': 2, 'label': '好きなもの優先'},
        ]
    },
    {
        'id': 30, 'category': 5,
        'text': '今、何か特定のものが食べたい気がしますか？',
        'options': [
            {'value': 0, 'label': '特にない'},
            {'value': 1, 'label': 'なんとなくある'},
            {'value': 2, 'label': 'はっきりある'},
        ]
    },

    # ===== 混乱・集中度 (category=6) =====
    {
        'id': 31, 'category': 6,
        'text': '今日、頭の中がごちゃごちゃしていましたか？',
        'options': [
            {'value': 0, 'label': 'スッキリしてた'},
            {'value': 1, 'label': '少しごちゃごちゃ'},
            {'value': 2, 'label': 'かなりごちゃごちゃ'},
        ]
    },
    {
        'id': 32, 'category': 6,
        'text': '今夜、メニューをじっくり選ぶ余裕がありますか？',
        'options': [
            {'value': 2, 'label': '全くない'},
            {'value': 1, 'label': 'あまりない'},
            {'value': 1, 'label': 'まあある'},
            {'value': 0, 'label': '十分ある'},
        ]
    },
    {
        'id': 33, 'category': 6,
        'text': '今日、何かを忘れたり、ミスが多かったですか？',
        'options': [
            {'value': 0, 'label': '全くない'},
            {'value': 1, 'label': '少し'},
            {'value': 2, 'label': 'かなりあった'},
        ]
    },
    {
        'id': 34, 'category': 6,
        'text': '今夜の食事、パッと決めたいですか？',
        'options': [
            {'value': 2, 'label': 'パッと決めたい'},
            {'value': 1, 'label': 'どちらでも'},
            {'value': 0, 'label': 'じっくり選びたい'},
        ]
    },
    {
        'id': 35, 'category': 6,
        'text': '今の気持ちをひと言で表すと？',
        'options': [
            {'value': 0, 'label': 'わくわく'},
            {'value': 1, 'label': 'すっきり'},
            {'value': 2, 'label': 'ぼんやり'},
            {'value': 3, 'label': 'モヤモヤ'},
        ]
    },
]
