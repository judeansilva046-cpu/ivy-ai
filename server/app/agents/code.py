"""
Code Agent - Execute and analyze code
Handles Python and JavaScript code execution with safety constraints
"""
from typing import Dict, Any, Optional
import re
from app.agents.base import BaseAgent, AgentCapability
from app.services.llm import get_llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CodeAgent(BaseAgent):
    """Code Agent - Execute and debug code

    This agent provides:
    - Python code execution
    - JavaScript code validation
    - Code analysis and debugging
    - Error explanation
    """

    def __init__(self):
        """Initialize Code Agent"""
        super().__init__(
            agent_id="ivy-code",
            name="Ivy Code",
            description="Execute and analyze code with safety constraints",
            version="1.0.0",
        )

        # Initialize LLM service
        self.llm_service = get_llm_service()

        # Define capabilities
        self.add_capability(
            AgentCapability(
                name="python-execution",
                description="Execute Python code and return results",
            )
        )
        self.add_capability(
            AgentCapability(
                name="javascript-validation",
                description="Analyze and validate JavaScript code",
            )
        )
        self.add_capability(
            AgentCapability(
                name="code-analysis",
                description="Analyze code quality and suggest improvements",
            )
        )
        self.add_capability(
            AgentCapability(
                name="error-debugging",
                description="Debug errors and suggest fixes",
            )
        )

        logger.info("CodeAgent initialized successfully")

    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        """Extract code blocks from text

        Looks for:
        ```python
        code here
        ```

        ```javascript
        code here
        ```
        """
        code_blocks = {}

        # Python blocks
        python_pattern = r"```python\n(.*?)\n```"
        for match in re.finditer(python_pattern, text, re.DOTALL):
            code_blocks["python"] = match.group(1)

        # JavaScript blocks
        js_pattern = r"```(?:javascript|js)\n(.*?)\n```"
        for match in re.finditer(js_pattern, text, re.DOTALL):
            code_blocks["javascript"] = match.group(1)

        return code_blocks

    async def _analyze_code(self, code: str, language: str) -> str:
        """Analyze code using LLM"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"Analyze this {language} code for quality, efficiency, and potential issues:\n\n```{language}\n{code}\n```",
                }
            ]

            analysis = await self._llm_response(messages)
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {language} code: {str(e)}")
            raise

    async def _execute_python(self, code: str) -> str:
        """Execute Python code safely (SANDBOX REQUIRED IN PRODUCTION)"""
        try:
            # In production, this should use a sandboxed execution environment
            # For now, we'll use LLM to simulate execution

            messages = [
                {
                    "role": "user",
                    "content": f"Execute this Python code and return the output:\n\n```python\n{code}\n```\n\nProvide only the output, or explain any errors.",
                }
            ]

            result = await self._llm_response(messages)
            return result

        except Exception as e:
            logger.error(f"Error executing Python code: {str(e)}")
            return f"Error: {str(e)}"

    async def _validate_javascript(self, code: str) -> str:
        """Validate JavaScript code"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"Validate this JavaScript code and explain any issues:\n\n```javascript\n{code}\n```\n\nCheck for: syntax errors, undefined variables, best practices.",
                }
            ]

            validation = await self._llm_response(messages)
            return validation

        except Exception as e:
            logger.error(f"Error validating JavaScript: {str(e)}")
            return f"Error: {str(e)}"

    async def _llm_response(self, messages: list) -> str:
        """Get response from LLM"""
        try:
            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt="You are a helpful code assistant. Provide clear, accurate responses about code execution and analysis.",
            )
            return response
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            raise

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process message for code-related tasks

        Args:
            message: User message that may contain code
            context: Additional context

        Returns:
            Analysis, execution result, or explanation
        """
        try:
            # Extract code blocks from message
            code_blocks = self._extract_code_blocks(message)

            if not code_blocks:
                # No code found, ask LLM for general help
                messages = [{"role": "user", "content": message}]
                return await self._llm_response(messages)

            response_parts = []

            # Process Python code
            if "python" in code_blocks:
                logger.info("Processing Python code block")
                result = await self._execute_python(code_blocks["python"])
                response_parts.append(f"**Python Execution:**\n{result}")

            # Process JavaScript code
            if "javascript" in code_blocks:
                logger.info("Processing JavaScript code block")
                result = await self._validate_javascript(code_blocks["javascript"])
                response_parts.append(f"**JavaScript Validation:**\n{result}")

            # If message asks for analysis
            if "analyze" in message.lower() or "improve" in message.lower():
                for lang, code in code_blocks.items():
                    analysis = await self._analyze_code(code, lang)
                    response_parts.append(
                        f"**{lang.title()} Analysis:**\n{analysis}"
                    )

            response = "\n\n".join(response_parts) if response_parts else message

            logger.info("CodeAgent processing completed")
            return response

        except Exception as e:
            logger.error(f"Error in CodeAgent.process: {str(e)}")
            raise


async def get_code_agent() -> CodeAgent:
    """Get or create code agent instance"""
    return CodeAgent()
