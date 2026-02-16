"""Re-export every model so Alembic and tests can import them in one shot."""

from applytrack.db.models.activity_event import ActivityEvent, ActivityEventType  # noqa: F401
from applytrack.db.models.ai_output import AIOutput, AIOutputKind  # noqa: F401
from applytrack.db.models.application import (  # noqa: F401
    Application,
    ApplicationPriority,
    ApplicationStatus,
)
from applytrack.db.models.company import Company  # noqa: F401
from applytrack.db.models.job_posting import JobPosting, JobSource, RemoteType  # noqa: F401
from applytrack.db.models.profile import Profile  # noqa: F401
from applytrack.db.models.reminder import Reminder  # noqa: F401
from applytrack.db.models.user import User  # noqa: F401
