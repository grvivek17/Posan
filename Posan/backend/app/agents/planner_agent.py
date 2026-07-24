import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.agents import AgentBase, AgentStatus, AgentOutput
from app.services.ai_content import ContentGenerator


class PlannerAgent(AgentBase):
    """
    Agent responsible for generating study plans using AI.
    It takes topics and a timeline and breaks them down into study sessions.
    """
    
    def __init__(self):
        super().__init__(name="planner")
        self.ai = ContentGenerator()
        
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        {
            "subject": "Mathematics",
            "topics": ["Algebra", "Geometry", "Calculus"],
            "start_date": "2026-07-25",
            "end_date": "2026-07-30"
        }
        """
        subject = input_data.get("subject", "General Study")
        topics = input_data.get("topics", [])
        start_date_str = input_data.get("start_date")
        end_date_str = input_data.get("end_date")
        
        if not topics or not start_date_str or not end_date_str:
            raise ValueError("subject, topics, start_date, and end_date are required.")
            
        # Try to parse dates
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        days_available = (end_date - start_date).days + 1
        
        if days_available <= 0:
            raise ValueError("End date must be after or on the same day as start date.")
            
        # Use AI to generate the plan
        prompt = f"""
Create a study schedule for {subject}.
The topics to cover are: {', '.join(topics)}.
I have {days_available} days to study (from {start_date_str} to {end_date_str}).

Break down the topics across the days. Some days can have multiple topics, or a topic can span multiple days.
Return a valid JSON array of session objects. 
Do not include markdown blocks or any other text, just the raw JSON array.
Each object should have:
- "day_offset": (integer) Number of days from start date (0 is the first day).
- "topic": (string) The subtopic to study.
- "duration_minutes": (integer) Recommended duration in minutes (e.g., 30 or 45).

Example output format:
[
  {{"day_offset": 0, "topic": "Introduction to Algebra", "duration_minutes": 30}},
  {{"day_offset": 1, "topic": "Solving equations", "duration_minutes": 45}}
]
"""
        
        ai_response = self.ai._generate_text(prompt, max_tokens=1000)
        
        # Clean up possible markdown json blocks
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]
            
        ai_response = ai_response.strip()
        
        try:
            sessions_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback strategy if AI didn't return valid JSON
            self.logger.warning("AI did not return valid JSON for the study plan. Using fallback.")
            sessions_data = []
            
            # Simple division fallback
            for i, topic in enumerate(topics):
                day_offset = i % days_available
                sessions_data.append({
                    "day_offset": day_offset,
                    "topic": topic,
                    "duration_minutes": 30
                })
        
        # Finalize the response by converting day_offset to actual dates
        final_sessions = []
        for s in sessions_data:
            offset = s.get("day_offset", 0)
            session_date = start_date + timedelta(days=offset)
            final_sessions.append({
                "date": session_date.strftime("%Y-%m-%d"),
                "topic": s.get("topic", "General Study"),
                "duration_minutes": s.get("duration_minutes", 30)
            })
            
        # Sort sessions by date
        final_sessions.sort(key=lambda x: x["date"])
            
        return {
            "title": f"{subject} Study Plan",
            "subject": subject,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "total_sessions": len(final_sessions),
            "sessions": final_sessions
        }

# Instantiate the agent globally if needed, or register it
planner_agent = PlannerAgent()
