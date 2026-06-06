"""Test result storage and retrieval."""

import json
from pathlib import Path
from typing import Optional
import logging

from src.models.schemas import (
    TestResult,
    BasicKnowledgeTestResult,
    OfficeMigrationTestResult,
    MindsetTestResult,
    MindsetInterviewResult,
    FinalAssessment,
)


logger = logging.getLogger(__name__)


class ResultStore:
    """Stores and retrieves test results."""

    def __init__(self, storage_path: str = "data/results"):
        """Initialize result store.

        Args:
            storage_path: Path to store result data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_test_result(
        self,
        session_id: str,
        result,
    ) -> bool:
        """Save a test result.

        Args:
            session_id: Session identifier
            result: Test result to save (dict or TestResult object)

        Returns:
            True if successful, False otherwise
        """
        try:
            session_dir = self.storage_path / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Handle both dict and TestResult object
            if isinstance(result, dict):
                data = result
                test_type = result.get("test_type", "TestResult")
                test_id = result.get("test_id", "default")
            else:
                data = result.model_dump(mode="json")
                test_type = result.__class__.__name__
                test_id = result.test_id

            result_file = session_dir / f"{test_type}_{test_id}.json"

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved {test_type} result for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving test result: {str(e)}")
            return False

    def get_test_result(
        self,
        session_id: str,
        test_id: str,
    ) -> Optional[TestResult]:
        """Get a test result by ID.

        Args:
            session_id: Session identifier
            test_id: Test identifier

        Returns:
            TestResult if found, None otherwise
        """
        try:
            session_dir = self.storage_path / session_id
            if not session_dir.exists():
                logger.warning(f"Session directory not found: {session_id}")
                return None

            # Search for the test file
            for result_file in session_dir.glob(f"*{test_id}*.json"):
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Determine result type from filename or data
                return self._deserialize_test_result(data)

            logger.warning(f"Test result not found: {test_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving test result: {str(e)}")
            return None

    def get_all_session_results(self, session_id: str) -> dict:
        """Get all test results for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with all results organized by type
        """
        results = {
            "basic_knowledge": None,
            "office_migration": None,
            "mindset": None,
            "mindset_interview": None,
        }

        try:
            session_dir = self.storage_path / session_id
            if not session_dir.exists():
                return results

            for result_file in session_dir.glob("*.json"):
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                result = self._deserialize_test_result(data)
                if result:
                    # Map to result type
                    if isinstance(result, BasicKnowledgeTestResult):
                        results["basic_knowledge"] = result
                    elif isinstance(result, OfficeMigrationTestResult):
                        results["office_migration"] = result
                    elif isinstance(result, MindsetTestResult):
                        results["mindset"] = result
                    elif isinstance(result, MindsetInterviewResult):
                        results["mindset_interview"] = result

        except Exception as e:
            logger.error(f"Error retrieving session results: {str(e)}")

        return results

    def save_final_assessment(
        self,
        session_id: str,
        assessment: FinalAssessment,
    ) -> bool:
        """Save final assessment.

        Args:
            session_id: Session identifier
            assessment: Final assessment to save

        Returns:
            True if successful, False otherwise
        """
        try:
            session_dir = self.storage_path / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            assessment_file = session_dir / "final_assessment.json"
            data = assessment.model_dump(mode="json")
            with open(assessment_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved final assessment for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving final assessment: {str(e)}")
            return False

    def get_final_assessment(
        self,
        session_id: str,
    ) -> Optional[FinalAssessment]:
        """Get final assessment for a session.

        Args:
            session_id: Session identifier

        Returns:
            FinalAssessment if found, None otherwise
        """
        try:
            session_dir = self.storage_path / session_id
            assessment_file = session_dir / "final_assessment.json"

            if not assessment_file.exists():
                logger.warning(f"Final assessment not found for session {session_id}")
                return None

            with open(assessment_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return FinalAssessment(**data)
        except Exception as e:
            logger.error(f"Error retrieving final assessment: {str(e)}")
            return None

    def _deserialize_test_result(self, data: dict) -> Optional[TestResult]:
        """Deserialize test result from JSON data.

        Args:
            data: Deserialized JSON data

        Returns:
            Appropriate TestResult subclass, or None if type unknown
        """
        try:
            # Determine type from data or filename hint
            test_agent = data.get("test_agent")

            if test_agent == "basic_knowledge_test":
                return BasicKnowledgeTestResult(**data)
            elif test_agent == "office_migration_test":
                return OfficeMigrationTestResult(**data)
            elif test_agent == "mindset_test":
                return MindsetTestResult(**data)
            elif test_agent == "mindset_interview":
                return MindsetInterviewResult(**data)
            else:
                logger.warning(f"Unknown test agent type: {test_agent}")
                return None
        except Exception as e:
            logger.error(f"Error deserializing test result: {str(e)}")
            return None
