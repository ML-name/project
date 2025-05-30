import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Add this import at the top
from tropos.preprocess_docx import StudentSubmission

class RubricProcessor:
    def __init__(self, root_dir='/content/project'):
        self.ROOT = root_dir
        self.RAW_DIR = f"{root_dir}/data/raw"
        self.PROCESSED_DIR = f"{root_dir}/data/processed/assignment"
        self.STUDENT_OUTPUT_DIR = f"{self.PROCESSED_DIR}/student_submissions"
        self.REQUIREMENTS_PATH = f"{self.RAW_DIR}/Requirements.docx"
        
        Path(self.STUDENT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    def format_clean_rubric(self):
        """Generate the clean rubric structure"""
        criteria = {
            "introduction": ["Engaging", ...],  # Your full criteria
            "background": [...],
            "analysis": [...],
            "response": [...]
        }
        return [{
            "portion_id": pid,
            "portion_name": pid.capitalize(),
            "criteria_group": criteria[pid]
        } for pid in criteria]

    def format_rubric_feedback(self, rubric):
        """Format feedback with criteria references"""
        portion_ids = ["introduction", "background", "analysis", "response"]
        feedback = []
        
        for i, portion in enumerate(rubric):
            items = portion.get("feedback", [])
            if not items:
                continue
            pid = portion_ids[i] if i < len(portion_ids) else f"portion_{i+1}"
            feedback.append({
                "portion_id": pid,
                "portion_name": pid.capitalize(),
                "criteria_group_ref": f"rubric_{pid}_criteria_group",
                "feedback": [
                    {"feedback_id": f"{pid}_F{j+1}", "text": fb.get("text", "")}
                    for j, fb in enumerate(items)
                ]
            })
        return feedback

    def process_student_submissions(self):
        """Main processing pipeline"""
        requirements_ref = "requirements/requirements.json"
        student_data = self._collect_submission_files()
        
        for sid, submissions in student_data.items():
            output = self._process_student(sid, submissions, requirements_ref)
            self._save_student_output(sid, output)
        
        self._save_metadata_files(requirements_ref)
        print("\nAll done.")

    def _collect_submission_files(self):
        """Scan directory and collect student files"""
        student_data = defaultdict(list)
        
        for folder in os.listdir(self.RAW_DIR):
            folder_path = os.path.join(self.RAW_DIR, folder)
            if not os.path.isdir(folder_path):
                continue

            for fname in os.listdir(folder_path):
                if not fname.endswith(".docx") or "requirements" in fname.lower():
                    continue

                sid = self._extract_student_id(fname)
                part = self._extract_part_key(fname)
                if not sid or not part:
                    print(f"⚠️ Skipping file: {fname}")
                    continue

                student_data[sid].append({
                    "filepath": os.path.join(folder_path, fname),
                    "filename": fname,
                    "part_key": part,
                    "mtime": os.path.getmtime(os.path.join(folder_path, fname))
                })
        return student_data

    def _process_student(self, sid, submissions, requirements_ref):
        """Process all submissions for one student"""
        output = {
            "student_id": sid,
            "requirements": requirements_ref,
            "submissions": {}
        }

        submissions.sort(key=lambda x: (
            float("inf") if x["part_key"] == "final" 
            else int(x["part_key"].split("_")[1]), 
            x["mtime"]
        ))
        seen = set()

        for sub in submissions:
            part = sub["part_key"]
            if part in seen:
                print(f"Duplicate part skipped: {part} ({sub['filename']})")
                continue
            seen.add(part)

            try:
                parsed = StudentSubmission(sub["filepath"], self.REQUIREMENTS_PATH).to_dict()
                output["submissions"][part] = {
                    "submission_text": parsed.get("submission_text", ""),
                    "comments": [
                        {k: v for k, v in c.items() if k != "commented_text"}
                        for c in parsed.get("comments", [])
                    ],
                    "rubric_feedback": self.format_rubric_feedback(parsed.get("rubric", []))
                }
                print(f"✅ {sub['filename']} -> {part}")
            except Exception as e:
                print(f"Failed {sub['filename']}: {e}")
        
        return output

    def _save_student_output(self, sid, output):
        """Save individual student JSON"""
        out_path = os.path.join(self.STUDENT_OUTPUT_DIR, f"{sid}.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"💾 Saved {out_path}")

    def _save_metadata_files(self, requirements_ref):
        """Save rubric and assignment metadata"""
        with open(os.path.join(self.PROCESSED_DIR, "rubric_table.json"), "w") as f:
            json.dump(self.format_clean_rubric(), f, indent=2)

        with open(os.path.join(self.PROCESSED_DIR, "assignment.json"), "w") as f:
            json.dump({"requirements": requirements_ref}, f, indent=2)

    @staticmethod
    def _extract_student_id(filename):
        match = re.search(r"Student[ _](\d+)", filename, re.IGNORECASE)
        return f"student{match.group(1).zfill(2)}" if match else None

    @staticmethod
    def _extract_part_key(filename):
        name = filename.lower()
        if "final" in name:
            return "final"
        match = re.search(r"part[ _]?(\d+)", name)
        if match:
            return f"part_{int(match.group(1))}"
        if re.search(r"student[ _]\d+", name):
            return "final"
        return None
    
##WHAT WOULD GO IN A/THE NOTEBOOK
## Import and call main functionfrom tropos import main
#main()
#import os
#import re
#import sys
#import json
#from pathlib import Path
#from collections import defaultdict

#from tropos.preprocess_docx.scraper1 import RubricProcessor


#processor = RubricProcessor(root_dir='/content/project')

# Run the processing
#processor.process_student_submissions()


##WHAT WOULD BE IN TROPOS __INIT__
# This file marks tropos as a Python package.

#from .models.gpt import generate_feedback
#from .models.trained import load_model

#from .preprocess_docx.rubric import parse_rubric
#from .preprocess_docx.submission import parse_submission
#from .preprocess_docx.assignment_requirements import parse_requirements
#from .preprocess_docx.comments import Comments, parse_comments
#from .preprocess_docx.scraper1 import process_student_submissions, RubricProcessor

#from .preprocess_docx import StudentSubmission


# Optional UI export
#from .gradio.ui import launch_ui

# Starts the program
#def main():
    # Tests the ui
    # make_ui()

    # Tests the docx data extraction

    #requirements_doc = Document()
    #requirements_doc.LoadFromFile(".data/raw/Requirements.docx")

    #submission_doc = Document()
    #submission_doc.LoadFromFile("data/raw/Student 1/Student 1 Part 1.docx")

    #print("Testing StudentSubmission class")
    #StudentSubmission(submission_doc, requirements_doc)

    #StudentSubmission(submission_doc, requirements_doc)



##WHAT WOULD BE IN PREPROCESS __INIT__
#
#from .scraper1 import RubricProcessor
#from .submission import parse_submission, Submission
#from .assignment_requirements import parse_requirements, AssignmentRequirements
#from .rubric import parse_rubric, Rubric
#from .comments import Comments

# Keep your existing StudentSubmission class
#class StudentSubmission:
    #def __init__(self, submission_path: str, requirements_path: str) -> None:
        #self.rubric = parse_rubric(submission_path)
        #self.submission = parse_submission(Document(submission_path))
        #self.comments = Comments(submission_path).parse_comments()
        #self.assignment_requirements = parse_requirements(requirements_path)

    #def to_dict(self):
        #return {
            #'comments': self.comments.get_results(),
            #'rubric': self.rubric.get_criteria(),
            #'feedback': self.rubric.get_comments(),
            #'assignment_requirements': self.assignment_requirements.get_instructions(),
            #'submission_text': self.submission.get_content()
        #}

# Explicitly list what should be importable
#__all__ = [
#    'StudentSubmission',
#    'RubricProcessor',
    # ... other classes/functions you want to expose ...
#]
    
    # TODO: Make getters and setters
    #
    # TODO: Make getters and setters
    #
