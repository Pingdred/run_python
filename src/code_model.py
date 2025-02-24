from typing import Optional
from pydantic import BaseModel, Field


class CodeModel(BaseModel):

    thought: str = Field(
        ...,
        title="Thought",
        description="Thought about how to write the code or what the code should do. \
        Fill this field before writing the code to help you focus on the task and write a better code."
    ) # Usefull for the LLM to generate better code
    explain_to_user: Optional[str] = Field(
        None,
        title="Explain to User",
        description="This field should contain the explanation of the code for the user. Can be None if the code is self-explanatory or the use ask only for the code"
    )
    code: str = Field(
        ...,
        title="Python Code",
        description=""""The python code to execute. 
The code should be a valid Python code in a python code block like:
```python
print('Hello World')
```
"""
    )
    code_lang: str = Field(
        ...,
        title="Code Language",
        description="The programming language of the code."
    )
    execution_confirmed: bool = Field(
        False,
        title="Execution Confirmed",
        description="Whether the user asked directly to execute some specific code. If not set to False."
    )
    dependencies: list[str] = Field(
        [],
        title="Dependencies",
        description="Python dependencies required to execute the code."
    )
