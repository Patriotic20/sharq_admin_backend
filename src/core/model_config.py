from sqlalchemy.orm import relationship
from sharq_models.models import StudyForm, StudyDirection


def configure_models():
    """
    Configure SQLAlchemy models to fix relationship issues.
    This function should be called before any database operations.
    """
    # Add the missing study_directions relationship to StudyForm
    if not hasattr(StudyForm, 'study_directions'):
        StudyForm.study_directions = relationship(
            "StudyDirection",
            back_populates="study_form",
            primaryjoin="StudyForm.id == StudyDirection.study_form_id"
        )
    
    # Configure the registry
    StudyForm.registry.configure() 