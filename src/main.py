"""Main entry point for PM diagnostic system."""

import asyncio
import logging
import os
from dotenv import load_dotenv

from src.agents.orchestrator import OrchestratorAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    logger.info("PM Diagnostic System Starting...")

    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    # Example: Start a test
    logger.info("Creating a new test session...")

    # Start primary test
    response = await orchestrator.execute({
        "action": "start_primary_test",
        "user_id": "test_user_001",
    })

    if response.status == "success":
        logger.info(f"Test started successfully: {response.result}")
    else:
        logger.error(f"Failed to start test: {response.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
