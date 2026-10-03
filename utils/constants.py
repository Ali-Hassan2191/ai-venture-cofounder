"""
Global application constants and token budget configuration.
Centralized definitions ensure consistency across agents, UI, and database.
"""

# Application Branding
APP_NAME = "AI Venture Co-Founder"
APP_TAGLINE = "Turn Your Idea Into A Real Startup"
APP_DESCRIPTION = (
    "AI-powered virtual co-founder platform that conducts deep market research, "
    "competitor intelligence, financial modeling, marketing strategy, technical architecture, "
    "and holistic executive evaluation."
)

# Global LLM Output Token Budget
# A maximum total of 7,500 output tokens across all six agents combined.
MAX_TOTAL_OUTPUT_TOKENS = 7500

DEFAULT_TOKEN_ALLOCATIONS = {
    "market_research": 1000,
    "competitor_analysis": 850,
    "finance": 1700,
    "marketing": 850,
    "cto": 1050,
    "ceo": 2050,
}

# Supported LLM Providers & Models
DEFAULT_LLM_PROVIDER = "groq"
DEFAULT_LLM_MODEL = "openai/gpt-oss-120b"
DEFAULT_TEMPERATURE = 0.2

# Agent Names & Metadata
AGENT_METADATA = {
    "market_research": {
        "title": "Market Research Agent",
        "role": "Chief Market Strategist",
        "icon": "🔍",
        "description": "Analyzes market size, target customers, customer pain points, and local demand trends.",
        "badge_color": "#3B82F6",
    },
    "competitor_analysis": {
        "title": "Competitor Agent",
        "role": "Competitive Intelligence Lead",
        "icon": "👥",
        "description": "Researches direct & indirect competitors, pricing, positioning, strengths, and market gaps.",
        "badge_color": "#10B981",
    },
    "finance": {
        "title": "Finance Agent",
        "role": "Chief Financial Analyst",
        "icon": "💲",
        "description": "Calculates unit economics, initial investment, runway, pricing options, and break-even milestones.",
        "badge_color": "#8B5CF6",
    },
    "marketing": {
        "title": "Marketing Agent",
        "role": "Head of Growth & Go-To-Market",
        "icon": "📢",
        "description": "Builds customer acquisition funnels, promotional campaigns, launch roadmap, and retention tactics.",
        "badge_color": "#EC4899",
    },
    "cto": {
        "title": "CTO Agent",
        "role": "Chief Technology Officer",
        "icon": "💻",
        "description": "Architects technical stack, core features, system architecture, database requirements, and tech roadmap.",
        "badge_color": "#06B6D4",
    },
    "ceo": {
        "title": "CEO Agent",
        "role": "Executive Decision & Synthesis Lead",
        "icon": "👑",
        "description": "Synthesizes specialist findings, generates scores, risk matrices, startup blueprint, and dynamic execution roadmap.",
        "badge_color": "#F59E0B",
    },
}

# UI Navigation Items
NAV_ITEMS = [
    ("Overview", "📊"),
    ("Startup Idea", "🚀"),
    ("AI Agents", "🤖"),
    ("Market Analysis", "📈"),
    ("Competitors", "🎯"),
    ("Financial Model", "💰"),
    ("Blueprint", "📋"),
    ("Execution Plan", "🗓️"),
    ("Progress", "⚡"),
    ("Chat", "💬"),
    ("Reports", "📄"),
    ("Settings", "⚙️"),
]

# Database configuration
DEFAULT_DB_PATH = "data/venture_cofounder.db"

# FAISS Directory & Files
FAISS_DIR = "data/faiss_index"
FAISS_INDEX_FILE = "data/faiss_index/index.faiss"
FAISS_CONFIG_FILE = "data/faiss_index/config.json"
FAISS_METADATA_FILE = "data/faiss_index/metadata.json"
FAISS_CHUNKS_FILE = "data/faiss_index/chunks.json"

# Startup Form Options
COMMON_COUNTRIES = [
    "United States",
    "United Kingdom",
    "Pakistan",
    "India",
    "Canada",
    "Germany",
    "France",
    "Australia",
    "Singapore",
    "United Arab Emirates",
    "Saudi Arabia",
    "Brazil",
    "Global",
]

COMMON_STARTUP_CATEGORIES = [
    "Artificial Intelligence & Machine Learning",
    "B2B SaaS & Enterprise Software",
    "FinTech & Payments",
    "HealthTech & BioTech",
    "EdTech & Future of Work",
    "E-Commerce & Quick Commerce",
    "AgriTech & Food Systems",
    "ClimateTech & Clean Energy",
    "Logistics & Supply Chain",
    "Cybersecurity & Data Infrastructure",
    "Consumer Tech & Social",
    "Other",
]

FOUNDER_EXPERIENCE_LEVELS = [
    "Beginner",
    "Intermediate",
    "Experienced Serial Founder",
    "Domain Expert",
]

