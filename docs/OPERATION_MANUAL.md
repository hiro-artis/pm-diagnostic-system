# PM協会テスト診断システム - 運用マニュアル

**バージョン：** 1.0  
**作成日：** 2026年6月6日  
**対象者：** システム管理者、テスト実施担当者

---

## 1. 環境セットアップ

### 1.1 必須環境

```
Python 3.9 以上
pip (Python パッケージマネージャ)
```

### 1.2 インストール手順

#### Step 1: リポジトリクローン

```bash
git clone https://github.com/pm-association/pm-diagnostic-system.git
cd pm-diagnostic-system
```

#### Step 2: 仮想環境構築

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

#### Step 3: 依存ライブラリインストール

```bash
pip install -r requirements.txt
```

#### Step 4: 環境設定

```bash
cp .env.example .env
```

`.env` ファイルを編集：

```
ANTHROPIC_API_KEY=your_api_key_here
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/pm_diagnostic.db
```

### 1.3 Claude API キー取得

1. https://console.anthropic.com にアクセス
2. API キーを生成
3. `.env` ファイルに設定

---

## 2. システム起動

### 2.1 CLI モード（単一ユーザー）

```bash
python -m src.cli
```

**フロー：**

```
Welcome to PM Diagnostic System
═══════════════════════════════

[Step 1] ユーザー情報入力
  ├─ User ID: user001
  ├─ Name: 山田太郎
  └─ Email: yamada@example.com

[Step 2] 1次テスト実施
  ├─ PM基礎知識（10問）
  ├─ オフィス移転（8問）
  └─ マインドセット（6シナリオ）
  → 結果: 合格

[Step 3] 2次テスト実施（条件合致時）
  ├─ マインドセット面接（4-6問）
  └─ 一貫性検証
  → 結果: 確認

[Step 4] 最終評価レポート表示
  ├─ 総合スコア: 73.5
  ├─ 評価: B
  └─ 推奨事項表示

[完了]
```

### 2.2 Web API サーバー起動（複数ユーザー）

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**確認：**

```
http://localhost:8000/docs
```

Swagger UI が表示されたら成功です。

---

## 3. テスト実施手順

### 3.1 単一ユーザーテスト

#### フロー

1. **初期入力**
   - User ID（例：`user001`）
   - Name（例：`山田太郎`）
   - Email（例：`yamada@example.com`）

2. **1次テスト実施**（約 60 分）
   - **PM基礎知識** - 10問（選択式）
     - 1問あたり 2-3 分
     - 正答数でスコア計算
   
   - **オフィス移転テスト** - 8問（選択式5 + 記述式3）
     - MC: 1問あたり 2 分
     - Essay: 1問あたり 10-15 分
   
   - **マインドセット** - 6シナリオ（選択式）
     - 1問あたり 3-5 分
     - 各マインドセット別スコア計算

3. **1次結果評価**
   - 基礎知識：70点以上で合格
   - オフィス移転：65点以上で合格
   - マインドセット：60点以上で2次進出

4. **2次テスト実施**（約 20 分 ※条件合致時のみ）
   - 弱点マインドセット集中質問（4-6問）
   - 開放型・深掘り型質問で実例を引き出す
   - 1次テストとの一貫性検証

5. **最終評価**
   - 総合スコア計算（重み付け）
   - 評価等級判定（A/B/C/再検査）
   - レポート生成・表示

### 3.2 複数ユーザー・バッチ処理

#### スクリプト実装例

```python
from src.agents.orchestrator import OrchestratorAgent
import asyncio

async def batch_test(user_list):
    orchestrator = OrchestratorAgent()
    
    for user in user_list:
        response = await orchestrator.execute({
            "action": "start_primary_test",
            "user_id": user['id'],
        })
        
        if response.status == "success":
            print(f"✓ {user['name']} - テスト開始")
        else:
            print(f"✗ {user['name']} - エラー: {response.error_message}")

# 実行
users = [
    {"id": "user001", "name": "山田太郎"},
    {"id": "user002", "name": "鈴木花子"},
]

asyncio.run(batch_test(users))
```

---

## 4. テスト問題管理

### 4.1 問題セット確認

```bash
python -c "from src.utils.test_data import QUESTIONS; print(f'Total: {len(QUESTIONS)} questions')"
```

### 4.2 問題セット追加

ファイル：`src/utils/test_data.py`

```python
NEW_QUESTION = {
    "id": "BK-011",  # 新規ID
    "section": "basic_knowledge",
    "question": "新しい質問内容...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "B",
    "explanation": "解説..."
}

QUESTIONS.append(NEW_QUESTION)
```

### 4.3 マインドセット評価パターンの調整

ファイル：`src/utils/scoring_logic.py`

```python
MINDSET_PATTERNS = {
    "MS-S01": {
        "A": {
            "future_focused": 3,
            "self_responsibility": 2,
            # ...
        },
        # ...
    }
}
```

---

## 5. データ管理

### 5.1 テスト結果保存先

```
data/
├── sessions/          # セッション情報
│   └── *.json
├── results/           # テスト結果
│   └── *.json
└── assessments/       # 最終評価
    └── *.json
```

### 5.2 結果エクスポート

```bash
# すべての結果をCSV出力
python -c "
from src.storage.result_store import ResultStore
store = ResultStore()
results = store.get_all_results()
# CSV出力処理
"
```

### 5.3 データベース初期化

```bash
# JSON ストレージをクリア
rm -rf data/sessions/* data/results/* data/assessments/*
```

---

## 6. トラブルシューティング

### 6.1 よくある問題と対応

| 問題 | 原因 | 対応 |
|------|------|------|
| `ANTHROPIC_API_KEY not found` | API キーが設定されていない | `.env` に API キー設定 |
| `Session not found` | セッションが期限切れ | 新規セッションから開始 |
| `Timeout error` | API 呼び出しが遅い | `TIMEOUT_SECONDS` を増やす |
| `JSON decode error` | ストレージファイルが破損 | データを削除して再スタート |

### 6.2 ログ確認

```bash
# ログレベル: INFO（デフォルト）
# ログ出力: コンソール

# より詳細なログを見たい場合
export LOG_LEVEL=DEBUG
python -m src.cli
```

### 6.3 デバッグモード

```python
# src/main.py で
logging.basicConfig(level=logging.DEBUG)

# 実行
python -m src.main
```

---

## 7. パフォーマンスチューニング

### 7.1 タイムアウト設定

`.env`：

```
PRIMARY_TEST_TIMEOUT_SECONDS=5400  # 90分
SECONDARY_TEST_TIMEOUT_SECONDS=1800  # 30分
API_CALL_TIMEOUT_SECONDS=30
```

### 7.2 同時セッション上限

`src/agents/orchestrator.py`：

```python
MAX_CONCURRENT_SESSIONS = 10  # 推奨値
```

### 7.3 採점エージェント並列化

```python
import asyncio

async def score_essays_parallel(essays):
    tasks = [score_essay(essay) for essay in essays]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 8. バックアップ・リカバリ

### 8.1 日次バックアップ

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

cp -r data/ $BACKUP_DIR/
cp -r src/ $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

実行：

```bash
chmod +x backup.sh
./backup.sh
```

### 8.2 復旧手順

```bash
# バックアップからリストア
cp -r backups/20260606/data/* data/

# 確認
ls -la data/
```

---

## 9. セキュリティ運用

### 9.1 API キー管理

- API キーを `.env` に保存（`.gitignore` に含める）
- 本運用では環境変数から読み込み
- キーの定期的なローテーション（推奨：90日ごと）

### 9.2 ユーザーデータ保護

- テスト結果は暗号化して保存（本運用環境）
- アクセスログを記録
- 個人情報は GDPR に準拠

### 9.3 監査ログ

```python
# すべてのテスト実施をログに記録
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"

# 例：
# [2026-06-06 10:00:00] [INFO] Session started: user001
# [2026-06-06 10:05:00] [INFO] Question answered: BK-001
# [2026-06-06 11:00:00] [INFO] Assessment completed: user001
```

---

## 10. 定期メンテナンス

### 10.1 週次チェック

- [ ] ログファイルサイズ確認
- [ ] エラー率監視
- [ ] API 応答時間確認
- [ ] 期限切れセッション削除

### 10.2 月次メンテナンス

- [ ] テスト問題の見直し
- [ ] マインドセット評価パターンの精度確認
- [ ] ユーザーフィードバック分析
- [ ] ドキュメント更新

### 10.3 四半期レビュー

- [ ] 採点精度分析
- [ ] システムパフォーマンス最適化
- [ ] セキュリティ監査
- [ ] 次版計画策定

---

## 11. テスト実施実績の管理

### 11.1 実績レポート

```bash
python -c "
from src.storage.result_store import ResultStore
from datetime import datetime, timedelta

store = ResultStore()

# 本月のテスト実績
today = datetime.utcnow()
start_of_month = today.replace(day=1)

results = store.get_results_by_date_range(start_of_month, today)

print(f'実施人数: {len(results)}')
print(f'合格者: {sum(1 for r in results if r[\"grade\"] in [\"A\", \"B\"])}')
print(f'再検査: {sum(1 for r in results if r[\"grade\"] == \"再検査\")}')
"
```

### 11.2 統計分析

```python
import json
from pathlib import Path

def analyze_results(results_dir):
    results = []
    
    for file in Path(results_dir).glob('*.json'):
        with open(file) as f:
            results.append(json.load(f))
    
    # 平均スコア計算
    avg_score = sum(r['total_score'] for r in results) / len(results)
    
    # 評価分布
    grades = {}
    for r in results:
        g = r['grade']
        grades[g] = grades.get(g, 0) + 1
    
    print(f"Average Score: {avg_score:.1f}")
    print(f"Grade Distribution: {grades}")
```

---

## 12. サポート

**問題発生時：**

1. ログを確認
2. このマニュアルのトラブルシューティング参照
3. GitHub Issues で報告

**連絡先：** support@pm-association.jp

---

**最終更新：** 2026年6月6日  
**次版予定：** 2026年7月（本運用フィードバック反映）
