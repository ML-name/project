# from spire.doc import *
# from spire.doc.common import *
from docx import Document

from .comments import parse_comments, Comments
from .submission import parse_submission, Submission
from .assignment_requirements import parse_requirements, AssignmentRequirements
from .rubric import parse_rubric, Rubric

#student submission data and requirements

class StudentSubmission:

    rubric: Rubric
    """
    The rubric table at the bottom of the submission document 
    """

    comments: Comments
    """
    The inline comments 
    """

    requirements: AssignmentRequirements
    """
    The requirements file 
    """

    submission: Submission
    """
    The students written work
    """

    def __init__(self, submission_path: str, requirements_path: str) -> None:
        self.rubric = parse_rubric(submission_path)
        self.submission = parse_submission(submission_path)
        self.comments = parse_comments(submission_path)
        self.assignment_requirements = parse_requirements(Document(requirements_path))
        

    # TODO: Make getters and setters
    #
