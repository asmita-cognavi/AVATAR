import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import openai
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define the dataclasses that model the target JSON structure
@dataclass
class Resource:
    title: str
    link: str
    type: str

@dataclass
class BulletPointResources:
    bullet_point: str
    resources: List[Resource]

@dataclass
class Phase:
    heading: str
    timeline: str
    content: List[str]
    phase_resources: List[BulletPointResources]

@dataclass
class TrendResource:
    title: str
    link: str
    type: str

@dataclass
class CurrentTrends:
    market_outlook: str
    salary_range: str
    industry_developments: str
    trend_resources: List[TrendResource]

@dataclass
class JobRole:
    name: str
    description: str
    aligned_skills: List[str]
    upskill_requirements: List[str]
    fit_rationale: str
    current_trends: CurrentTrends

@dataclass
class CategoryResource:
    title: str
    description: str
    link: str

@dataclass
class ResourceCategory:
    category: str
    resources: List[CategoryResource]

@dataclass
class EducationAnalysis:
    degree_relevance: str
    academic_strengths: List[str]

@dataclass
class SkillAssessment:
    technical_skills: List[str]
    soft_skills: List[str]

@dataclass
class ProfileSummary:
    title: str
    subtitle: str
    content: str
    education_analysis: EducationAnalysis
    skill_assessment: SkillAssessment
    key_strengths: List[str]
    areas_for_improvement: List[str]
    experience_evaluation: str

@dataclass
class PossibleJobRoles:
    title: str
    subtitle: str
    roles: List[JobRole]

@dataclass
class CareerPath:
    title: str
    subtitle: str
    phases: List[Phase]

@dataclass
class AdditionalResources:
    title: str
    subtitle: str
    general_resources: List[ResourceCategory]

@dataclass
class WelcomeIntroduction:
    title: str
    subtitle: str
    content: str

@dataclass
class Conclusion:
    title: str
    subtitle: str
    content: str

@dataclass
class CareerPathDocument:
    welcome_introduction: WelcomeIntroduction
    profile_summary: ProfileSummary
    possible_job_roles: PossibleJobRoles
    career_path_role_1: CareerPath
    career_path_role_2: CareerPath
    additional_resources: AdditionalResources
    conclusion: Conclusion

class CareerPathGenerator:
    def __init__(self, api_key=None):
      """Initialize the career path generator with OpenAI API key."""
      self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
      if not self.api_key:
          raise ValueError("OpenAI API key is required. Please provide it or set the OPENAI_API_KEY environment variable.")

      # Initialize OpenAI client
      self.client = openai.OpenAI(api_key=self.api_key)

      # Check if gpt-4o is available (required for web browsing capability)
      try:
          models = self.client.models.list()
          available_models = [model.id for model in models.data]
          if "gpt-4o" not in available_models:
              logging.warning("The gpt-4o model is not available. Web browsing capability may be limited.")
      except Exception as e:
          logging.warning(f"Could not check available models: {e}")

    def _create_generation_prompt(self, student_profile: Dict[str, Any]) -> str:
        """Create a prompt for generating the career path document."""
        return f"""Given a student profile, generate a personalized career path document in structured JSON format.
The document should be comprehensive, tailored to the student's background, and provide actionable guidance.

STUDENT PROFILE:
{json.dumps(student_profile, indent=2)}

Generate a complete, detailed career path document with the following structure.
Return ONLY the JSON without any additional text or explanation.
It should not begin and end with ```json as it disrupts parsing. Strictly give the json as follows:

{{
  "welcome_introduction": {{
    "title": "Welcome to Your Personalized Career Path",
    "subtitle": "A comprehensive guide based on your skills and experience",
    "content": "A personalized welcome message addressing the student by name and summarizing the purpose of this document. Atleast 5 well-written and creative sentences."
  }},
  "profile_summary": {{
    "title": "Profile Understanding",
    "subtitle": "Analysis of your resume and background",
    "content": "A comprehensive analysis of the student's educational background, technical skills, and relevant experiences.",
    "education_analysis": {{
      "degree_relevance": "How the student's degree aligns with industry demands",
      "academic_strengths": ["Specific strength 1", "Specific strength 2"]
    }},
    "skill_assessment": {{
      "technical_skills": ["Specific technical skill 1", "Specific technical skill 2"],
      "soft_skills": ["Specific soft skill 1", "Specific soft skill 2"]
    }},
    "key_strengths": ["Specific explanation of strength 1", "Specific explanation of strength 2"],
    "areas_for_improvement": ["Detailed explanation area 1", "Detailed explanation of area 2"],
    "experience_evaluation": "Evaluation of internships and projects with specific, but detailed insights. Atleast 2 sentences."
  }},
  "possible_job_roles": {{
    "title": "Recommended Career Paths",
    "subtitle": "Aligning Your Skills with Market Opportunities",
    "roles": [
      {{
        "name": "Specific Job Role 1",
        "description": "Detailed description of the first recommended job role and its primary responsibilities.",
        "aligned_skills": ["Specific skill from student profile 1", "Specific skill from student profile 2"],
        "upskill_requirements": ["Specific skill to develop 1", "Specific skill to develop 2"],
        "fit_rationale": "Detailed explanation of why this role is a good fit based on the student's unique combination of skills and experiences.",
        "current_trends": {{
          "market_outlook": "Specific growth projection and demand outlook for this role through next 5 years",
          "salary_range": "Specific salary range depending on experience and location",
          "industry_developments": "Specific major industry shifts, adoption trends, and emerging applications in this field",
          "trend_resources": [
            {{
              "title": "Specific Industry Report Title 1",
              "link": "https://example.com/industry-report",
              "type": "publication"
            }},
            {{
              "title": "Specific Government Data Source",
              "link": "https://example.gov/job-statistics",
              "type": "government data"
            }}
          ]
        }}
      }},
      {{
        "name": "Specific Job Role 2",
        "description": "Detailed description of the second recommended job role and its primary responsibilities.",
        "aligned_skills": ["Specific skill from student profile 1", "Specific skill from student profile 2"],
        "upskill_requirements": ["Specific skill to develop 1", "Specific skill to develop 2"],
        "fit_rationale": "Detailed explanation of why this role is a good fit based on the student's unique combination of skills and experiences.",
        "current_trends": {{
          "market_outlook": "Detailed insights on specific growth projection and demand outlook for this role through next 5 years. Atleast 3 sentences.",
          "salary_range": "Specific salary range depending on experience and location",
          "industry_developments": "Specific major industry shifts, adoption trends, and emerging applications in this field. Atleast 3 sentences or more.",
          "trend_resources": [
            {{
              "title": "Specific Industry Report Title 1",
              "link": "https://example.com/industry-report",
              "type": "news/article/blog/government data"
            }},
            {{
              "title": "Specific Government Data Source",
              "link": "https://example.gov/job-statistics",
              "type": "news/article/blog/government data"
            }}
          ]
        }}
      }}
    ]
  }},
  "career_path_role_1": {{
    "title": "Career Path: Specific Job Role 1",
    "subtitle": "From Entry Level to Leadership",
    "phases": [
      {{
        "heading": "Phase 1: Foundation Building",
        "timeline": "0-2 years",
        "content": [
          "Specific core skill or competency to develop 1",
          "Specific core skill or competency to develop 2",
          "Specific action item or milestone to achieve 3",
          "Specific action item or milestone to achieve 4",
          "Specific action item or milestone to achieve 5"
        ],
        "phase_resources": [
          {{
            "bullet_point": "Specific core skill or competency to develop 1",
            "resources": [
              {{
                "title": "Specific Resource Title 1",
                "link": "https://example.com/resource1",
                "type": "documentation"
              }},
              {{
                "title": "Specific Resource Title 2",
                "link": "https://example.com/resource2",
                "type": "book"
              }}
            ]
          }},
          {{
            "bullet_point": "Specific core skill or competency to develop 2",
            "resources": [
              {{
                "title": "Specific Resource Title 3",
                "link": "https://example.com/resource3",
                "type": "course"
              }},
              {{
                "title": "Specific Resource Title 4",
                "link": "https://example.com/resource4",
                "type": "github"
              }}
            ]
          }}
        ]
      }},
      {{
        "heading": "Phase 2: Specialization & Growth",
        "timeline": "2-5 years",
        "content": [
          "Specific specialization or growth area 1",
          "Specific specialization or growth area 2",
          "Specific mid-career milestone 3",
          "Specific mid-career milestone 4",
          "Specific mid-career milestone 5"
        ],
        "phase_resources": []
      }},
      {{
        "heading": "Phase 3: Advanced Expertise",
        "timeline": "5-8 years",
        "content": [
          "Specific advanced expertise area 1",
          "Specific advanced expertise area 2",
          "Specific senior-level responsibility 3",
          "Specific senior-level responsibility 4",
          "Specific senior-level responsibility 5"
        ],
        "phase_resources": []
      }},
      {{
        "heading": "Phase 4: Leadership & Innovation",
        "timeline": "8+ years",
        "content": [
          "Specific leadership or innovation area 1",
          "Specific leadership or innovation area 2",
          "Specific executive-level responsibility 3",
          "Specific executive-level responsibility 4",
          "Specific executive-level responsibility 5"
        ],
        "phase_resources": []
      }}
    ]
  }},
  "career_path_role_2": {{
    "title": "Career Path: Specific Job Role 2",
    "subtitle": "From Entry Level to Leadership",
    "phases": [
      {{
        "heading": "Phase 1: Foundation Building",
        "timeline": "0-2 years",
        "content": [
          "Specific core skill or competency to develop 1",
          "Specific core skill or competency to develop 2",
          "Specific action item or milestone to achieve 3",
          "Specific action item or milestone to achieve 4",
          "Specific action item or milestone to achieve 5"
        ],
        "phase_resources": []
      }},
      {{
        "heading": "Phase 2: Specialization & Growth",
        "timeline": "2-5 years",
        "content": [
          "Specific specialization or growth area 1",
          "Specific specialization or growth area 2",
          "Specific mid-career milestone 3",
          "Specific mid-career milestone 4",
          "Specific mid-career milestone 5"
        ],
        "phase_resources": []
      }},
      {{
        "heading": "Phase 3: Advanced Expertise",
        "timeline": "5-8 years",
        "content": [
          "Specific advanced expertise area 1",
          "Specific advanced expertise area 2",
          "Specific senior-level responsibility 3",
          "Specific senior-level responsibility 4",
          "Specific senior-level responsibility 5"
        ],
        "phase_resources": []
      }},
      {{
        "heading": "Phase 4: Leadership & Innovation",
        "timeline": "8+ years",
        "content": [
          "Specific leadership or innovation area 1",
          "Specific leadership or innovation area 2",
          "Specific executive-level responsibility 3",
          "Specific executive-level responsibility 4",
          "Specific executive-level responsibility 5"
        ],
        "phase_resources": []
      }}
    ]
  }},
  "additional_resources": {{
    "title": "Additional Learning Resources",
    "subtitle": "Supplementary materials to enhance your career journey",
    "general_resources": [
      {{
        "category": "Professional Development",
        "resources": [
          {{
            "title": "Specific resource title",
            "description": "What this resource offers specifically",
            "link": "URL to the resource"
          }}
        ]
      }},
      {{
        "category": "Technical Skills",
        "resources": [
          {{
            "title": "Specific resource title",
            "description": "What this resource offers specifically",
            "link": "URL to the resource"
          }}
        ]
      }},
      {{
        "category": "Industry Insights",
        "resources": [
          {{
            "title": "Specific resource title",
            "description": "What this resource offers specifically",
            "link": "URL to the resource"
          }}
        ]
      }}
    ]
  }},
  "conclusion": {{
    "title": "Final Thoughts on Your Career Journey",
    "subtitle": "Embracing continuous growth and adaptation",
    "content": "A personalized summary of key insights and encouragement for the career journey ahead, emphasizing the importance of continuous learning and adaptation in a dynamic professional landscape."
  }}
}}

Additional instructions:
1. Tailor all content specifically to the student's background, skills, and preferences
2. For job roles, choose 2 distinct options that align with the student's skill set and preferences
3. Career Development Phases:
  - Structure the career path into 4 distinct phases (Foundation Building, Specialization & Growth, Advanced Expertise, and Leadership & Innovation) with appropriate timelines for the specific field
  - Each phase heading must include the phase number (e.g., "Phase 1: Foundation Building") and reflect progression in seniority and responsibility
  - For each phase, provide 5 detailed, actionable, and field-specific bullet points in the "content" field that go beyond generic advice.
  - For technical roles: Include specific projects with titles, technologies used, technical challenges addressed, and measurable outcomes
  - For non-technical roles: Include specific initiatives, methodologies, frameworks, or business strategies relevant to the field
  - Suggest specific internship programs, fellowships, or entry-level opportunities with named organizations in the early phases
  - Recommend target companies at each career stage, including both industry leaders and innovative startups relevant to the field
  - Detail skill development recommendations with specific tools, platforms, or methodologies to master, along with suggested learning resources
  - When suggesting projects/initiatives, must include: project title ideas, unique value proposition ideas, required skills, estimated timeline, and potential impact metrics. Do not be generic but give creative doable ideas.
  - For networking recommendations: Name 2-3 specific industry leaders or organizations to follow/connect with on LinkedIn or other platforms with a brief explanation of their relevance
  - Include field-specific certifications, courses, or learning opportunities with specific names and providers
  - For management paths: Include specific team sizes, budgetary responsibilities, and leadership methodologies
  - For individual contributor paths: Include specialization opportunities, technical leadership roles, and ways to increase impact without direct reports
  - For entrepreneurial paths: Include specific market opportunities, founding team composition suggestions, and funding milestones
  - For other types of suggestions, write details accordingly but ensure they are well written and well-suited for career path.
  - Ensure content demonstrates clear progression with early phases focused on skill acquisition and execution, middle phases on specialization and project leadership, and later phases on strategic vision, innovation, and organizational impact.
  - Do not be generic but give creative doable ideas for every point made.

4. Make sure all industry trends and salary ranges are realistic and up to date
5. Include specific soft skills development not just technical skills
6. All fields for all "resources" should be set to null. It will be filled later so make sure all resources and its fields are null.
7. trend_resources should cite proper links from where trends have been extracted and no example site should be given. Make use of web search.
8. Strictly follow the JSON output format. It should not begin and end with ```json as it disrupts parsing. Simply give the json.

Note that the career path document should be HIGHLY PERSONALIZED to the specific student profile provided, with concrete recommendations based on their specific skills, interests, and background.
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with retries."""
        logging.info("Calling LLM...")
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert career counselor with deep knowledge of industry trends, job requirements, and career progression paths. Generate detailed, personalized career guidance in the exact JSON format specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        if not response.choices or not response.choices[0].message.content:
            logging.error(f"LLM returned empty response or missing content. Response: {response}")
            raise ValueError("LLM returned empty or incomplete response")

        return response.choices[0].message.content

    def enrich_resources_with_web_search(self, career_path_doc):
        """Enrich the empty resource fields with web search results."""
        logging.info("Enriching resources with web search...")

        # Set up tools for web browsing
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "browsing",
                    "description": "Browse the web to find information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on the web"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        # Function to process a single phase and find resources for each bullet point
        def process_phase_resources(phase):
            phase_resources = []
            for bullet_point in phase.content:
                resources = self._find_resources_for_bullet(bullet_point, phase.heading)
                phase_resources.append(BulletPointResources(
                    bullet_point=bullet_point,
                    resources=resources
                ))
            return phase_resources

        # Process career path role 1
        for i, phase in enumerate(career_path_doc.career_path_role_1.phases):
            career_path_doc.career_path_role_1.phases[i].phase_resources = process_phase_resources(phase)

        # Process career path role 2
        for i, phase in enumerate(career_path_doc.career_path_role_2.phases):
            career_path_doc.career_path_role_2.phases[i].phase_resources = process_phase_resources(phase)

        # Enrich trend resources for job roles
        for i, role in enumerate(career_path_doc.possible_job_roles.roles):
            career_path_doc.possible_job_roles.roles[i].current_trends.trend_resources = self._find_trend_resources(role)

        # Enrich additional resources
        updated_general_resources = []
        for category in career_path_doc.additional_resources.general_resources:
            resources = self._find_category_resources(category.category)
            updated_general_resources.append(ResourceCategory(
                category=category.category,
                resources=resources
            ))
        career_path_doc.additional_resources.general_resources = updated_general_resources

        return career_path_doc

    def _find_resources_for_bullet(self, bullet_point, phase_heading):
        """Find relevant resources for a specific bullet point using web search."""
        logging.info(f"Finding resources for: {bullet_point}")

        # Create a search query based on the bullet point and phase
        query = f"best resources for {bullet_point} in {phase_heading} career phase"

        # Prepare messages for the LLM
        messages = [
            {
                "role": "system",
                "content": """You are a career resource specialist. Your task is to find specific, high-quality resources
                related to the given career development bullet point. For each resource:
                1. Provide an accurate title
                2. Include a working link to the resource
                3. Identify the type (documentation, book, course, github, etc.)

                Focus on credible, current, and highly relevant resources. Avoid generic suggestions.
                Return exactly 2 resources in the specified format."""
            },
            {
                "role": "user",
                "content": f"Find resources for this career development item: '{bullet_point}' (Phase: {phase_heading})"
            }
        ]

        # Make initial request with tool call
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self._get_tools(),
            tool_choice="auto",
            temperature=0.3,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message
        all_messages = [*messages, assistant_message]

        # Process tool calls
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                query = function_args.get('query', '')

                # In a production environment, this would be a real web search
                # For demonstration, we'll simulate web search results
                search_results = self._simulate_web_search(query)

                all_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": search_results
                })

            # Get final response with resource information
            final_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=all_messages,
                temperature=0.2,
                max_tokens=1000
            )

            # Extract resources from the response
            try:
                # Parse the output for resource information
                content = final_response.choices[0].message.content
                resources = self._parse_resources_from_response(content)
                return resources
            except Exception as e:
                logging.error(f"Error extracting resources: {e}")
                return []
        else:
            return []

    def _find_trend_resources(self, job_role):
        """Find relevant trend resources for a job role using web search."""
        query = f"latest industry reports statistics trends for {job_role.name} career"

        messages = [
            {
                "role": "system",
                "content": """You are a career trends analyst. Identify 2-3 specific, current resources about
                industry trends for the given job role. Each resource should include:
                1. A specific publication title (industry report, article, or government data)
                2. A working link to the resource
                3. The type of resource (publication, government data, article, blog)

                Focus on credible, recent sources with actual industry data or insights."""
            },
            {
                "role": "user",
                "content": f"Find current trend resources for {job_role.name}, especially related to market outlook, salary range, and industry developments."
            }
        ]

        # Similar implementation as _find_resources_for_bullet
        # Make initial request with tool call
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self._get_tools(),
            tool_choice="auto",
            temperature=0.3,
            max_tokens=1000
        )

        # Process similar to _find_resources_for_bullet
        # Extract and return trend resources
        assistant_message = response.choices[0].message
        all_messages = [*messages, assistant_message]

        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            # Process tool calls, get final response
            # Implementation similar to _find_resources_for_bullet
            # Return parsed trend resources
            for tool_call in assistant_message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                query = function_args.get('query', '')

                search_results = self._simulate_web_search(query)

                all_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": search_results
                })

            final_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=all_messages,
                temperature=0.2,
                max_tokens=1000
            )

            try:
                content = final_response.choices[0].message.content
                return self._parse_trend_resources_from_response(content)
            except Exception as e:
                logging.error(f"Error extracting trend resources: {e}")
                return []
        else:
            return []

    def _find_category_resources(self, category):
        """Find resources for a specific category in additional resources."""
        query = f"best resources for {category} in professional development"

        messages = [
            {
                "role": "system",
                "content": f"""You are a professional development specialist. Identify 3 specific, high-quality
                resources for the '{category}' category. Each resource should include:
                1. A specific title
                2. A brief but specific description of what the resource offers
                3. A working link to the resource

                Focus on diverse, credible, and current resources that professionals would find valuable."""
            },
            {
                "role": "user",
                "content": f"Find 3 excellent resources for the '{category}' category that would be valuable for professional development."
            }
        ]

        # Implementation similar to other search methods
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self._get_tools(),
            tool_choice="auto",
            temperature=0.3,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message
        all_messages = [*messages, assistant_message]

        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                query = function_args.get('query', '')

                search_results = self._simulate_web_search(query)

                all_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": search_results
                })

            final_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=all_messages,
                temperature=0.2,
                max_tokens=1000
            )

            try:
                content = final_response.choices[0].message.content
                return self._parse_category_resources_from_response(content)
            except Exception as e:
                logging.error(f"Error extracting category resources: {e}")
                return []
        else:
            return []

    def _get_tools(self):
        """Return the tools configuration for web browsing."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "browsing",
                    "description": "Browse the web to find information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on the web"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _simulate_web_search(self, query):
        """
        Simulate a web search response.
        In a production environment, this would connect to a real search API.
        """
        logging.info(f"Web search query: {query}")

        # In production, replace this with actual search API calls
        # For example, using Bing Search API, Google Custom Search, etc.
        return f"""Search results for: {query}

    Result 1: [Title: "Complete Guide to {query}"] - This comprehensive resource covers all aspects of the topic with practical examples and step-by-step tutorials. URL: https://example.com/guide-to-{query.replace(' ', '-').lower()}

    Result 2: [Title: "Top Resources for {query}"] - Curated list of tools, courses, and communities focused on this area with reviews from professionals. URL: https://best-practices.org/{query.replace(' ', '_').lower()}

    Result 3: [Title: "{query} Certification Programs"] - Overview of available certifications with comparison of requirements, costs, and career impact. URL: https://certifications.edu/{query.replace(' ', '-').lower()}

    Result 4: [Title: "Latest Trends in {query}"] - Research report analyzing current industry developments and future projections with data visualizations. URL: https://trends-report.org/{query.replace(' ', '_').lower()}

    Result 5: [GitHub Repository: "{query}-toolkit"] - Open-source collection of tools and templates for professionals in this field with active community support. URL: https://github.com/community/{query.replace(' ', '-').lower()}-toolkit
        """

    def _parse_resources_from_response(self, content):
        """Parse resource information from the LLM response."""
        try:
            # For simplicity, we're assuming a structured response
            # In production, you might want to use regex or more sophisticated parsing
            resources = []
            lines = content.split('\n')

            current_title = None
            current_link = None
            current_type = None

            for line in lines:
                line = line.strip()
                if line.startswith("Title:") or line.startswith("Resource:") or line.startswith("1.") or line.startswith("2."):
                    # Save previous resource if we have one
                    if current_title and current_link and current_type:
                        resources.append(Resource(
                            title=current_title,
                            link=current_link,
                            type=current_type
                        ))

                    # Start new resource
                    current_title = line.split(":", 1)[1].strip() if ":" in line else line.split(".", 1)[1].strip()
                    current_link = None
                    current_type = None
                elif "http" in line.lower():
                    current_link = line.strip() if ":" not in line else line.split(":", 1)[1].strip()
                    # Extract URL if embedded in text
                    if "http" in current_link:
                        import re
                        urls = re.findall(r'https?://[^\s]+', current_link)
                        if urls:
                            current_link = urls[0]
                elif "type:" in line.lower() or "category:" in line.lower():
                    current_type = line.split(":", 1)[1].strip()

            # Add the last resource
            if current_title and current_link and current_type:
                resources.append(Resource(
                    title=current_title,
                    link=current_link,
                    type=current_type
                ))

            # Ensure we return at most 2 resources
            return resources[:2]
        except Exception as e:
            logging.error(f"Error parsing resources: {e}")
            return []

    def _parse_trend_resources_from_response(self, content):
        """Parse trend resource information from the LLM response."""
        try:
            # Similar implementation as _parse_resources_from_response
            # but adapted for TrendResource objects
            resources = []
            lines = content.split('\n')

            current_title = None
            current_link = None
            current_type = None

            for line in lines:
                line = line.strip()
                if line.startswith("Title:") or line.startswith("Resource:") or line.startswith("1.") or line.startswith("2."):
                    # Save previous resource if we have one
                    if current_title and current_link and current_type:
                        resources.append(TrendResource(
                            title=current_title,
                            link=current_link,
                            type=current_type
                        ))

                    # Start new resource
                    current_title = line.split(":", 1)[1].strip() if ":" in line else line.split(".", 1)[1].strip()
                    current_link = None
                    current_type = None
                elif "http" in line.lower():
                    current_link = line.strip() if ":" not in line else line.split(":", 1)[1].strip()
                    # Extract URL if embedded in text
                    if "http" in current_link:
                        import re
                        urls = re.findall(r'https?://[^\s]+', current_link)
                        if urls:
                            current_link = urls[0]
                elif "type:" in line.lower() or "category:" in line.lower():
                    current_type = line.split(":", 1)[1].strip()

            # Add the last resource
            if current_title and current_link and current_type:
                resources.append(TrendResource(
                    title=current_title,
                    link=current_link,
                    type=current_type
                ))

            return resources[:3]  # Limit to 3 resources
        except Exception as e:
            logging.error(f"Error parsing trend resources: {e}")
            return []

    def _parse_category_resources_from_response(self, content):
        """Parse category resource information from the LLM response."""
        try:
            resources = []
            lines = content.split('\n')

            current_title = None
            current_desc = None
            current_link = None

            for line in lines:
                line = line.strip()
                if line.startswith("Title:") or line.startswith("Resource:") or line.startswith("1.") or line.startswith("2."):
                    # Save previous resource if we have one
                    if current_title and current_desc and current_link:
                        resources.append(CategoryResource(
                            title=current_title,
                            description=current_desc,
                            link=current_link
                        ))

                    # Start new resource
                    current_title = line.split(":", 1)[1].strip() if ":" in line else line.split(".", 1)[1].strip()
                    current_desc = None
                    current_link = None
                elif "description:" in line.lower():
                    current_desc = line.split(":", 1)[1].strip()
                elif "http" in line.lower():
                    current_link = line.strip() if ":" not in line else line.split(":", 1)[1].strip()
                    # Extract URL if embedded in text
                    if "http" in current_link:
                        import re
                        urls = re.findall(r'https?://[^\s]+', current_link)
                        if urls:
                            current_link = urls[0]
                elif not current_desc and not line.startswith("Link:") and not line.startswith("URL:"):
                    # Assume this is a description if we don't have one yet
                    current_desc = line

            # Add the last resource
            if current_title and current_desc and current_link:
                resources.append(CategoryResource(
                    title=current_title,
                    description=current_desc,
                    link=current_link
                ))

            return resources[:3]  # Limit to 3 resources
        except Exception as e:
            logging.error(f"Error parsing category resources: {e}")
            return []

    def generate_career_path(self, student_profile: Dict[str, Any]) -> CareerPathDocument:
      """Generate a career path document based on the student profile."""
      prompt = self._create_generation_prompt(student_profile)

      llm_response = self._call_llm(prompt)
      try:
          logging.info("Parsing LLM response...")
          data = json.loads(llm_response)

          # Construct CareerPathDocument from the JSON response
          # [Your existing parsing code here]
          welcome = WelcomeIntroduction(**data["welcome_introduction"])

          # Extract profile summary
          profile_data = data["profile_summary"]
          education_analysis = EducationAnalysis(**profile_data["education_analysis"])
          skill_assessment = SkillAssessment(**profile_data["skill_assessment"])
          profile_summary = ProfileSummary(
              title=profile_data["title"],
              subtitle=profile_data["subtitle"],
              content=profile_data["content"],
              education_analysis=education_analysis,
              skill_assessment=skill_assessment,
              key_strengths=profile_data["key_strengths"],
              areas_for_improvement=profile_data["areas_for_improvement"],
              experience_evaluation=profile_data["experience_evaluation"]
          )

          # Extract job roles
          roles_data = data["possible_job_roles"]
          job_roles = []
          for role_data in roles_data["roles"]:
              trends_data = role_data["current_trends"]
              # Initially create with empty trend resources
              trend_resources = []
              current_trends = CurrentTrends(
                  market_outlook=trends_data["market_outlook"],
                  salary_range=trends_data["salary_range"],
                  industry_developments=trends_data["industry_developments"],
                  trend_resources=trend_resources
              )
              job_role = JobRole(
                  name=role_data["name"],
                  description=role_data["description"],
                  aligned_skills=role_data["aligned_skills"],
                  upskill_requirements=role_data["upskill_requirements"],
                  fit_rationale=role_data["fit_rationale"],
                  current_trends=current_trends
              )
              job_roles.append(job_role)

          possible_job_roles = PossibleJobRoles(
              title=roles_data["title"],
              subtitle=roles_data["subtitle"],
              roles=job_roles
          )

          # Extract career paths with initially empty resources
          def extract_career_path(path_data):
              phases = []
              for phase_data in path_data["phases"]:
                  # Initially create with empty phase resources
                  phase = Phase(
                      heading=phase_data["heading"],
                      timeline=phase_data["timeline"],
                      content=phase_data["content"],
                      phase_resources=[]  # Initially empty
                  )
                  phases.append(phase)

              return CareerPath(
                  title=path_data["title"],
                  subtitle=path_data["subtitle"],
                  phases=phases
              )

          career_path_role_1 = extract_career_path(data["career_path_role_1"])
          career_path_role_2 = extract_career_path(data["career_path_role_2"])

          # Extract additional resources
          resources_data = data["additional_resources"]
          general_resources = []
          for category_data in resources_data["general_resources"]:
              # Initially create with empty resources
              general_resources.append(ResourceCategory(
                  category=category_data["category"],
                  resources=[]  # Initially empty
              ))

          additional_resources = AdditionalResources(
              title=resources_data["title"],
              subtitle=resources_data["subtitle"],
              general_resources=general_resources
          )

          # Extract conclusion
          conclusion = Conclusion(**data["conclusion"])

          # Create initial document with empty resources
          career_path_document = CareerPathDocument(
              welcome_introduction=welcome,
              profile_summary=profile_summary,
              possible_job_roles=possible_job_roles,
              career_path_role_1=career_path_role_1,
              career_path_role_2=career_path_role_2,
              additional_resources=additional_resources,
              conclusion=conclusion
          )

          # Now enrich with web search for resources
          logging.info("Enriching document with web-searched resources...")
          enriched_document = self.enrich_resources_with_web_search(career_path_document)

          return enriched_document

      except json.JSONDecodeError as e:
          logging.error(f"Failed to parse LLM response as JSON: {e}, Response: {llm_response}")
          raise ValueError(f"Failed to parse LLM response as JSON: {e}")
      except KeyError as e:
          logging.error(f"Missing required field in JSON response: {e}, Response: {llm_response}")
          raise ValueError(f"Missing required field in JSON response: {e}")

    def generate_career_path_json(self, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a career path document as a JSON dictionary."""
        career_path_doc = self.generate_career_path(student_profile)
        return asdict(career_path_doc)

    def save_career_path_json(self, student_profile: Dict[str, Any], output_path: str) -> None:
        """Generate a career path document and save it to a JSON file."""
        career_path_json = self.generate_career_path_json(student_profile)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(career_path_json, f, indent=2)
        print(f"Career path document saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Example student profile (you would load this from your existing JSON)
    student_profile = {
        "work_experience": [
            {
                "job_title": "Software Engineering Intern",
                "employer": "Tech Solutions Inc.",
                "location": "San Francisco, CA",
                "start_month": 5,
                "start_year": 2023,
                "end_month": 8,
                "end_year": 2023,
                "currently_working": False,
                "employment_type": "internship",
                "work_description": "Developed and maintained RESTful APIs using Node.js and Express. Collaborated with the frontend team to integrate API endpoints.",
                "work_accomplishment": "Improved API response time by 40% through query optimization.",
                "work_skills": [
                    {
                        "name": "JavaScript",
                        "rating": 4,
                        "versions": ["ES6", "ES7"],
                        "verified_skill_level": "intermediate"
                    },
                    {
                        "name": "Node.js",
                        "rating": 3,
                        "versions": ["14.x"],
                        "verified_skill_level": "intermediate"
                    }
                ]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform with React, Node.js, and MongoDB. Implemented features like user authentication, product catalog, and payment processing.",
                "start_month": 9,
                "start_year": 2022,
                "end_month": 12,
                "end_year": 2022,
                "is_in_progress": False
            }
        ],
        "skills": [
            {
                "name": "JavaScript",
                "rating": 4,
                "versions": ["ES6", "ES7"],
                "verified_skill_level": "intermediate"
            },
            {
                "name": "React",
                "rating": 4,
                "versions": ["16.x", "17.x"],
                "verified_skill_level": "intermediate"
            },
            {
                "name": "Node.js",
                "rating": 3,
                "versions": ["14.x"],
                "verified_skill_level": "intermediate"
            },
            {
                "name": "MongoDB",
                "rating": 3,
                "versions": ["4.4"],
                "verified_skill_level": "beginner"
            },
            {
                "name": "Python",
                "rating": 3,
                "versions": ["3.8", "3.9"],
                "verified_skill_level": "intermediate"
            },
            {
                "name": "SQL",
                "rating": 2,
                "versions": [],
                "verified_skill_level": "beginner"
            }
        ],
        "preferences": {
            "job_positions": ["Software Engineer", "Full Stack Developer"],
            "professions": ["Web Development", "Software Development"],
            "industry": ["Technology", "Fintech"],
            "job_location": [
                {
                    "location_name": "San Francisco"
                },
                {
                    "location_name": "Remote"
                }
            ],
            "job_type": "permanent",
            "workplace_type": "hybrid",
            "expected_start_salary": 85000,
            "expected_end_salary": 95000,
            "currency": "USD",
            "open_to_any_location": False,
            "immediate_joining": True
        },
        "achievements": [
            {
                "title": "Hackathon Winner",
                "description": "First place in university hackathon for developing an innovative mobile app for campus navigation."
            }
        ],
        "educations": [
            {
                "college_name": "University of California, Berkeley",
                "degree": "Bachelor of Science",
                "stream": "Computer Science",
                "start_month": 8,
                "start_year": 2020,
                "end_month": 5,
                "end_year": 2024,
                "currently_attending": True,
                "performance_scale": "gpa",
                "performance": 3.7,
                "skills": [
                    {
                        "name": "Data Structures",
                        "rating": 4,
                        "versions": [],
                        "verified_skill_level": "intermediate"
                    },
                    {
                        "name": "Algorithms",
                        "rating": 4,
                        "versions": [],
                        "verified_skill_level": "intermediate"
                    }
                ],
                "achievements": "Dean's List 2021-2022",
                "specialization": "Software Engineering",
                "minor_specialization": "Data Science"
            }
        ]
    }

    # Initialize and use the generator
    generator = CareerPathGenerator(api_key="sk-key")

    # Generate and save the career path document
    generator.save_career_path_json(student_profile, "career_path_document.json")

    # Alternatively, get the document as a Python object
    # career_path = generator.generate_career_path(student_profile)

    # Or get the document as a JSON dictionary
    # career_path_json = generator.generate_career_path_json(student_profile)
