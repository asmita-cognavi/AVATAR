# WITH ENHANCEMENT


from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, constr, conint
import docx
import json
from openai import OpenAI
import os

class PerformanceEnum(str, Enum):
    GPA = "gpa"
    PERCENTAGE = "percentage"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EmploymentType(str, Enum):
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    FULLTIME = "full_time"
    PARTTIME = "part_time"

class WorkplaceTypeEnum(str, Enum):
    IN_PERSON = "in_person"
    REMOTE = "remote"
    HYBRID = "hybrid"
    OPEN = "open_to_any"

class JobTypeEnum(str, Enum):
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    PERMANENT = "permanent"

# Data classes for various sections

@dataclass
class SkillResponse:
    name: str = ""
    rating: Optional[int] = None
    versions: Optional[List[str]] = None
    verified_skill_level: Optional[SkillLevel] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "rating": self.rating,
            "versions": self.versions,
            "verified_skill_level": (self.verified_skill_level.value
                                       if self.verified_skill_level else None)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillResponse':
        skill_level = data.get('verified_skill_level')
        if skill_level and not isinstance(skill_level, SkillLevel):
            skill_level = SkillLevel(skill_level)
        return cls(
            name=data.get('name', ''),
            rating=data.get('rating'),
            versions=data.get('versions', []),
            verified_skill_level=skill_level
        )

@dataclass
class JobLocationResponse:
    location_name: str = ""

    def to_dict(self) -> Dict:
        return {
            "location_name": self.location_name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'JobLocationResponse':
        return cls(location_name=data.get('location_name', ''))

@dataclass
class WorkExperienceResponse:
    work_experience_id: Optional[str] = None
    job_title: Optional[str] = None
    employer: Optional[str] = None
    location: Optional[str] = None
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    currently_working: Optional[bool] = None
    employment_type: Optional[EmploymentType] = None
    work_description: Optional[str] = None
    work_accomplishment: Optional[str] = None
    work_skills: Optional[List[SkillResponse]] = None
    ctc: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "work_experience_id": self.work_experience_id,
            "job_title": self.job_title,
            "employer": self.employer,
            "location": self.location,
            "start_month": self.start_month,
            "start_year": self.start_year,
            "end_month": self.end_month,
            "end_year": self.end_year,
            "currently_working": self.currently_working,
            "employment_type": (self.employment_type.value
                                if self.employment_type else None),
            "work_description": self.work_description,
            "work_accomplishment": self.work_accomplishment,
            "work_skills": [skill.to_dict() for skill in self.work_skills] if self.work_skills else None,
            "ctc": self.ctc
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkExperienceResponse':
        emp_type = data.get('employment_type')
        if emp_type and not isinstance(emp_type, EmploymentType):
            emp_type = EmploymentType(emp_type)
        work_skills = [SkillResponse.from_dict(skill) for skill in data.get('work_skills', [])] if data.get('work_skills') else None
        return cls(
            work_experience_id=data.get('work_experience_id'),
            job_title=data.get('job_title'),
            employer=data.get('employer'),
            location=data.get('location'),
            start_month=data.get('start_month'),
            start_year=data.get('start_year'),
            end_month=data.get('end_month'),
            end_year=data.get('end_year'),
            currently_working=data.get('currently_working'),
            employment_type=emp_type,
            work_description=data.get('work_description'),
            work_accomplishment=data.get('work_accomplishment'),
            work_skills=work_skills,
            ctc=data.get('ctc')
        )

@dataclass
class ProjectResponse:
    title: str = ""
    description: Optional[str] = None
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    is_in_progress: bool = False

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "start_month": self.start_month,
            "start_year": self.start_year,
            "end_month": self.end_month,
            "end_year": self.end_year,
            "is_in_progress": self.is_in_progress
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectResponse':
        return cls(
            title=data.get('title', ''),
            description=data.get('description'),
            start_month=data.get('start_month'),
            start_year=data.get('start_year'),
            end_month=data.get('end_month'),
            end_year=data.get('end_year'),
            is_in_progress=data.get('is_in_progress', False)
        )

@dataclass
class AchievementResponse:
    title: str = ""
    description: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AchievementResponse':
        return cls(
            title=data.get('title', ''),
            description=data.get('description')
        )

@dataclass
class PreferenceResponse:
    job_positions: Optional[Set[str]] = None
    professions: Optional[Set[str]] = None
    industry: Optional[Set[str]] = None
    job_location: Optional[List[JobLocationResponse]] = None
    job_type: Optional[JobTypeEnum] = None
    workplace_type: Optional[WorkplaceTypeEnum] = None
    expected_start_salary: Optional[int] = None
    expected_end_salary: Optional[int] = None
    currency: Optional[str] = None
    open_to_any_location: Optional[bool] = None
    immediate_joining: Optional[bool] = None

    def to_dict(self) -> Dict:
        return {
            "job_positions": list(self.job_positions) if self.job_positions else [],
            "professions": list(self.professions) if self.professions else [],
            "industry": list(self.industry) if self.industry else [],
            "job_location": [loc.to_dict() for loc in self.job_location] if self.job_location else [],
            "job_type": self.job_type.value if self.job_type else None,
            "workplace_type": self.workplace_type.value if self.workplace_type else None,
            "expected_start_salary": self.expected_start_salary,
            "expected_end_salary": self.expected_end_salary,
            "currency": self.currency,
            "open_to_any_location": self.open_to_any_location,
            "immediate_joining": self.immediate_joining
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PreferenceResponse':
        job_type = data.get('job_type')
        if job_type and not isinstance(job_type, JobTypeEnum):
            job_type = JobTypeEnum(job_type)

        workplace_type = data.get('workplace_type')
        if workplace_type and not isinstance(workplace_type, WorkplaceTypeEnum):
            workplace_type = WorkplaceTypeEnum(workplace_type)

        job_locations = [JobLocationResponse.from_dict(loc) for loc in data.get('job_location', [])] if data.get('job_location') else None
        return cls(
            job_positions=set(data.get('job_positions', [])),
            professions=set(data.get('professions', [])),
            industry=set(data.get('industry', [])),
            job_location=job_locations,
            job_type=job_type,
            workplace_type=workplace_type,
            expected_start_salary=data.get('expected_start_salary'),
            expected_end_salary=data.get('expected_end_salary'),
            currency=data.get('currency'),
            open_to_any_location=data.get('open_to_any_location'),
            immediate_joining=data.get('immediate_joining')
        )


@dataclass
class GapEducation:
    gap_reason: Optional[str] = None
    gap_duration: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "gap_reason": self.gap_reason,
            "gap_duration": self.gap_duration
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GapEducation':
        return cls(
            gap_reason=data.get("gap_reason"),
            gap_duration=data.get("gap_duration")
        )

@dataclass
class EducationsResponse:
    college_name: Optional[str] = None
    degree: Optional[str] = None
    stream: Optional[str] = None
    diploma_board: Optional[str] = None
    course: Optional[str] = None
    enrollment_no: Optional[str] = None
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    currently_attending: Optional[bool] = None
    performance_scale: Optional[PerformanceEnum] = None
    performance: Optional[float] = None
    skills: Optional[List[SkillResponse]] = None
    achievements: Optional[str] = None
    specialization: Optional[str] = None
    minor_specialization: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "college_name": self.college_name,
            "degree": self.degree,
            "stream": self.stream,
            "diploma_board": self.diploma_board,
            "course": self.course,
            "enrollment_no": self.enrollment_no,
            "start_month": self.start_month,
            "start_year": self.start_year,
            "end_month": self.end_month,
            "end_year": self.end_year,
            "currently_attending": self.currently_attending,
            "performance_scale": self.performance_scale.value if self.performance_scale else None,
            "performance": self.performance,
            "skills": [skill.to_dict() for skill in self.skills] if self.skills else None,
            "achievements": self.achievements,
            "specialization": self.specialization,
            "minor_specialization": self.minor_specialization
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'EducationsResponse':
        performance_scale = data.get("performance_scale")
        if performance_scale and not isinstance(performance_scale, PerformanceEnum):
            performance_scale = PerformanceEnum(performance_scale)
        skills = [SkillResponse.from_dict(skill) for skill in data.get("skills", [])] if data.get("skills") else None
        return cls(
            college_name=data.get("college_name"),
            degree=data.get("degree"),
            stream=data.get("stream"),
            diploma_board=data.get("diploma_board"),
            course=data.get("course"),
            enrollment_no=data.get("enrollment_no"),
            start_month=data.get("start_month"),
            start_year=data.get("start_year"),
            end_month=data.get("end_month"),
            end_year=data.get("end_year"),
            currently_attending=data.get("currently_attending"),
            performance_scale=performance_scale,
            performance=data.get("performance"),
            skills=skills,
            achievements=data.get("achievements"),
            specialization=data.get("specialization"),
            minor_specialization=data.get("minor_specialization")
        )

@dataclass
class StudentProfile:
    work_experience: List[WorkExperienceResponse]
    projects: List[ProjectResponse]
    skills: List[SkillResponse]
    preferences: PreferenceResponse
    achievements: List[AchievementResponse]
    educations: List[EducationsResponse]
    gap_education: Optional[GapEducation]

    def to_dict(self) -> Dict:
        return {
            "work_experience": [work.to_dict() for work in self.work_experience],
            "projects": [proj.to_dict() for proj in self.projects],
            "skills": [skill.to_dict() for skill in self.skills],
            "preferences": self.preferences.to_dict(),
            "achievements": [achievement.to_dict() for achievement in self.achievements],
            "educations": [edu.to_dict() for edu in self.educations],
            "gap_education": self.gap_education.to_dict() if self.gap_education else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StudentProfile':
        return cls(
            work_experience=[WorkExperienceResponse.from_dict(work) for work in data.get('work_experience', [])],
            projects=[ProjectResponse.from_dict(proj) for proj in data.get('projects', [])],
            skills=[SkillResponse.from_dict(skill) for skill in data.get('skills', [])],
            preferences=PreferenceResponse.from_dict(data.get('preferences', {})),
            achievements=[AchievementResponse.from_dict(achievement) for achievement in data.get('achievements', [])],
            educations=[EducationsResponse.from_dict(edu) for edu in data.get('educations', [])],
            gap_education=GapEducation.from_dict(data.get('gap_education')) if data.get('gap_education') else None
        )

# MAIN ANALYZER

class CareerCounselorAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def _create_extraction_prompt(self, transcript: str) -> str:
        return f"""Given a conversation transcript, extract information into this structured format. Return ONLY the JSON without any additional text or explanation:
{{
    "work_experience": [
        {{
            "work_experience_id": "string or null",
            "job_title": "string",
            "employer": "string",
            "location": "string",
            "start_month": integer,
            "start_year": integer,
            "end_month": integer or null,
            "end_year": integer or null,
            "currently_working": boolean,
            "employment_type": "freelance" | "internship" | "full_time" | "part_time",
            "work_description": "string",
            "work_accomplishment": "string",
            "work_skills": [
                {{
                    "name": "string",
                    "rating": integer (1-5),
                    "versions": ["string"],
                    "verified_skill_level": "beginner" | "intermediate" | "advanced"
                }}
            ],
            "ctc": integer or null
        }}
    ],
    "projects": [
        {{
            "title": "string",
            "description": "string",
            "start_month": integer,
            "start_year": integer,
            "end_month": integer or null,
            "end_year": integer or null,
            "is_in_progress": boolean
        }}
    ],
    "skills": [
        {{
            "name": "string",
            "rating": integer (1-5),
            "versions": ["string"],
            "verified_skill_level": "beginner" | "intermediate" | "advanced"
        }}
    ],
    "preferences": {{
        "job_positions": ["string"],
        "professions": ["string"],
        "industry": ["string"],
        "job_location": [
            {{
                "location_name": "string"
            }}
        ],
        "job_type": "contract" | "internship" | "permanent",
        "workplace_type": "in_person" | "remote" | "hybrid" | "open_to_any",
        "expected_start_salary": integer,
        "expected_end_salary": integer,
        "currency": "string",
        "open_to_any_location": boolean,
        "immediate_joining": boolean
    }},
    "achievements": [
        {{
            "title": "string",
            "description": "string"
        }}
    ],
    "educations": [
        {{
            "college_name": "string or null",
            "degree": "string or null",
            "stream": "string or null",
            "diploma_board": "string or null",
            "course": "string or null",
            "enrollment_no": "string or null",
            "start_month": integer,
            "start_year": integer,
            "end_month": integer or null,
            "end_year": integer or null,
            "currently_attending": boolean,
            "performance_scale": "gpa" | "percentage" or null,
            "performance": number or null,
            "skills": [
                {{
                    "name": "string",
                    "rating": integer (1-5),
                    "versions": ["string"],
                    "verified_skill_level": "beginner" | "intermediate" | "advanced"
                }}
            ],
            "achievements": "string or null",
            "specialization": "string or null",
            "minor_specialization": "string or null"
        }}
    ],
    "gap_education": {{
        "gap_reason": "string or null",
        "gap_duration": integer or null
    }}
}}

Extraction rules:
1. Work and Project descriptions should be elaborate, quantified and creative.
2. Years should be four-digit integers (e.g., 2024)
3. For ongoing activities, omit end_month and end_year and set currently_working or is_in_progress to true
4. Skill ratings should be 1-5 integers
5. Employment type should match exactly one of the specified values
6. Job type and workplace type should match exactly one of the specified values
7. Currency should be standard 3-letter code (e.g., "USD", "INR")
8. Months should be 1-12 integers.
9. All dates should be in ISO format (YYYY-MM-DD) when possible, or YYYY-MM or YYYY if only partial dates are available.
10. Location should be extracted for institutions, companies when mentioned.
11. If any field is not mentioned in the transcript, use null for optional fields or empty arrays for lists
12. Convert any mentioned CGPAs or Percentages to a 10.0 scale CGPA. No negatives should be entertained and if any, then set to 0.

Here's the conversation transcript:
{transcript}"""

    def analyze_transcript(self, transcript: str) -> StudentProfile:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert career counselor analyst. Extract information in the exact JSON format specified. Include only the JSON in your response, no additional text."},
                {"role": "user", "content": self._create_extraction_prompt(transcript)}
            ],
            temperature=0
        )

        try:
            data = json.loads(response.choices[0].message.content)
            return StudentProfile.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

def read_transcript(file_path: str) -> str:
    """
    Supports both DOCX and plain text (TXT) formats.
    """
    if file_path.lower().endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)
            return '\n'.join(full_text)
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    else:
        raise ValueError("Unsupported file format. Please provide a .docx or .txt file.")

def enhance_descriptions(section: List[Dict], section_type: str, api_key: str) -> List[Dict]:
    """
    Enhances the descriptions for either work experience or projects by calling the LLM.
    """
    enhanced_section = []
    llm_client = OpenAI(api_key=api_key)

    for item in section:
        if section_type == "work":
            details = (
                f"Job Title: {item.get('job_title', '')}\n"
                f"Current Description: {item.get('work_description', '')}\n"
                f"Accomplishments: {item.get('work_accomplishment', '')}\n"
                f"Skills: {', '.join([skill.get('name', '') for skill in (item.get('work_skills') or [])])}"
            )
        elif section_type == "project":
            details = (
                f"Project Title: {item.get('title', '')}\n"
                f"Current Description: {item.get('description', '')}"
            )
        else:
            details = ""

        prompt = (
    f"Enhance the following {section_type} details and generate 2-3 concise but well-descriptive bullet points "
    f"for the description. Each bullet should be separated by a newline. "
    f"Focus strongly on specific responsibilities, compulsorily quantify achievements, mention technologies used, and individual impact. "
    f"Do not include job titles or headers, only the bullet points.\n\n"
    f"{details}\n\n"
    f"Enhanced Description:"
)


        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative text enhancer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        enhanced_text = response.choices[0].message.content.strip()

        if section_type == "work":
            item["work_description"] = enhanced_text
        else:
            item["description"] = enhanced_text

        enhanced_section.append(item)
    return enhanced_section

def main():
    # Provide the file path directly (can be DOCX or TXT)
    transcript_file = '/content/example1.docx.txt'

    try:
        print("Reading transcript file...")
        transcript = read_transcript(transcript_file)
        print(transcript)
        print()
        API_KEY='sk-key'
        print("Analyzing transcript...")
        analyzer = CareerCounselorAnalyzer(api_key=API_KEY)
        profile = analyzer.analyze_transcript(transcript)

        work_experience_list = [we.to_dict() for we in profile.work_experience]
        enhanced_work = enhance_descriptions(work_experience_list, "work", api_key=API_KEY)
        profile.work_experience = [WorkExperienceResponse.from_dict(item) for item in enhanced_work]

        projects_list = [proj.to_dict() for proj in profile.projects]
        enhanced_projects = enhance_descriptions(projects_list, "project", api_key=API_KEY)
        profile.projects = [ProjectResponse.from_dict(item) for item in enhanced_projects]

        # Save results to JSON
        output_file = "analysis_results1.json"
        with open(output_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=4)
        print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
