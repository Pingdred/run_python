from pydantic import BaseModel, Field

from cat.mad_hatter.decorators import plugin


class Settings(BaseModel):
    """Settings for the Meowgram plugin."""
    show_warnings: bool = Field(
        True,
        title="Show Warnings",
        description="Whether to show warnings in the confirmation message."
    )
    quick_execute: bool = Field(
        False,
        title="Quick Execute (Can be dangerous)",
        description="Whether to execute the code without asking for confirmation when ask directly to execute some code."
    )

@plugin
def settings_model():
    return Settings