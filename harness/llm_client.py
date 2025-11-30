import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger("Harness")

class LLMClient:
    def __init__(self, model: str = "gpt-5-nano"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def generate_tests(self, module_code: str, existing_test_code: str, coverage_info: str) -> str:
        """
        Generate improved tests for a module.
        Returns the FULL content of the test file.
        """
        prompt = f"""
You are an expert Python testing agent.
Your goal is to increase test coverage for a specific module.

Target Module Code:
```python
{module_code}
```

Existing Test Code:
```python
{existing_test_code}
```

Coverage Info:
{coverage_info}

INSTRUCTIONS:
1. Analyze the target module and the existing tests.
2. Identify gaps in coverage (branches, functions, or edge cases not tested).
3. Write a COMPLETE, updated test file that includes the original tests (if valid) and NEW tests to cover the gaps.
4. Do NOT remove existing tests unless they are incorrect.
5. Output ONLY the python code for the new test file. Do not include markdown backticks or explanations.
6. Ensure the code is runnable and imports are correct (assume `target_repo` is in python path).
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant specialized in Python unit testing."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            # Strip markdown if present
            if content.startswith("```python"):
                content = content.replace("```python", "", 1)
            if content.startswith("```"):
                content = content.replace("```", "", 1)
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            
            return content.strip()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
