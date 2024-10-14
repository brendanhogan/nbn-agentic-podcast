"""
This file contains classes representing podcast hosts for the Mohonk Stories show.
Each host class inherits from an abstract base class and provides a description
of the host's background and interests.
"""

from abc import ABC, abstractmethod

class Host(ABC):
    @abstractmethod
    def get_description(self) -> str:
        pass

class Bob(Host):
    def get_description(self) -> str:
        return (
            "Bob is a co-host of the Mohonk Stories podcast. "
            "He grew up in Brooklyn but now lives in New Paltz, NY. "
            "Bob works as a dentist and does podcasting on the side for fun. "
            "He's an avid reader and a big fan of the New York Yankees."
        )

class Carolyn(Host):
    def get_description(self) -> str:
        return (
            "Carolyn is a co-host of the Mohonk Stories podcast. "
            "She grew up in Dry Ridge, Kentucky but now resides in New Paltz, NY. "
            "Carolyn works as a school teacher. "
            "She's an avid reader with a particular interest in true crime stories."
        )
