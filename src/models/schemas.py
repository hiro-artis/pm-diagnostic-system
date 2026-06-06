"""Pydantic schemas for PM diagnostic system."""

from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class TestStatus(str, Enum):
    """Test status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    TIMED_OUT = "timed_out"


class AgentType(str, Enum):
    """Agent type enumeration."""
    ORCHESTRATOR = "orchestrator"
    BASIC_KNOWLEDGE = "basic_knowledge_test"
    OFFICE_MIGRATION = "office_migration_test"
    MINDSET = "mindset_test"
    MINDSET_INTERVIEW = "mindset_interview"
    COMPREHENSIVE_SCORER = "comprehensive_scorer"


class TestPhase(str, Enum):
    """Test phase enumeration."""
    PRIMARY = "primary_test"
    SECONDARY = "secondary_test"
    COMPLETED = "completed"


class Mindset(str, Enum):
    """Six mindsets enumeration."""
    FUTURE_FOCUSED = "futureFocused"
    SELF_RESPONSIBILITY = "selfResponsibility"
    KINDNESS = "kindness"
    LISTENING_SKILL = "listeningSkill"
    INCLUSIVITY = "inclusivity"
    COLLABORATION = "collaboration"


# ============================================================================
# Session and Core Models
# ============================================================================

class SessionInfo(BaseModel):
    """Session information."""
    session_id: str = Field(..., description="Unique session ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    current_phase: TestPhase = Field(default=TestPhase.PRIMARY)
    current_test_agent: Optional[AgentType] = None
    status: TestStatus = Field(default=TestStatus.NOT_STARTED)
    timeout_seconds: int = 3600


class TestResult(BaseModel):
    """Base test result model."""
    test_id: str
    session_id: str
    test_agent: AgentType
    score: int
    total_points: int
    passed: bool
    start_time: datetime
    end_time: datetime
    time_spent_seconds: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Basic Knowledge Test Models
# ============================================================================

class BasicKnowledgeQuestion(BaseModel):
    """Basic knowledge test question."""
    question_id: str = Field(..., description="e.g., BK-001")
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)  # A, B, C, D
    correct_answer: str
    explanation: str


class BasicKnowledgeAnswer(BaseModel):
    """User answer for basic knowledge question."""
    question_id: str
    user_answer: str
    is_correct: bool
    score: int  # 0 or 10


class BasicKnowledgeTestResult(TestResult):
    """Complete basic knowledge test result."""
    questions: List[BasicKnowledgeAnswer]
    total_questions: int
    correct_answers: int
    score: int = Field(..., ge=0, le=100)  # 0-100


# ============================================================================
# Office Migration Test Models
# ============================================================================

class OfficeMigrationMCQuestion(BaseModel):
    """Multiple choice question for office migration test."""
    question_id: str = Field(..., description="e.g., OM-MC-001")
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str
    score_per_question: int = 5


class OfficeMigrationEssayQuestion(BaseModel):
    """Essay question for office migration test."""
    question_id: str = Field(..., description="e.g., OM-ES-001")
    question: str
    word_count_min: int = 200
    word_count_max: int = 300
    evaluation_criteria: Dict[str, Dict[str, Any]]  # Criteria with max scores


class OfficeMigrationAnswer(BaseModel):
    """User answer for office migration question."""
    question_id: str
    answer_text: str
    user_answer: Optional[str] = None  # For MC
    score: int
    scoring_rationale: Optional[str] = None


class OfficeMigrationTestResult(TestResult):
    """Complete office migration test result."""
    mc_score: int = Field(..., ge=0, le=25)
    essay_score: int = Field(..., ge=0, le=75)
    score: int = Field(..., ge=0, le=100)  # Total
    questions: List[OfficeMigrationAnswer]


# ============================================================================
# Mindset Test Models
# ============================================================================

class MindsetScenario(BaseModel):
    """Mindset scenario with options."""
    scenario_id: str = Field(..., description="e.g., MS-S01")
    scenario: str
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str
    score_per_question: int = 15
    evaluated_mindsets: List[Mindset]  # Mindsets evaluated by this scenario


class MindsetAnswer(BaseModel):
    """User answer for mindset scenario."""
    scenario_id: str
    user_answer: str
    score: int
    scoring_rationale: str
    mindset_scores: Dict[Mindset, int]  # Score breakdown by mindset


class MindsetScores(BaseModel):
    """Aggregated mindset scores."""
    future_focused: int = Field(..., ge=0, le=100)
    self_responsibility: int = Field(..., ge=0, le=100)
    kindness: int = Field(..., ge=0, le=100)
    listening_skill: int = Field(..., ge=0, le=100)
    inclusivity: int = Field(..., ge=0, le=100)
    collaboration: int = Field(..., ge=0, le=100)
    total_score: int = Field(..., ge=0, le=100)


class MindsetTestResult(TestResult):
    """Complete mindset test result."""
    scenarios: List[MindsetAnswer]
    mindset_scores: MindsetScores
    score: int = Field(..., ge=0, le=100)  # Total mindset score
    passes_secondary_test: bool = Field(default=False)  # >= 60 points


# ============================================================================
# Secondary Test (Interview) Models
# ============================================================================

class InterviewQuestion(BaseModel):
    """Interview question during secondary test."""
    question_number: int
    question_text: str
    question_type: str = Field(..., description="open | deep_dive | verification")
    evaluated_mindsets: List[Mindset]


class InterviewResponse(BaseModel):
    """Interview response."""
    question_number: int
    response_text: str
    evaluated_mindsets: Dict[Mindset, int]  # Mindset scores from this response
    consistency_with_primary: str = Field(..., description="consistent | improved | declined | unclear")
    notes: Optional[str] = None


class MindsetInterviewResult(TestResult):
    """Complete mindset interview (secondary test) result."""
    interview_questions: List[InterviewQuestion]
    responses: List[InterviewResponse]
    revised_mindset_scores: MindsetScores
    score: int = Field(..., ge=0, le=100)
    consistency_rating: str = Field(..., description="high | moderate | low")


# ============================================================================
# Comprehensive Assessment Models
# ============================================================================

class PrimaryTestResults(BaseModel):
    """Aggregated results from all primary tests."""
    basic_knowledge_result: BasicKnowledgeTestResult
    office_migration_result: OfficeMigrationTestResult
    mindset_result: MindsetTestResult

    def all_passed(self) -> bool:
        """Check if all primary tests passed."""
        return (
            self.basic_knowledge_result.passed and
            self.office_migration_result.passed and
            self.mindset_result.passed
        )


class FinalAssessment(BaseModel):
    """Final assessment and recommendation."""
    session_id: str
    user_id: str
    test_date: datetime

    # Scores
    basic_knowledge_score: int = Field(..., ge=0, le=100)
    office_migration_score: int = Field(..., ge=0, le=100)
    mindset_score: int = Field(..., ge=0, le=100)
    interview_score: Optional[int] = Field(None, ge=0, le=100)
    total_score: float

    # Mindset breakdown
    mindset_breakdown: MindsetScores

    # Assessment
    grade_level: str = Field(..., description="A | B | C | 再検査")
    summary: str
    strengths: List[str]
    development_areas: List[str]
    recommendations: List[str]

    # Metadata
    primary_test_completed: bool
    secondary_test_completed: bool
    secondary_test_conducted: bool


# ============================================================================
# Agent Communication Models
# ============================================================================

class AgentMessage(BaseModel):
    """Message between agents."""
    message_id: str
    from_agent: AgentType
    to_agent: Optional[AgentType] = None
    message_type: str = Field(..., description="execute | request_score | notify_result | error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]
    priority: str = Field(default="normal", description="high | normal | low")


class AgentResponse(BaseModel):
    """Response from an agent."""
    agent_type: AgentType
    status: str = Field(..., description="success | error")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Request/Response Models for API
# ============================================================================

class StartTestRequest(BaseModel):
    """Request to start a test."""
    user_id: str
    retake_allowed: bool = True
    test_config: Dict[str, Any] = Field(default_factory=dict)


class TestResponseRequest(BaseModel):
    """User response to a test question."""
    session_id: str
    question_id: str
    answer: str


class TestStatusResponse(BaseModel):
    """Current test status."""
    session_id: str
    status: TestStatus
    current_phase: TestPhase
    current_test_agent: Optional[AgentType]
    progress: Dict[str, Any]


class TestResultResponse(BaseModel):
    """Test result response."""
    session_id: str
    final_assessment: FinalAssessment
    next_steps: Optional[str] = None
