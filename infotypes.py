"""

This module defines the typing system for agent inputs and outputs.
Each agent in the workflow takes some text input, performs computation,
and returns some output. To ensure agents can work together seamlessly,
we need a consistent typing system for these information types.

"""

from typing import List


class SourceText:
    description: str = "Original source text to be processed"
    def __init__(self, value: str):
        self.value = value

class Summary:
    description: str = "A condensed version of the source text"
    def __init__(self, value: str):
        self.value = value

class Narrative(Summary):
    description: str = "A focused, story-driven summary of the source text"
    def __init__(self, value: str):
        super().__init__(value)

class Acts(Summary):
    description: str = "A summary divided into distinct narrative acts"
    def __init__(self, value: str):
        super().__init__(value)

class IndepthSummary(Summary):
    description: str = "A detailed, comprehensive summary of the source text"
    def __init__(self, value: str):
        super().__init__(value)

class Transcript:
    description: str = "A written record of spoken content"
    def __init__(self, value: str):
        self.value = value

class PersonalizedTranscript(Transcript):
    description: str = "A transcript tailored to specific preferences or requirements"
    def __init__(self, value: str):
        super().__init__(value)

class Bool:
    description: str = "A boolean value"
    def __init__(self, value: bool):
        self.value = value
