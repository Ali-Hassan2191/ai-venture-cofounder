"""
Domain models and dataclasses for AI Venture Co-Founder.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Startup:
    name: str
    idea: str
    country: str
    target_market: str
    target_customer: str
    budget: float = 0.0
    currency: str = "$"
    founder_name: str = "Founder"
    founder_experience: str = "Beginner"
    additional_context: str = ""
    status: str = "created"
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class AgentResult:
    startup_id: int
    agent_key: str
    status: str = "pending"
    raw_output: str = ""
    structured_output: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class StartupAnalysis:
    startup_id: int
    overall_score: int = 0
    category_scores: Dict[str, int] = field(default_factory=dict)
    difficulty_level: str = "MEDIUM"
    difficulty_reasoning: str = ""
    executive_summary: str = ""
    problem_statement: str = ""
    solution_statement: str = ""
    usp: str = ""
    business_model: str = ""
    revenue_model: str = ""
    core_features: List[str] = field(default_factory=list)
    technical_direction: str = ""
    financial_overview: str = ""
    risk_analysis: Dict[str, Any] = field(default_factory=dict)
    key_advantages: List[str] = field(default_factory=list)
    major_risks: List[str] = field(default_factory=list)
    recommended_next_steps: List[str] = field(default_factory=list)
    feasibility_verdict: str = "Good Potential"
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class RoadmapTask:
    roadmap_id: int
    day_number: int
    phase: str
    title: str
    description: str = ""
    is_completed: bool = False
    notes: str = ""
    milestone_tag: str = ""
    id: Optional[int] = None


@dataclass
class DynamicRoadmap:
    startup_id: int
    total_duration_days: int
    current_day: int = 1
    current_phase: str = "Validation"
    progress_percent: float = 0.0
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[RoadmapTask] = field(default_factory=list)
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class ChatMessage:
    startup_id: int
    sender: str
    message: str
    timestamp: Optional[str] = None
    id: Optional[int] = None


@dataclass
class ReportMeta:
    startup_id: int
    file_path: str
    report_title: str
    generated_at: Optional[str] = None
    id: Optional[int] = None
