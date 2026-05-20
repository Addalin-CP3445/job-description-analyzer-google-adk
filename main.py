import os
import json
from dotenv import load_dotenv
load_dotenv()

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

import vertexai
# Replace "your-project-id" with your actual Google Cloud Project ID
vertexai.init(project="gdg-project-496917", location="us-central1")
from typing import List, Dict, Optional
from googlesearch import search

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool

class ParserSchema(BaseModel):
    hard_skills: List[str] = Field(description="List of hard skills extracted")
    soft_skills: List[str] = Field(description="List of soft skills extracted")
    years_of_experience: float = Field(description="Total years of professional experience")
    active_certifications: List[str] = Field(description="List of active certifications explicitly captured")

class MatchmakerSchema(BaseModel):
    matched_skills: List[str] = Field(description="Skills present in both CV and Job Description")
    missing_skills: List[str] = Field(description="Skills required by Job Description but missing from CV")
    remediation_strategy: Dict[str, str] = Field(
        description="Dictionary mapping each missing skill to one of: 'course', 'certification', or 'rewrite'"
    )

def course_search_tool_func(query: str) -> str:
    """
    Executes a web search for the given skill or certification name to find a relevant course,
    returning a markdown formatted link with the course title and URL.
    """
    try:
        results = search(f"best course for {query}", num_results=3, advanced=True)
        for res in results:
            if res.url:
                return f"[{res.title}]({res.url})"
        return f"No course found for {query}"
    except Exception as e:
        return f"Error searching for {query}: {str(e)}"

course_search_tool = FunctionTool(func=course_search_tool_func)

VERTEX_MODEL_NAME = "projects/gdg-project-496917/locations/us-central1/publishers/google/models/gemini-2.5-flash"

def run_analysis(cv_text: str, jd_text: str) -> str:
    parser_agent = LlmAgent(
        name="ParserAgent",
        model=VERTEX_MODEL_NAME,
        instruction="""You are a precise document parser. 
        Extract and categorize professional entities precisely from the provided raw CV and Job Description text. 
        Do not evaluate; only structure the data according to the schema.""",
        output_schema=ParserSchema
    )

    matchmaker_agent = LlmAgent(
        name="MatchmakerAgent",
        model=VERTEX_MODEL_NAME,
        instruction="""You are an analytical matchmaker. 
        Perform a logical gap analysis by cross-referencing the extracted CV baseline against the job requirements. 
        Determine the weight of missing skills and map them to a remediation strategy (course, certification, or rewrite).
        Your input will be a JSON object containing the CV and JD details.""",
        output_schema=MatchmakerSchema
    )

    career_coach_agent = LlmAgent(
        name="CareerCoachAgent",
        model=VERTEX_MODEL_NAME,
        instruction="""You are a professional Career Coach.
        Translate the gap analysis into a professional, human-readable advisory report.
        Whenever the remediation_strategy flags a missing skill that requires educational intervention (like 'course' or 'certification'), 
        you MUST use the CourseSearchTool to fetch a real course title and URL to include in your final report.
        Do not return JSON, just return a well-formatted markdown report.""",
        tools=[course_search_tool]
    )

    pipeline = SequentialAgent(
        name="CVAnalyzerPipeline",
        sub_agents=[parser_agent, matchmaker_agent, career_coach_agent]
    )

    session_service = InMemorySessionService()
    runner = Runner(agent=pipeline, app_name="CV_Analyzer", session_service=session_service, auto_create_session=True)

    initial_input = f"--- CV ---\n{cv_text}\n\n--- Job Description ---\n{jd_text}"

    print("Starting pipeline execution...")
    from google.genai.types import Content, Part
    msg_content = Content(role="user", parts=[Part.from_text(text=initial_input)])
    
    result = runner.run(new_message=msg_content, user_id="user1", session_id="session1")
    
    final_text = ""
    try:
        for chunk in result:
            if hasattr(chunk, 'content') and chunk.content and hasattr(chunk.content, 'parts'):
                for part in chunk.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_text += part.text
    except Exception as e:
        print(f"Pipeline finished, result: {result}")
    
    return final_text

def main():
    try:
        with open("cv.txt", "r", encoding="utf-8") as f:
            cv_text = f.read()
    except FileNotFoundError:
        cv_text = ""
        print("cv.txt not found, proceeding with empty CV")
        
    try:
        with open("jd.txt", "r", encoding="utf-8") as f:
            jd_text = f.read()
    except FileNotFoundError:
        jd_text = ""
        print("jd.txt not found, proceeding with empty JD")

    report = run_analysis(cv_text, jd_text)
    print("\n--- FINAL REPORT ---")
    print(report)

if __name__ == "__main__":
    main()
