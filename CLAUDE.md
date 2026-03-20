# 今夜なに食べる？ (DinnerDecider)

## 概要
35問の質問バンクからランダムで5問を出題し、7カテゴリスコアを算出。
scikit-learnの決定木で10グループに分類し、夕食を提案するWebアプリ。

## 技術スタック
- バックエンド: Python 3.x + Flask
- データベース: SQLite (`dinner.db`)
- フロントエンド: HTML + CSS + JavaScript (Chart.js for radar chart)
- 機械学習: scikit-learn (DecisionTreeClassifier)

## ファイル構成
```
DinnerDecider/
├── app.py              # Flaskメインアプリ
├── database.py         # SQLite操作
├── ml_model.py         # 決定木モデル・グループ定義
├── questions_data.py   # 35問の質問バンク
├── requirements.txt
├── model.pkl           # 学習済みモデル (自動生成)
├── dinner.db           # SQLiteデータベース (自動生成)
├── static/
│   ├── css/style.css
│   └── js/app.js
└── templates/
    ├── base.html
    ├── index.html
    ├── quiz.html
    ├── result.html
    └── history.html
```

## セットアップ
```bash
cd /Users/adachitaiki/DinnerDecider
pip install -r requirements.txt
python app.py
# → http://localhost:5000 でアクセス
```

## アーキテクチャ

### 質問選択アルゴリズム
- 7カテゴリ（ストレス・疲労・緊張・活気・社会性・欲求・混乱）から5カテゴリをランダム選択
- 各カテゴリから1問ずつランダム選択 → 合計5問
- 選ばれなかった2カテゴリはニュートラルスコア(1.0)を付与

### スコア算出
- 各質問の回答値: 0〜3
- カテゴリスコア: 回答値そのまま(0〜3)
- 未選択カテゴリ: 1.0（ニュートラル）

### MLモデル
- 初回起動時: 合成訓練データ（各グループ100サンプル）で決定木を学習
- モデルは `model.pkl` に保存、再起動時に読み込み
- 50件以上のユーザーデータが蓄積されたら `/api/retrain` で再学習可能

### 10グループ定義
| ID | グループ名 | 特徴 |
|----|----------|------|
| G1 | 限界戦士 | ストレス・疲労が高い |
| G2 | ご褒美モード | 欲求・活気が高い |
| G3 | 癒しが欲しい | 緊張・疲労が高い |
| G4 | 健康意識モード | 活気が高く、ストレス・疲労が低い |
| G5 | 省エネモード | 疲労が高く、活気・欲求が低い |
| G6 | 発散したい | ストレスが高く、緊張が低い |
| G7 | 社交モード | 社会性・活気が高い |
| G8 | しんみりモード | 混乱が高く、社会性・活気が低い |
| G9 | チャレンジャー | 活気・欲求が高く、疲労が低い |
| G10 | 普通の日 | すべてバランス型（料理はランダム提案） |

## API エンドポイント
- `GET /` — トップ画面
- `GET /quiz` — クイズ画面
- `GET /api/questions` — ランダム5問取得
- `POST /api/submit` — 回答送信・グループ判定
- `GET /result/<id>` — 結果画面
- `GET /history` — 履歴一覧
- `POST /api/retrain` — モデル再学習（50件以上必要）
- `GET /api/stats` — 統計情報
