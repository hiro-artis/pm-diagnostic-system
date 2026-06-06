# Phase 1: コア基盤構築 - 詳細分析

**プロジェクト：** PM協会テスト診断システム  
**フェーズ：** Phase 1（コア基盤構築）  
**期間：** 1-2週間  
**成功基準：** テスト進行エージェントが1次テスト開始指示を出力できる

---

## 1. Phase 1 概要

### 目標
最小限の稼働エージェント構築。全体のスケルトン・通信基盤・セッション管理を実装し、テスト進行エージェント（オーケストレーター）が起動・制御可能な状態にする。

### 成功基準（具体的仕様）

テスト進行エージェントが以下を実行できること：

```
入力: {"action": "start_primary_test", "userId": "user123", "sessionId": "session-xyz"}
      ↓
出力: {
  "status": "in_progress",
  "nextAction": "run_basic_knowledge_test",
  "sessionId": "session-xyz",
  "message": "1次テストを開始します。基礎知識テストから始めます。"
}
```

つまり、**実際にテストを実施するのではなく、テストの開始指示・進行管理ができるまで**が目標。

### Phase 1で実装する範囲

| 実装対象 | 詳細 | 実装範囲 |
|---------|------|---------|
| テスト進行エージェント | オーケストレーター | ✅ 実装（フルスケール） |
| エージェント通信基盤 | 基底クラス + スキーマ | ✅ 実装 |
| セッション・結果管理 | 永続化機構 | ✅ 実装 |
| 各テスト実行エージェント | 基礎知識・オフィス移転・マインドセット | ❌ Phase 2以降 |
| 採点エージェント | 詳細採点・面接 | ❌ Phase 2以降 |

---

## 2. 実装の4つのタスク

### タスク1: プロジェクト初期化

#### 1.1 リポジトリ構造作成

```
PM協会テスト診断/
├── CLAUDE.md                          # プロジェクト計画書
├── README.md                          # プロジェクト概要
├── .env.example                       # 環境変数テンプレート
├── .gitignore
├── requirements.txt                   # 依存ライブラリ
│
├── docs/
│   ├── agent-map.md
│   ├── agent-specifications.md
│   ├── test-questions.md
│   ├── SCOPE_PROGRESS.md
│   └── PHASE1_DETAILED_ANALYSIS.md    # このドキュメント
│
├── src/
│   ├── __init__.py
│   ├── main.py                        # エントリーポイント
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              # 基底エージェントクラス ★
│   │   ├── orchestrator.py            # テスト進行エージェント ★
│   │   ├── basic_knowledge_test.py    # (Phase 2)
│   │   ├── office_migration_test.py   # (Phase 2)
│   │   ├── mindset_test.py            # (Phase 3)
│   │   ├── mindset_interview.py       # (Phase 4)
│   │   └── comprehensive_scorer.py    # (Phase 2-3)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                 # Pydantic スキーマ定義 ★
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── session_manager.py         # セッション管理 ★
│   │   └── result_store.py            # 結果の永続化 ★
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                  # ロギング
│   │   ├── config.py                  # 設定管理
│   │   └── scoring_logic.py           # (Phase 3)
│   │
│   └── api/
│       ├── __init__.py
│       └── routes.py                  # (オプション: FastAPI)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # pytest fixture
│   ├── test_orchestrator.py           # オーケストレーター単体テスト
│   ├── test_session_manager.py        # セッション管理テスト
│   ├── fixtures/
│   │   ├── sample_responses.json
│   │   └── test_data.py
│   └── integration/
│       └── test_phase1_flow.py        # 統合テスト（Phase 1）
│
└── logs/                              # (実行時に作成)
    └── (テスト実行時のログファイル)
```

#### 1.2 requirements.txt

**必須ライブラリ**：

```text
# LLM API
anthropic>=0.28.0

# データバリデーション
pydantic>=2.0.0
pydantic-settings>=2.0.0

# API フレームワーク（オプション）
fastapi>=0.104.0
uvicorn>=0.24.0

# データベース・永続化
sqlalchemy>=2.0.0
python-dotenv>=1.0.0

# ロギング・ユーティリティ
python-json-logger>=2.0.0

# テスト
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# コード品質
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

#### 1.3 .env.example

```env
# Anthropic API
ANTHROPIC_API_KEY=your-api-key-here

# プロジェクト設定
PROJECT_NAME=PM協会テスト診断
ENVIRONMENT=development  # development / staging / production

# ストレージ設定
STORAGE_TYPE=json  # json / sqlite / postgresql
JSON_STORAGE_PATH=./data/sessions
SQLITE_DB_PATH=./data/pm_test.db

# ロギング
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# API（FastAPI使用時）
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# テスト設定
TEST_MODE=False
MOCK_RESPONSES=False
```

---

### タスク2: エージェント通信基盤

#### 2.1 基底エージェントクラス（base_agent.py）

**責務：**
- 全エージェント共通の基本機能
- Claude API呼び出し（抽象化）
- エージェント間の通信インターフェース定義
- エラーハンドリング

**実装スケルトン**：

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime
import uuid

class BaseAgent(ABC):
    """
    全エージェントの基底クラス
    
    子クラスが実装すべきメソッド:
    - execute(): エージェントのメイン処理
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        エージェントのメイン処理
        
        Args:
            input_data: エージェントへの入力
        
        Returns:
            エージェントの出力（標準フォーマット）
        """
        pass
    
    async def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Claude APIを呼び出す
        
        Args:
            system_prompt: システムプロンプト
            user_message: ユーザーメッセージ
            model: 使用モデル
            temperature: 創造性（0-1）
            max_tokens: 最大トークン数
        
        Returns:
            Claude からの応答テキスト
        """
        from anthropic import Anthropic
        import os
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Claude API call failed: {str(e)}")
            raise
    
    def create_output(
        self,
        status: str,
        data: Dict[str, Any],
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        標準フォーマットで出力を作成
        
        Args:
            status: 実行ステータス
            data: 出力データ
            error: エラーメッセージ（あればそれを含める）
        
        Returns:
            標準フォーマットの出力
        """
        output = {
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        if error:
            output["error"] = error
        return output
    
    def log_execution(self, action: str, details: Dict[str, Any]):
        """実行ログを記録"""
        self.logger.info(f"{action}: {details}")
```

#### 2.2 スキーマ定義（models/schemas.py）

**Pydantic を使ったデータモデル定義**：

```python
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# ============= エージェント通信用スキーマ =============

class MessageType(str, Enum):
    """エージェント間メッセージのタイプ"""
    EXECUTE = "execute"
    REQUEST_SCORE = "request_score"
    NOTIFY_RESULT = "notify_result"
    ERROR = "error"

class AgentMessage(BaseModel):
    """エージェント間通信のメッセージ形式"""
    messageId: UUID4 = Field(default_factory=uuid4)
    fromAgent: str
    toAgent: Optional[str] = None
    messageType: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any]
    priority: str = "normal"  # high / normal / low

# ============= テスト進行エージェント用スキーマ =============

class TestConfig(BaseModel):
    """テスト設定"""
    retakeAllowed: bool = True
    secondaryTestThreshold: int = 60  # マインドセット最低点
    primaryTestTimeout: int = 3600  # 秒

class OrchestratorInput(BaseModel):
    """オーケストレーター入力スキーマ"""
    action: str  # start_primary_test / check_results / start_secondary / finalize
    userId: str
    sessionId: Optional[UUID4] = None
    testConfig: Optional[TestConfig] = None

class OrchestratorOutput(BaseModel):
    """オーケストレーター出力スキーマ"""
    status: str  # in_progress / primary_complete / secondary_complete / finalized
    nextAction: Optional[str] = None
    sessionId: UUID4
    message: str
    qualifiesForSecondary: Optional[bool] = None
    sessionEndTime: Optional[datetime] = None

# ============= セッション管理用スキーマ =============

class SessionState(str, Enum):
    """セッションの状態"""
    INITIALIZED = "initialized"
    PRIMARY_TEST_IN_PROGRESS = "primary_test_in_progress"
    PRIMARY_TEST_COMPLETE = "primary_test_complete"
    SECONDARY_TEST_IN_PROGRESS = "secondary_test_in_progress"
    SECONDARY_TEST_COMPLETE = "secondary_test_complete"
    FINALIZED = "finalized"
    ABANDONED = "abandoned"

class Session(BaseModel):
    """テストセッション"""
    sessionId: UUID4
    userId: str
    startTime: datetime
    endTime: Optional[datetime] = None
    state: SessionState
    primaryTestStartTime: Optional[datetime] = None
    primaryTestEndTime: Optional[datetime] = None
    secondaryTestStartTime: Optional[datetime] = None
    secondaryTestEndTime: Optional[datetime] = None
    qualifiesForSecondary: Optional[bool] = None

# ============= テスト結果用スキーマ =============

class TestScore(BaseModel):
    """テストスコア（1セクション分）"""
    sectionName: str  # basic_knowledge / office_migration / mindset
    score: int  # 0-100
    totalQuestions: int
    correctAnswers: Optional[int] = None
    passed: bool

class PrimaryTestResults(BaseModel):
    """1次テスト全体の結果"""
    sessionId: UUID4
    userId: str
    testDate: datetime
    basicKnowledge: Optional[TestScore] = None
    officeMigration: Optional[TestScore] = None
    mindset: Optional[TestScore] = None
    allPassed: bool
    qualifiesForSecondary: bool

# ============= エラーハンドリング用 =============

class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    errorCode: str
    errorMessage: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

#### 2.3 メッセージング機構

**エージェント間通信の実装方針**：

```python
# src/agents/message_broker.py

from typing import Dict, Callable, Any, Coroutine
import asyncio
import uuid

class MessageBroker:
    """
    エージェント間のメッセージング仲介
    （非同期イベントベース）
    """
    
    def __init__(self):
        self.handlers: Dict[str, list] = {}
        self.message_queue = asyncio.Queue()
    
    def subscribe(
        self,
        agent_id: str,
        message_type: str,
        handler: Callable[[Dict[str, Any]], Coroutine]
    ):
        """
        エージェント登録
        
        Args:
            agent_id: エージェントID
            message_type: 購読するメッセージタイプ
            handler: コールバック関数
        """
        key = f"{agent_id}:{message_type}"
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)
    
    async def publish(
        self,
        from_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        メッセージを発行
        
        Args:
            from_agent: 送信元エージェントID
            message_type: メッセージタイプ
            payload: ペイロード
        
        Returns:
            メッセージID
        """
        message_id = str(uuid.uuid4())
        message = {
            "messageId": message_id,
            "fromAgent": from_agent,
            "messageType": message_type,
            "payload": payload
        }
        await self.message_queue.put(message)
        return message_id
    
    async def process_messages(self):
        """メッセージキューを処理（バックグラウンド）"""
        while True:
            message = await self.message_queue.get()
            # 対応するハンドラーを実行
            # 実装詳細は省略
```

---

### タスク3: テスト進行エージェント実装

#### 3.1 orchestrator.py - メイン実装

**責務：**
- 全テストの進行管理
- 各テストエージェントの起動・制御
- 結果の集約
- 2次テスト進出判定

**実装スケルトン**：

```python
# src/agents/orchestrator.py

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import uuid
from .base_agent import BaseAgent
from ..models.schemas import OrchestratorInput, OrchestratorOutput, Session
from ..storage.session_manager import SessionManager
from ..storage.result_store import ResultStore

class TestOrchestratorAgent(BaseAgent):
    """
    テスト進行エージェント（オーケストレーター）
    
    責務:
    - 1次テストの3つのセクション（基礎知識・オフィス移転・マインドセット）の進行統制
    - 2次テスト実施判定
    - 最終レポート生成
    """
    
    def __init__(self):
        super().__init__(
            agent_id="agent_test_orchestrator",
            agent_name="テスト進行エージェント"
        )
        self.session_manager = SessionManager()
        self.result_store = ResultStore()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        メイン実行ロジック
        
        入力スキーマ:
        {
            "action": "start_primary_test" | "check_results" | "start_secondary" | "finalize",
            "userId": "string",
            "sessionId": "uuid?",
            "testConfig": {...}
        }
        """
        try:
            # 入力バリデーション
            input_obj = OrchestratorInput(**input_data)
            self.log_execution("orchestrator_execute", {
                "action": input_obj.action,
                "userId": input_obj.userId
            })
            
            # アクション別処理
            if input_obj.action == "start_primary_test":
                return await self._start_primary_test(input_obj)
            elif input_obj.action == "check_results":
                return await self._check_primary_results(input_obj)
            elif input_obj.action == "start_secondary":
                return await self._start_secondary_test(input_obj)
            elif input_obj.action == "finalize":
                return await self._finalize(input_obj)
            else:
                raise ValueError(f"Unknown action: {input_obj.action}")
        
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {str(e)}")
            return self.create_output(
                status="error",
                data={},
                error=str(e)
            )
    
    async def _start_primary_test(
        self,
        input_obj: OrchestratorInput
    ) -> Dict[str, Any]:
        """
        1次テストを開始
        
        処理フロー:
        1. セッション作成（新規）または既存セッション取得
        2. テスト実行エージェントの起動指示準備
        3. 次のアクション（基礎知識テスト）を返す
        """
        # セッション作成
        session = await self.session_manager.create_session(
            user_id=input_obj.userId,
            test_config=input_obj.testConfig
        )
        
        # セッション状態を更新
        await self.session_manager.update_session_state(
            session_id=session.sessionId,
            state="PRIMARY_TEST_IN_PROGRESS"
        )
        
        # 次のアクション指示
        output = {
            "status": "in_progress",
            "nextAction": "run_basic_knowledge_test",
            "sessionId": str(session.sessionId),
            "message": "1次テストを開始します。まずは基礎知識テストから始めます。",
            "testSequence": [
                "基礎知識テスト（15分）",
                "オフィス移転テスト（45分）",
                "マインドセットテスト（30分）"
            ]
        }
        
        self.log_execution("start_primary_test", output)
        return self.create_output(status="in_progress", data=output)
    
    async def _check_primary_results(
        self,
        input_obj: OrchestratorInput
    ) -> Dict[str, Any]:
        """
        1次テスト結果をチェック
        
        処理フロー:
        1. 各テストセクションのスコア取得
        2. 合格判定
        3. 2次テスト進出判定（マインドセット60点以上）
        """
        if not input_obj.sessionId:
            raise ValueError("sessionId is required")
        
        # セッション取得
        session = await self.session_manager.get_session(input_obj.sessionId)
        if not session:
            raise ValueError(f"Session not found: {input_obj.sessionId}")
        
        # テスト結果を取得
        results = await self.result_store.get_primary_test_results(
            session_id=input_obj.sessionId
        )
        
        # 合格判定
        all_passed = (
            results.basicKnowledge.passed and
            results.officeMigration.passed and
            results.mindset.passed
        )
        
        # 2次テスト進出判定
        qualifies_for_secondary = (
            results.mindset.score >= 60 and all_passed
        )
        
        # セッション状態更新
        await self.session_manager.update_session_state(
            session_id=input_obj.sessionId,
            state="PRIMARY_TEST_COMPLETE"
        )
        
        output = {
            "status": "primary_complete",
            "sessionId": str(input_obj.sessionId),
            "results": {
                "basicKnowledge": {
                    "score": results.basicKnowledge.score,
                    "passed": results.basicKnowledge.passed
                },
                "officeMigration": {
                    "score": results.officeMigration.score,
                    "passed": results.officeMigration.passed
                },
                "mindset": {
                    "score": results.mindset.score,
                    "passed": results.mindset.passed
                }
            },
            "allPassed": all_passed,
            "qualifiesForSecondary": qualifies_for_secondary,
            "nextAction": "start_secondary" if qualifies_for_secondary else "finalize",
            "message": (
                "1次テスト結果：全セクション合格。2次テスト（面接）に進みます。"
                if qualifies_for_secondary
                else "1次テスト結果：合格。その他のセクションについては再検査が必要です。"
            )
        }
        
        self.log_execution("check_primary_results", output)
        return self.create_output(status="primary_complete", data=output)
    
    async def _start_secondary_test(
        self,
        input_obj: OrchestratorInput
    ) -> Dict[str, Any]:
        """2次テスト（面接）を開始"""
        if not input_obj.sessionId:
            raise ValueError("sessionId is required")
        
        await self.session_manager.update_session_state(
            session_id=input_obj.sessionId,
            state="SECONDARY_TEST_IN_PROGRESS"
        )
        
        output = {
            "status": "in_progress",
            "nextAction": "run_secondary_interview",
            "sessionId": str(input_obj.sessionId),
            "message": "2次テスト（面接）を開始します。AIとの対話を通じてマインドセットを深掘り検証します。"
        }
        
        self.log_execution("start_secondary_test", output)
        return self.create_output(status="in_progress", data=output)
    
    async def _finalize(self, input_obj: OrchestratorInput) -> Dict[str, Any]:
        """
        最終評価を生成
        
        処理フロー:
        1. 1次テスト結果（＋2次テスト結果）を統合
        2. 最終評価を算出（A/B/C/再検査）
        3. フィードバック・推奨事項を生成
        """
        if not input_obj.sessionId:
            raise ValueError("sessionId is required")
        
        # セッション・結果を取得
        session = await self.session_manager.get_session(input_obj.sessionId)
        results = await self.result_store.get_all_results(input_obj.sessionId)
        
        # 最終評価算出（簡易版）
        overall_score = self._calculate_overall_score(results)
        grade = self._determine_grade(overall_score, results)
        
        # セッション終了
        await self.session_manager.update_session_state(
            session_id=input_obj.sessionId,
            state="FINALIZED",
            end_time=datetime.now()
        )
        
        output = {
            "status": "finalized",
            "sessionId": str(input_obj.sessionId),
            "finalAssessment": {
                "totalScore": overall_score,
                "grade": grade,
                "summary": f"PM適性診断の最終評価: {grade}",
                "message": "テストが完了しました。ご協力ありがとうございます。"
            }
        }
        
        self.log_execution("finalize", output)
        return self.create_output(status="finalized", data=output)
    
    def _calculate_overall_score(self, results) -> int:
        """総合スコアを計算"""
        # 簡易版: 3セクションの平均
        if not all([results.basicKnowledge, results.officeMigration, results.mindset]):
            return 0
        return (
            results.basicKnowledge.score +
            results.officeMigration.score +
            results.mindset.score
        ) // 3
    
    def _determine_grade(self, overall_score: int, results) -> str:
        """最終評価を判定"""
        # Phase 1では簡易判定
        if overall_score >= 80:
            return "A"
        elif overall_score >= 70:
            return "B"
        elif overall_score >= 60:
            return "C"
        else:
            return "再検査"
```

#### 3.2 オーケストレーターの状態遷移図

```
[初期状態]
    ↓
[START_PRIMARY_TEST]
    ├→ セッション作成
    ├→ 状態: PRIMARY_TEST_IN_PROGRESS
    └→ 次: 基礎知識テスト
    ↓
[各テスト実行]
    ├→ 基礎知識テスト結果受け取り
    ├→ オフィス移転テスト結果受け取り
    └→ マインドセット結果受け取り
    ↓
[CHECK_PRIMARY_RESULTS]
    ├→ 合格判定
    ├→ 2次進出判定
    └→ 状態: PRIMARY_TEST_COMPLETE
    ↓
[2次テスト判定]
    ├→ 進出条件を満たす → START_SECONDARY_TEST
    └→ 満たさない → FINALIZE
    ↓
[FINALIZE]
    ├→ 最終評価算出
    ├→ 状態: FINALIZED
    └→ [終了]
```

---

### タスク4: セッション・結果管理

#### 4.1 session_manager.py

**責務：**
- セッションのライフサイクル管理
- セッション状態の永続化
- セッション情報の取得・更新

**実装スケルトン**：

```python
# src/storage/session_manager.py

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from ..models.schemas import Session, SessionState, TestConfig
import json
import os

class SessionManager:
    """セッション管理"""
    
    def __init__(self, storage_path: str = "./data/sessions"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def create_session(
        self,
        user_id: str,
        test_config: Optional[TestConfig] = None
    ) -> Session:
        """
        新しいセッションを作成
        
        Args:
            user_id: ユーザーID
            test_config: テスト設定
        
        Returns:
            作成されたセッション
        """
        session_id = uuid.uuid4()
        session = Session(
            sessionId=session_id,
            userId=user_id,
            startTime=datetime.now(),
            state=SessionState.INITIALIZED
        )
        
        # ディスクに保存
        await self._save_session(session)
        return session
    
    async def get_session(self, session_id: uuid.UUID) -> Optional[Session]:
        """
        セッション情報を取得
        
        Args:
            session_id: セッションID
        
        Returns:
            セッション情報（見つからない場合はNone）
        """
        file_path = os.path.join(self.storage_path, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Session(**data)
    
    async def update_session_state(
        self,
        session_id: uuid.UUID,
        state: str,
        end_time: Optional[datetime] = None
    ):
        """
        セッション状態を更新
        
        Args:
            session_id: セッションID
            state: 新しい状態
            end_time: セッション終了時刻（終了時のみ）
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.state = state
        if end_time:
            session.endTime = end_time
        
        await self._save_session(session)
    
    async def _save_session(self, session: Session):
        """セッション情報をディスクに保存"""
        file_path = os.path.join(self.storage_path, f"{session.sessionId}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.dict(default=str), f, indent=2, ensure_ascii=False)
    
    async def list_sessions(self, user_id: str) -> list:
        """ユーザーの全セッションを取得"""
        sessions = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                with open(os.path.join(self.storage_path, filename), 'r') as f:
                    data = json.load(f)
                    session = Session(**data)
                    if session.userId == user_id:
                        sessions.append(session)
        return sessions
```

#### 4.2 result_store.py

**責務：**
- テスト結果の永続化
- 結果の取得・検索
- 結果の統合管理

**実装スケルトン**：

```python
# src/storage/result_store.py

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json
import os

class ResultStore:
    """テスト結果の永続化管理"""
    
    def __init__(self, storage_path: str = "./data/results"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def save_primary_test_result(
        self,
        session_id: uuid.UUID,
        section_name: str,
        result_data: Dict[str, Any]
    ):
        """
        1次テスト結果を保存
        
        Args:
            session_id: セッションID
            section_name: セクション名（basic_knowledge / office_migration / mindset）
            result_data: 結果データ
        """
        result_dir = os.path.join(self.storage_path, str(session_id))
        os.makedirs(result_dir, exist_ok=True)
        
        file_path = os.path.join(result_dir, f"{section_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "section": section_name,
                "savedAt": datetime.now().isoformat(),
                **result_data
            }, f, indent=2, ensure_ascii=False)
    
    async def get_primary_test_result(
        self,
        session_id: uuid.UUID,
        section_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        1次テスト結果を取得
        
        Args:
            session_id: セッションID
            section_name: セクション名
        
        Returns:
            結果データ（見つからない場合はNone）
        """
        file_path = os.path.join(
            self.storage_path,
            str(session_id),
            f"{section_name}.json"
        )
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def get_all_results(
        self,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        セッションの全結果を取得
        
        Returns:
            {
                "basicKnowledge": {...},
                "officeMigration": {...},
                "mindset": {...},
                "secondaryTest": {...} (実施時のみ)
            }
        """
        result_dir = os.path.join(self.storage_path, str(session_id))
        if not os.path.exists(result_dir):
            return {}
        
        results = {}
        for filename in os.listdir(result_dir):
            if filename.endswith('.json'):
                section_name = filename.replace('.json', '')
                file_path = os.path.join(result_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    results[section_name] = json.load(f)
        
        return results
```

---

## 3. 依存関係・インターフェース定義

### 3.1 エージェント間の依存関係図

```
┌─────────────────────────────────────────────────────┐
│ テスト進行エージェント（Orchestrator）            │
│  ├→ SessionManager の利用                          │
│  ├→ ResultStore の利用                             │
│  └→ テスト実行エージェント群の起動指示              │
└────────┬────────────────────────────────────────────┘
         ↓
     ┌───────────────────────────────────────┐
     │ テスト実行エージェント群（Phase 2以降） │
     ├─ 基礎知識テスト実行エージェント        │
     ├─ オフィス移転テスト実行エージェント    │
     └─ マインドセットテスト実行エージェント  │
         ↓ (採点が必要な場合)
     ┌───────────────────────────────────────┐
     │ 採点エージェント（詳細採点）          │
     │  ├→ 記述式採点                         │
     │  └→ 複雑な判定                         │
     └───────────────────────────────────────┘
```

### 3.2 APIs（入出力インターフェース）

#### Orchestrator API

```
[入力]
POST /api/orchestrator/execute
{
  "action": "start_primary_test" | "check_results" | "start_secondary" | "finalize",
  "userId": "user123",
  "sessionId": "uuid?" (check_results以降は必須),
  "testConfig": {
    "retakeAllowed": true,
    "secondaryTestThreshold": 60,
    "primaryTestTimeout": 3600
  }
}

[出力]
{
  "agentId": "agent_test_orchestrator",
  "status": "in_progress" | "primary_complete" | "secondary_complete" | "finalized",
  "data": {
    "status": "...",
    "nextAction": "run_basic_knowledge_test" | "...",
    "sessionId": "uuid",
    "message": "...",
    // アクションに応じた追加データ
  },
  "timestamp": "ISO8601"
}
```

#### SessionManager API

```
[セッション作成]
create_session(user_id: str, test_config: TestConfig?) -> Session

[セッション取得]
get_session(session_id: uuid.UUID) -> Optional[Session]

[セッション状態更新]
update_session_state(session_id: uuid.UUID, state: str, end_time?: datetime)

[ユーザーのセッション一覧]
list_sessions(user_id: str) -> List[Session]
```

#### ResultStore API

```
[結果保存]
save_primary_test_result(
    session_id: uuid.UUID,
    section_name: str,
    result_data: Dict[str, Any]
)

[結果取得]
get_primary_test_result(session_id: uuid.UUID, section_name: str) -> Optional[Dict]

[全結果取得]
get_all_results(session_id: uuid.UUID) -> Dict[str, Any]
```

---

## 4. 成功基準の具体的仕様

### 4.1 機能的成功基準

**テスト進行エージェントが以下を実行できること：**

| # | 機能 | 詳細仕様 | 検証方法 |
|---|------|---------|---------|
| 1 | セッション作成 | ユーザーIDと設定から新規セッション作成 | `pytest test_orchestrator.py::test_create_session` |
| 2 | テスト開始指示 | `start_primary_test` アクション時に次アクションを返す | `test_start_primary_test` |
| 3 | 状態遷移 | セッション状態が正しく遷移する | `test_session_state_transitions` |
| 4 | 結果統合 | 複数セクションの結果を集約できる | `test_aggregate_results` |
| 5 | 2次進出判定 | マインドセット60点以上で進出判定 | `test_secondary_qualification` |

### 4.2 非機能的成功基準

| # | 基準 | 目標 |
|---|------|------|
| 1 | レスポンスタイム | API呼び出しが1秒以内に返る |
| 2 | エラーハンドリング | 入力エラーに対して適切なエラーメッセージを返す |
| 3 | ロギング | すべての主要操作がログに記録される |
| 4 | 永続化 | セッション・結果がディスクに保存される |
| 5 | テストカバレッジ | 80%以上のコードカバレッジ |

---

## 5. API呼び出し戦略（Anthropic SDK）

### 5.1 Phase 1での API 利用方針

**Phase 1 では Claude API の呼び出しを最小限にする**

```
[Phase 1 (コア基盤)]
├─ テスト進行エージェント
│   └─ Claude API呼び出し: ❌ なし
│      （テスト問題配信や採点は Phase 2以降）
│
├─ セッション管理
│   └─ Claude API呼び出し: ❌ なし
│      （純粋なデータ管理）
│
└─ エージェント通信基盤
    └─ Claude API呼び出し: ⚠️ テスト用のみ
       （base_agent の call_claude() メソッドは実装するが、
        実際の呼び出しは Phase 2以降）
```

### 5.2 Anthropic SDK の初期化

```python
# src/utils/config.py

from anthropic import Anthropic
import os

def get_anthropic_client() -> Anthropic:
    """
    Anthropic クライアントを初期化
    
    環境変数 ANTHROPIC_API_KEY が設定されていることを前提
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    return Anthropic(api_key=api_key)

# 使用例
# client = get_anthropic_client()
# response = client.messages.create(
#     model="claude-3-5-sonnet-20241022",
#     max_tokens=2048,
#     messages=[
#         {"role": "user", "content": "..."}
#     ]
# )
```

### 5.3 Phase 2以降での API 活用計画

| フェーズ | 用途 | API呼び出し回数 | 対策 |
|---------|------|---|---|
| Phase 2 | 記述式採点 | 3回/テスト | Prompt Caching |
| Phase 3 | マインドセット採点分析 | 6回/テスト | ハードコード評価パターン |
| Phase 4 | 面接質問生成・分析 | 5-8回/セッション | キャッシング + 最小化設計 |

---

## 6. Phase 1 の実装チェックリスト

### セットアップ段階

- [ ] リポジトリ構造作成
- [ ] requirements.txt 作成
- [ ] .env.example 作成
- [ ] README.md 作成

### コア基盤実装

- [ ] `src/agents/base_agent.py` 実装
- [ ] `src/models/schemas.py` 実装
- [ ] `src/agents/message_broker.py` 実装（オプション）
- [ ] `src/utils/config.py` 実装
- [ ] `src/utils/logger.py` 実装

### オーケストレーター実装

- [ ] `src/agents/orchestrator.py` 実装
- [ ] `_start_primary_test()` メソッド実装
- [ ] `_check_primary_results()` メソッド実装
- [ ] `_start_secondary_test()` メソッド実装
- [ ] `_finalize()` メソッド実装

### ストレージ実装

- [ ] `src/storage/session_manager.py` 実装
- [ ] `src/storage/result_store.py` 実装
- [ ] `src/storage/__init__.py` 作成

### テスト実装

- [ ] `tests/conftest.py` 作成（フィクスチャ定義）
- [ ] `tests/test_orchestrator.py` 実装
- [ ] `tests/test_session_manager.py` 実装
- [ ] `tests/integration/test_phase1_flow.py` 実装

### ドキュメント・デプロイ

- [ ] 実装完了ドキュメント作成
- [ ] Dockerfile 作成（オプション）
- [ ] CI/CD 設定（GitHub Actions 等）

---

## 7. トラブルシューティング・リスク対策

### 7.1 よくあるエラーと対策

| エラー | 原因 | 対策 |
|-------|------|------|
| `ANTHROPIC_API_KEY not found` | 環境変数未設定 | `.env` ファイルを確認 |
| `Session not found` | セッションIDの不正 | セッションマネージャーのログを確認 |
| `JSON decode error` | 結果ファイルの破損 | バックアップから復元 |
| `Circular imports` | モジュール間の循環依存 | import 順序を見直す |

### 7.2 パフォーマンス最適化

**Phase 1 段階での最適化項目：**

- セッション情報をメモリキャッシュ（頻繁にアクセス）
- JSON ファイルを SQLite に移行（運用段階）
- ロギングレベルを環境に応じて調整

---

## 8. 次のステップ（Phase 2 への移行）

### Phase 1 完了時の成果物

1. **実装物**
   - テスト進行エージェント（フル稼働）
   - エージェント通信基盤
   - セッション・結果管理システム

2. **テスト**
   - 単体テスト（Orchestrator）
   - 統合テスト（Phase 1 フロー）
   - 80%以上のコードカバレッジ

3. **ドキュメント**
   - API 仕様書
   - 実装ガイド
   - トラブルシューティングガイド

### Phase 2 で実装すべき内容

1. **基礎知識テスト実行エージェント** → 10問のランダム配信 + 自動採点
2. **オフィス移転テスト実行エージェント** → 選択式5問 + 記述式3問
3. **詳細採点エージェント（簡易版）** → 記述式採点ロジック

### 時間配分の目安（1-2週間）

| 項目 | 所要時間 |
|------|---------|
| セットアップ・構造作成 | 0.5日 |
| 基盤実装（base_agent等） | 1日 |
| Orchestrator 実装 | 2日 |
| ストレージ実装 | 1日 |
| テスト実装 | 1.5日 |
| ドキュメント | 1日 |
| 調整・最適化 | 1日 |
| **合計** | **約 8-9日** |

---

## 付録：コード実装例（最小限）

### A. main.py（エントリーポイント）

```python
# src/main.py

import asyncio
from agents.orchestrator import TestOrchestratorAgent
from models.schemas import OrchestratorInput

async def main():
    """メイン実行"""
    orchestrator = TestOrchestratorAgent()
    
    # 1次テスト開始
    input_data = {
        "action": "start_primary_test",
        "userId": "user123",
        "testConfig": {
            "retakeAllowed": True,
            "secondaryTestThreshold": 60,
            "primaryTestTimeout": 3600
        }
    }
    
    result = await orchestrator.execute(input_data)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### B. conftest.py（テスト用フィクスチャ）

```python
# tests/conftest.py

import pytest
from pathlib import Path
import tempfile
import uuid
from src.storage.session_manager import SessionManager
from src.storage.result_store import ResultStore

@pytest.fixture
def temp_storage():
    """テンポラリストレージ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def session_manager(temp_storage):
    """セッションマネージャー"""
    return SessionManager(storage_path=f"{temp_storage}/sessions")

@pytest.fixture
def result_store(temp_storage):
    """結果ストア"""
    return ResultStore(storage_path=f"{temp_storage}/results")

@pytest.fixture
def sample_user_id():
    """サンプルユーザーID"""
    return "test_user_001"

@pytest.fixture
def sample_session_id():
    """サンプルセッションID"""
    return uuid.uuid4()
```

---

**作成日:** 2026年6月6日  
**対象者:** PM協会テスト診断システム開発チーム  
**ドキュメント版:** 1.0
