import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class LLMClient:
    def __init__(self, model: str = "gpt-5-nano"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def generate_tests(self, module_code: str, module_path: str, existing_test_code: str, coverage_info: str) -> str:
        """
        Generate improved tests for a module.
        Returns the FULL content of the test file.
        """
        prompt = f"""
You are an expert Python testing agent. Your goal is to improve test coverage for the following module.

Target Module Path: {module_path}
(Use this path to correctly import the module in your tests. E.g. if path is 'target_repo/src/utils/helpers.py', import as 'from target_repo.src.utils.helpers import ...')

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

Task:
1. Analyze the module code and existing tests.
2. Write a COMPLETE Python test file that improves coverage.
3. If tests exist, keep them and add new ones. If no tests exist, create a full suite.
4. Ensure all imports are correct based on the module path provided.
5. Return ONLY the python code for the test file. No markdown formatting, no explanations.
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
