"""FastAPI server for PM diagnostic system."""

import asyncio
import logging
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.primary_test_orchestrator import PrimaryTestOrchestratorAgent
from src.agents.secondary_test_orchestrator import SecondaryTestOrchestratorAgent
from src.agents.final_assessment import FinalAssessmentAgent


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="PM協会テスト診断システム API",
    description="PM適性診断エージェントAPI",
    version="1.0.0"
)

# Add CORS middleware for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "https://pm-diagnostic.vercel.app")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
primary_orchestrator = PrimaryTestOrchestratorAgent()
secondary_orchestrator = SecondaryTestOrchestratorAgent()
final_assessment = FinalAssessmentAgent()


# ===== Pydantic Models =====

class StartSessionRequest(BaseModel):
    user_id: str
    user_name: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    status: str


class PrimaryTestAnswers(BaseModel):
    session_id: str
    basic_knowledge: Dict[str, str]
    office_migration_mc: Dict[str, str]
    office_migration_essay: Dict[str, str]
    mindset: Dict[str, str]


class PrimaryTestResultResponse(BaseModel):
    session_id: str
    status: str
    scores: Dict[str, int]
    passed: bool
    qualifies_for_secondary: bool
    mindset_breakdown: Dict[str, int]


class SecondaryTestAnswers(BaseModel):
    session_id: str
    interview_responses: Dict[str, str]


class SecondaryTestResultResponse(BaseModel):
    session_id: str
    status: str
    interview_score: int
    revised_mindset_scores: Dict[str, int]


class FinalAssessmentResponse(BaseModel):
    session_id: str
    grade_level: str
    total_score: float
    summary: str
    strengths: list
    development_areas: list
    recommendations: list


# ===== Health Check =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "PM診断システム API",
        "version": "1.0.0"
    }


# ===== Session Management =====

@app.post("/api/sessions/start", response_model=SessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new test session."""
    try:
        session_id = f"{request.user_id}_{int(asyncio.get_event_loop().time() * 1000)}"

        logger.info(f"Starting session for user: {request.user_id}")

        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            status="initialized"
        )
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Primary Test =====

@app.post("/api/tests/primary/submit", response_model=PrimaryTestResultResponse)
async def submit_primary_test(request: PrimaryTestAnswers):
    """Submit primary test answers."""
    try:
        logger.info(f"Processing primary test for session: {request.session_id}")

        result = await primary_orchestrator.run_complete_primary_test(
            user_id=request.session_id,
            basic_answers=request.basic_knowledge,
            office_mc_answers=request.office_migration_mc,
            office_essay_answers=request.office_migration_essay,
            mindset_answers=request.mindset
        )

        if result.status == "success":
            return PrimaryTestResultResponse(
                session_id=request.session_id,
                status="completed",
                scores=result.result.get("scores", {}),
                passed=result.result.get("passed", False),
                qualifies_for_secondary=result.result.get("qualifies_for_secondary", False),
                mindset_breakdown=result.result.get("mindset_breakdown", {})
            )
        else:
            raise HTTPException(status_code=400, detail=result.error_message)

    except Exception as e:
        logger.error(f"Error processing primary test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Secondary Test =====

@app.post("/api/tests/secondary/submit", response_model=SecondaryTestResultResponse)
async def submit_secondary_test(request: SecondaryTestAnswers):
    """Submit secondary test (interview) answers."""
    try:
        logger.info(f"Processing secondary test for session: {request.session_id}")

        result = await secondary_orchestrator.run_complete_secondary_test(
            session_id=request.session_id,
            primary_mindset_scores={},
            interview_responses=request.interview_responses
        )

        if result.status == "success":
            return SecondaryTestResultResponse(
                session_id=request.session_id,
                status="completed",
                interview_score=result.result.get("interview_score", 0),
                revised_mindset_scores=result.result.get("revised_mindset_scores", {})
            )
        else:
            raise HTTPException(status_code=400, detail=result.error_message)

    except Exception as e:
        logger.error(f"Error processing secondary test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Final Assessment =====

@app.post("/api/assessment/final")
async def generate_final_assessment(
    session_id: str,
    primary_scores: Dict,
    secondary_scores: Optional[Dict] = None
):
    """Generate final assessment."""
    try:
        logger.info(f"Generating final assessment for session: {session_id}")

        result = await final_assessment.evaluate(
            session_id=session_id,
            primary_results=primary_scores,
            secondary_results=secondary_scores
        )

        if result.status == "success":
            assessment = result.result.get("assessment", {})
            return FinalAssessmentResponse(
                session_id=session_id,
                grade_level=assessment.get("grade_level", "N/A"),
                total_score=assessment.get("total_score", 0),
                summary=assessment.get("summary", ""),
                strengths=assessment.get("strengths", []),
                development_areas=assessment.get("development_areas", []),
                recommendations=assessment.get("recommendations", [])
            )
        else:
            raise HTTPException(status_code=400, detail=result.error_message)

    except Exception as e:
        logger.error(f"Error generating final assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Error Handlers =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "status": "error",
        "message": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
