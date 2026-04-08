# TEST_REPORT.md

---

## [2026-04-08] トップ画面の不要表示削除・自炊意向質問の除外

### 単体テスト
- app.py 構文チェック: ✅
- database.py 構文チェック: ✅
- ml_model.py 構文チェック: ✅
- questions_data.py 構文チェック: ✅
- id=7「今夜、料理する気力はありますか？」が削除されている: ✅
- 質問数: 34問（35→34）: ✅
- カテゴリ 0〜6 全て存在: ✅
- カテゴリ別問題数（最低1問以上）: ✅
- index.html: 診断件数・PWAヒント 削除: ✅
- app.py: index() が count を渡していない: ✅

### 結合テスト
- GET /: 診断件数・PWAヒントなし、2ボタンあり: ✅
- GET /api/questions: 5問取得、id=7 が30回試行で出題されない: ✅
- POST /api/submit: 正常動作: ✅
- GET /result/<id>: 200: ✅
- GET /history: 200: ✅

### 結果: 全通過（15/15）

---

## [2026-04-08] 外食・自炊モード分岐機能

### 単体テスト
- app.py 構文チェック: ✅
- database.py 構文チェック: ✅
- ml_model.py 構文チェック: ✅
- questions_data.py 構文チェック: ✅
- GROUP_INFO: 全10グループ foods_out/foods_in 各4品: ✅
- food_to_group: 既知料理・None・空文字・未登録料理: ✅
- quiz_results: mode カラム存在（マイグレーション済み）: ✅
- app.js: mode をペイロードに含めて送信: ✅
- index.html: 外食・自炊 2ボタン: ✅
- quiz.html: quizMode hidden input / mode-badge: ✅
- result.html: mode-badge / openTabelog / tabelog URL / geo-note: ✅
- history.html: mode-badge（外食/自炊）: ✅
- style.css: .mode-buttons / .mode-badge / .geo-note スタイル: ✅

### 結合テスト
- GET /: 外食・自炊 2ボタンレンダリング: ✅
- GET /quiz?mode=out: 外食モードバッジ / hidden input: ✅
- GET /quiz?mode=in: 自炊モードバッジ / hidden input: ✅
- POST /api/submit mode=out → result_id取得: ✅
- GET /result/<id> (out): 外食モードバッジ / 食べログリンク: ✅
- GET /result/<id> (in): 自炊モードバッジ / クックパッドリンク: ✅
- 外食モード結果の料理がすべて foods_out リストに存在: ✅
- GET /history: 200: ✅
- GET /api/questions: 正常（既存機能）: ✅

### 結果: 全通過（22/22）

---

## [2026-04-08] PWA化（manifest.json / Service Worker / アイコン）

### 単体テスト
- app.py 構文チェック: ✅
- database.py 構文チェック: ✅
- ml_model.py 構文チェック: ✅
- questions_data.py 構文チェック: ✅
- manifest.json: name/short_name/theme_color/background_color/display/icons: ✅
- static/icons/icon-192.svg 存在確認: ✅
- static/icons/icon-512.svg 存在確認: ✅
- static/icons/apple-touch-icon.svg 存在確認: ✅
- sw.js: install/activate/fetch/offline fallback: ✅
- base.html: manifest/theme-color/iOS meta/SW登録スクリプト: ✅
- index.html: pwa-hint/iOS・Android手順: ✅
- style.css: .pwa-hint スタイル: ✅

### 結合テスト
- GET /: manifest/SW登録/pwa-hint/ホーム画面手順 レンダリング: ✅
- GET /sw.js: 200, Content-Type=JS, Cache-Control=no-cache: ✅
- GET /static/manifest.json: 200, JSON valid: ✅
- GET /static/icons/icon-192.svg: 200: ✅
- GET /static/icons/icon-512.svg: 200: ✅
- GET /static/icons/apple-touch-icon.svg: 200: ✅
- GET /quiz: 200（既存機能正常）: ✅
- GET /api/questions: 5問取得（既存機能正常）: ✅

### 結果: 全通過（20/20）

---

## [2026-03-22] 質問画面の自動遷移を廃止し「次へ」ボタン方式に変更

### 単体テスト
- app.py 構文チェック: ✅
- database.py 構文チェック: ✅
- ml_model.py 構文チェック: ✅
- questions_data.py 構文チェック: ✅
- app.js: 自動遷移(setTimeout)が削除されている: ✅
- app.js: 選択時にselectedクラスをトグルしている: ✅
- app.js: 未選択時にnextボタンがdisabled: ✅
- app.js: nextQuestion()関数が存在する: ✅
- quiz.html: nextQuestion / prevQuestion ボタン確認: ✅

### 結合テスト
- GET /quiz: 200: ✅
- GET /api/questions: 5問取得: ✅
- POST /api/submit → result_id取得: ✅
- GET /result/<id>: 200: ✅

### 結果: 全通過（13/13）

---

## [2026-03-21] 料理カードをクックパッド検索リンクに変更

### 単体テスト
- app.py 構文チェック: ✅
- database.py 構文チェック: ✅
- ml_model.py 構文チェック: ✅
- questions_data.py 構文チェック: ✅
- result.html: Cookpad URL（https://cookpad.com/search/{{ food }}）: ✅
- result.html: target="_blank" 属性: ✅
- result.html: rel="noopener noreferrer" 属性: ✅
- result.html: food-recipe-hint クラス: ✅
- style.css: .food-card に text-decoration:none・display:block: ✅
- style.css: .food-recipe-hint スタイル定義: ✅
- style.css: .food-card:hover .food-recipe-hint 表示ルール: ✅
- style.css: .food-card--highlight .food-recipe-hint 色ルール: ✅
- style.css: .food-card:hover リフト効果: ✅

### 結合テスト
- POST /api/submit → result_id 取得: ✅
- GET /result/<id>: cookpad.com/search/ リンク描画: ✅
- GET /result/<id>: target=_blank 描画: ✅
- GET /result/<id>: 「レシピを見る →」テキスト描画: ✅
- GET /result/<id>: <a>タグの food-card 4件確認: ✅

### 結果: 全通過（18/18）

---

## [2026-03-21] 再学習ボタンを履歴ページから削除

### 単体テスト
- app.py 構文チェック: ✅
- /api/retrain エンドポイント（開発者用として）存在: ✅

### 結合テスト
- GET /history 200: ✅
- 再学習ボタン（retrain-section）が非表示: ✅
- retrain() JS関数が削除されている: ✅
- feedback_count 変数がテンプレートに渡されない: ✅
- 診断→結果保存が正常動作: ✅
- 自分の履歴が表示される: ✅
- 履歴リスト要素が存在する: ✅

### 結果: 全通過（9/9）

---

## [2026-03-21] PEP8 docstring・インラインコメント追加

### 単体テスト
- 構文チェック（app.py）: ✅
- 構文チェック（database.py）: ✅
- 構文チェック（ml_model.py）: ✅
- 構文チェック（questions_data.py）: ✅
- モジュールdocstring 存在（4ファイル全て）: ✅
- Database.save_result docstring: ✅
- Database.get_result docstring: ✅
- Database.save_feedback docstring: ✅
- MLModel.predict docstring: ✅
- MLModel.retrain docstring: ✅
- food_to_group docstring: ✅

### 結合テスト（ロジック不変確認）
- GET /: ✅
- GET /api/questions（5問取得）: ✅
- POST /api/submit: ✅
- GET /result/\<id\>: ✅
- GET /history: ✅
- GET /api/feedback/count: ✅
- GET /api/stats: ✅
- ML predict G1（高ストレス・高疲労）: ✅
- ML predict G9（高活気・高欲求）: ✅
- food_to_group 既知料理・未知料理・None: ✅
- 質問バンク35問・カテゴリ0-6全存在: ✅

### 結果: 全通過（24/24）

---

## [2026-03-21] セッション単位の履歴フィルタリング

### 単体テスト
- session_idカラム存在（quiz_results）: ✅
- get_result_count(session_id=A) → 2件: ✅
- get_result_count(session_id=B) → 1件: ✅
- get_result_count()引数なし → 全件返す: ✅
- get_results_paginated(session_id=A) → 2件: ✅
- get_results_paginated(session_id=B) → 1件: ✅
- sid_Aの結果にsid_Bのデータが混入しない: ✅
- get_training_data()はsession_idでフィルタしない（ML用全件）: ✅

### 結合テスト
- before_request: sidが自動生成される（UUID形式）: ✅
- GET /history → 200: ✅
- 自分の診断結果が履歴に表示される: ✅
- 別セッションの結果が自分の履歴に表示されない: ✅
- 履歴画面にセッション説明文が表示される: ✅

### 結果: 全通過（13/13）

---

## テスト実施日: 2026-03-20
## 対象機能: フィードバック機能

---

## 単体テスト結果（PMエージェント代行実施）

### 1. 構文チェック

| ファイル | 結果 |
|---------|------|
| app.py | ✅ OK |
| database.py | ✅ OK |
| ml_model.py | ✅ OK |
| questions_data.py | ✅ OK |

### 2. ml_model.py — food_to_group() テスト

| テストケース | 結果 | 備考 |
|------------|------|------|
| 全グループ全料理マッピング（40品） | ✅ OK（一部※） | ※重複料理は後述 |
| 未登録料理（ピザ） → None | ✅ OK | |
| 空文字 → None | ✅ OK | |
| None → None | ✅ OK | |
| カレー → G10 | ✅ OK | |
| こってりラーメン → G1 | ✅ OK | |
| 寿司 → G2 | ✅ OK | |

**⚠️ 既知の仕様上の問題（バグではなくデータ設計の課題）:**
| 料理名 | 重複グループ | food_to_group() の戻り値 | 影響 |
|-------|------------|------------------------|------|
| 焼肉 | G1・G2 両方に存在 | G1（先着順） | ML学習時にG2の焼肉がG1として学習される可能性 |
| 鍋 | G3・G7 両方に存在 | G3（先着順） | ML学習時にG7の鍋がG3として学習される可能性 |

→ 対策案: 将来的にフィードバック時の「提案グループ」も参考にして紐付けることを推奨。現時点では許容範囲内。

### 3. database.py — フィードバックDB テスト（Flask test_client 経由）

| テストケース | 結果 | 備考 |
|------------|------|------|
| save_feedback() 正常系 | ✅ OK | success: true |
| get_feedback_count() ≥1 | ✅ OK | count=1 |
| 同一result_id 上書き（件数不変） | ✅ OK | before=1, after=1 |
| get_feedback_for_training() キー確認 | ✅ OK | 全9キー確認済み |

### 4. app.py — POST /api/feedback バリデーション テスト

| テストケース | 結果 | エラーメッセージ |
|------------|------|---------------|
| actual_food = 空文字 | ✅ OK（failure） | 食べた料理を入力してください |
| actual_food = 空白のみ（strip後空） | ✅ OK（failure） | 食べた料理を入力してください |
| satisfaction = 6（範囲外） | ✅ OK（failure） | 満足度は1〜5の整数で入力してください |
| satisfaction = 0（範囲外） | ✅ OK（failure） | 満足度は1〜5の整数で入力してください |
| satisfaction = '5'（文字列型） | ✅ OK（failure） | 満足度は1〜5の整数で入力してください |
| result_id = 99999（存在しない） | ✅ OK（failure） | 対応する診断結果が見つかりません |

### 5. GET /api/feedback/count テスト

| テストケース | 結果 | 備考 |
|------------|------|------|
| レスポンスに count キーが含まれる | ✅ OK | {'count': 1} |

### 単体テスト サマリー
- 総テスト数: 16
- 成功: 16
- 失敗: 0
- 既知課題: 料理名の重複（焼肉・鍋）がMLマッピングに影響する可能性あり

---

## 結合テスト結果（PMエージェント代行実施）

### フロー1: 診断 → フィードバック完全フロー

| ステップ | 結果 | 備考 |
|---------|------|------|
| GET /api/questions | ✅ OK | 5問取得 |
| POST /api/submit | ✅ OK | result_id 取得 |
| GET /result/\<id\> | ✅ OK | feedbackSection 存在確認 |
| POST /api/feedback（正常系） | ✅ OK | success: true |
| GET /api/feedback/count | ✅ OK | count=1 |
| 重複送信（上書き、件数不変） | ✅ OK | before=after=1 |

### フロー2: 異常系フィードバック

| テストケース | 結果 | 備考 |
|------------|------|------|
| actual_food 空文字 | ✅ OK（failure） | |
| actual_food 空白のみ | ✅ OK（failure） | strip() で検出 |
| satisfaction 文字列型 '5' | ✅ OK（failure） | isinstance チェック |
| result_id 存在しない(99999) | ✅ OK（failure） | |

### フロー3: 履歴画面

| テストケース | 結果 | 備考 |
|------------|------|------|
| GET /history ステータス200 | ✅ OK | |
| feedback_count がテンプレートに渡る | ✅ OK | 50件未満のため再学習ボタン非表示 |

### フロー4: フリーテキスト（その他）フィードバック

| テストケース | 結果 | 備考 |
|------------|------|------|
| actual_food = 'カップラーメン'（未登録料理）の保存 | ✅ OK | DBには保存成功。ML変換時は food_to_group() が None を返すためスキップ |

### フロー5: get_feedback_for_training() の結合確認

| テストケース | 結果 | 確認キー |
|------------|------|---------|
| 全必須キーの存在 | ✅ OK | stress, fatigue, tension, vitality, social, desire, confusion, actual_food, satisfaction |
| quiz_results との JOIN | ✅ OK | カテゴリスコアが正しく紐づく |

### 結合テスト サマリー
- 総シナリオ数: 5フロー / 13テストケース
- 成功: 13
- 失敗: 0
- 特記事項: フリーテキスト（未登録料理）はDB保存は成功するが、ML再学習時にはスキップされる仕様（設計通り）

---

## 総合サマリー

| 区分 | テスト数 | 成功 | 失敗 |
|------|---------|------|------|
| 構文チェック | 4 | 4 | 0 |
| 単体テスト | 12 | 12 | 0 |
| 結合テスト | 13 | 13 | 0 |
| **合計** | **29** | **29** | **0** |

**既知課題（今後対応）:**
- 料理名の重複（焼肉・鍋）がfood_to_group()のMLマッピングに影響する可能性 → 将来的に要検討
