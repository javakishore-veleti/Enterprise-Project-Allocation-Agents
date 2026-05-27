"""The six MCP-AI agents."""
from .assignment_agent import AssignmentAgent
from .availability_checker_agent import AvailabilityCheckerAgent
from .communication_agent import CommunicationAgent
from .reporting_agent import ReportingAgent
from .requirement_parsing_agent import RequirementParsingAgent
from .skill_matching_agent import SkillMatchingAgent

# Canonical pipeline order (matches the paper).
PIPELINE = [
    RequirementParsingAgent,
    SkillMatchingAgent,
    AvailabilityCheckerAgent,
    AssignmentAgent,
    CommunicationAgent,
    ReportingAgent,
]

__all__ = ["PIPELINE", *[a.__name__ for a in PIPELINE]]
