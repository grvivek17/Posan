import httpx
import os
import json
import re

AI_GATEWAY_URL = os.getenv(
    "AI_GATEWAY_URL",
    "https://aigateway-intern.ad.infosys.com/aigateway/chat/completions"
)
AI_API_KEY = os.getenv("INFOSYS_CODER_API_KEY", "")

# Known skill keywords for fallback parsing
SKILL_CATEGORIES: dict[str, list[str]] = {
    "Frontend": ["react", "angular", "vue", "vue.js", "html", "html5", "css", "css3", "javascript", "typescript", "tailwind", "tailwind css", "bootstrap", "next.js", "nextjs", "svelte", "jquery", "sass", "less", "webpack", "vite", "redux", "zustand", "rxjs", "ngrx"],
    "Backend": ["node.js", "nodejs", "python", "java", "c#", ".net", "ruby", "php", "go", "golang", "rust", "scala", "express", "fastapi", "django", "flask", "spring", "spring boot", "rails", "laravel", "asp.net", "asp.net core", "signalr", "grpc", "kafka", "rabbitmq"],
    "Database": ["sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite", "oracle", "cassandra", "dynamodb", "firebase", "elasticsearch", "sql server", "cosmosdb", "db2"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "jenkins", "ci/cd", "github actions", "gitlab ci", "ansible", "helm", "linux", "argocd", "prometheus", "grafana", "datadog", "pulumi", "cloudformation"],
    "Testing": ["selenium", "cypress", "playwright", "junit", "testng", "pytest", "jest", "mocha", "chai", "testing", "qa", "automation", "bdd", "tdd", "appium", "detox", "espresso"],
    "Mobile": ["react native", "flutter", "swift", "kotlin", "ios", "android", "xamarin", "dart", "swiftui", "jetpack compose"],
    "Data & AI": ["machine learning", "ml", "ai", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "data science", "nlp", "computer vision", "scikit-learn", "langchain", "openai", "hugging face", "spark", "airflow", "databricks", "snowflake", "pyspark", "dbt", "mlflow", "kubeflow", "sagemaker"],
    "SAP": ["sap", "abap", "sap hana", "sap fiori", "sap ui5", "sap btp", "sap s/4hana", "sap ecc", "sap mm", "sap sd", "sap fi/co", "sap pp", "sap wm", "sap pi/po", "sap cpi", "bapi", "idoc", "odata"],
    "Mainframe": ["cobol", "jcl", "cics", "vsam", "rexx", "tso", "ispf", "mainframe", "endevor", "db2", "ims"],
    "Tools & Methodologies": ["git", "jira", "confluence", "agile", "scrum", "kanban", "rest", "graphql", "microservices", "api", "safe", "itil"],
}


def fallback_parse_resume(resume_text: str) -> dict:
    """Parse resume text without AI, using keyword matching."""
    text_lower = resume_text.lower()
    lines = resume_text.strip().split("\n")

    # Extract name (first non-empty line)
    name = ""
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) < 60 and not any(c in stripped for c in ["@", "http", "://"]):
            name = stripped
            break

    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', resume_text)
    email = email_match.group(0) if email_match else ""

    # Extract phone
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', resume_text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # Extract skills by category
    skills_result = []
    for category, keywords in SKILL_CATEGORIES.items():
        found_skills = []
        for kw in keywords:
            if kw in text_lower:
                found_skills.append({"name": kw.title() if len(kw) > 3 else kw.upper(), "level": "Intermediate", "years": None})
        if found_skills:
            skills_result.append({"category": category, "skills": found_skills})

    # Extract experience years
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)', text_lower)
    experience_years = int(exp_match.group(1)) if exp_match else None

    # Try to calculate from date ranges like (2015-2023)
    if not experience_years:
        year_ranges = re.findall(r'(20\d{2})\s*[-–]\s*(20\d{2}|[Pp]resent)', resume_text)
        if year_ranges:
            min_year = min(int(yr[0]) for yr in year_ranges)
            max_year = max(2025 if yr[1].lower() == "present" else int(yr[1]) for yr in year_ranges)
            experience_years = max_year - min_year

    # Extract education
    education = []
    edu_patterns = [
        r"((?:B\.?Tech|B\.?S|B\.?Sc|B\.?E|B\.?A|M\.?Tech|M\.?S|M\.?Sc|M\.?E|M\.?A|MBA|Ph\.?D|Bachelor|Master)\b[^.\n]{0,80})",
    ]
    for pat in edu_patterns:
        for match in re.finditer(pat, resume_text, re.IGNORECASE):
            text = match.group(0).strip()
            # Filter out false positives - must be at start of a line or after a bullet
            if len(text) > 10 and any(kw in text.lower() for kw in ["tech", "science", "engineering", "university", "college", "institute", "mit", "stanford", "bachelor", "master", "mba", "phd"]):
                education.append({"degree": text, "institution": "", "year": ""})

    # Extract certifications
    certifications = []
    cert_keywords = ["certified", "certification", "certificate", "aws ", "azure ", "gcp ", "pmp", "istqb", "scrum master"]
    for line in lines:
        line_lower = line.strip().lower()
        if any(kw in line_lower for kw in cert_keywords) and len(line.strip()) < 100:
            certifications.append(line.strip())

    # Build summary
    summary_parts = []
    if experience_years:
        summary_parts.append(f"{experience_years}+ years of experience")
    all_skills = []
    for cat in skills_result:
        for s in cat["skills"][:3]:
            all_skills.append(s["name"])
    if all_skills:
        summary_parts.append(f"skilled in {', '.join(all_skills[:6])}")
    summary = "Professional with " + " and ".join(summary_parts) + "." if summary_parts else "Professional profile."

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "skills": skills_result,
        "experience_years": experience_years,
        "education": education,
        "certifications": certifications,
    }


async def call_ai(system_prompt: str, user_prompt: str) -> str:
    if not AI_API_KEY:
        return "AI_UNAVAILABLE"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}",
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }
    try:
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            response = await client.post(AI_GATEWAY_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI_UNAVAILABLE: {str(e)}"


async def generate_skill_matrix(resume_text: str) -> dict:
    system_prompt = """You are an expert HR analyst. Analyze the resume text and extract a structured skill matrix.
Return ONLY valid JSON with this structure:
{
  "name": "candidate name",
  "email": "email if found",
  "phone": "phone if found",
  "summary": "brief professional summary",
  "skills": [
    {"category": "category name", "skills": [{"name": "skill", "level": "Expert/Advanced/Intermediate/Beginner", "years": number_or_null}]}
  ],
  "experience_years": total_years_number,
  "education": [{"degree": "degree", "institution": "school", "year": "year"}],
  "certifications": ["cert1", "cert2"]
}"""
    result = await call_ai(system_prompt, f"Extract skill matrix from this resume:\n\n{resume_text}")

    # If AI is available, try to parse the response
    if not result.startswith("AI_UNAVAILABLE"):
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # Fallback: parse resume with keyword matching
    return fallback_parse_resume(resume_text)


def fallback_match_profiles(query: str, profiles_data: list[dict]) -> str:
    """Match profiles against a query using keyword matching when AI is unavailable."""
    query_lower = query.lower()
    results = []

    # Stop words to ignore in query matching
    stop_words = {
        "i", "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "is", "it", "be", "as", "do", "no", "not", "so", "if",
        "my", "we", "me", "he", "up", "am", "was", "are", "has", "had", "can",
        "need", "want", "wanted", "looking", "find", "search", "get", "team",
        "people", "person", "who", "that", "this", "have", "like", "some",
        "developers", "developer", "engineers", "engineer", "professionals",
        "candidates", "candidate", "resources", "resource", "members", "member",
    }

    # All known tech skills for strict matching
    known_skills: set[str] = set()
    for cat_skills in SKILL_CATEGORIES.values():
        for s in cat_skills:
            known_skills.add(s.lower())

    # Extract meaningful tech keywords from query (not stop words)
    query_words = re.findall(r'\b[\w.#+]+\b', query_lower)
    query_tech_terms = [w for w in query_words if w not in stop_words and len(w) > 1]

    # Also check for multi-word tech terms in the query
    query_multi_terms: list[str] = []
    for skill in known_skills:
        if " " in skill and skill in query_lower:
            query_multi_terms.append(skill)

    # Role-type keywords map to required skills
    role_keywords = {
        "frontend": ["react", "angular", "vue", "html", "css", "javascript", "typescript"],
        "backend": ["node", "python", "java", "express", "fastapi", "spring", "django"],
        "tester": ["selenium", "cypress", "testing", "qa", "playwright", "junit", "pytest"],
        "test": ["selenium", "cypress", "testing", "qa", "playwright", "junit", "pytest"],
        "fullstack": ["react", "node", "python", "javascript", "typescript"],
        "full stack": ["react", "node", "python", "javascript", "typescript"],
        "devops": ["docker", "kubernetes", "aws", "terraform", "jenkins", "ci/cd"],
        "mobile": ["react native", "flutter", "swift", "kotlin", "ios", "android"],
        "cobol": ["cobol"],
        "mainframe": ["cobol", "jcl", "cics", "db2", "mainframe"],
        "sap": ["sap", "abap", "hana"],
        "data": ["pandas", "numpy", "tensorflow", "pytorch", "data science", "machine learning"],
    }

    # Determine what skills to look for based on query
    required_skill_sets: list[str] = []

    # Add role-based skills
    for role, role_skills in role_keywords.items():
        if role in query_lower:
            required_skill_sets.extend(role_skills)

    # Add direct tech terms from query
    for term in query_tech_terms:
        if term in known_skills:
            required_skill_sets.append(term)
    for term in query_multi_terms:
        required_skill_sets.append(term)

    # If no recognizable tech terms or roles found, try matching query words directly
    if not required_skill_sets:
        required_skill_sets = query_tech_terms

    for profile in profiles_data:
        score = 0
        matched_skills = []
        name = profile.get("name", "Unknown")
        skills_data = profile.get("skills", {})

        # Flatten all skill names from the profile
        all_skills: list[str] = []
        if isinstance(skills_data, dict):
            for cat in skills_data.get("skills", []):
                if isinstance(cat, dict):
                    for s in cat.get("skills", []):
                        if isinstance(s, dict):
                            all_skills.append(s.get("name", "").lower())
        elif isinstance(skills_data, list):
            for item in skills_data:
                if isinstance(item, str):
                    all_skills.append(item.lower())

        all_skills_str = " ".join(all_skills)

        # Only match on required skill sets — strict matching
        for req_skill in required_skill_sets:
            for profile_skill in all_skills:
                if req_skill == profile_skill or req_skill in profile_skill or profile_skill in req_skill:
                    score += 1
                    matched_skills.append(profile_skill)
                    break

        # Deduplicate matched skills
        matched_skills = list(set(matched_skills))

        # Only include if there are actual skill matches
        if score > 0 and matched_skills:
            results.append((score, name, profile.get("id"), matched_skills))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        return f"No matching profiles found for: \"{query}\". The required skills were not found in any uploaded profiles. Consider uploading more resumes with the relevant skill set."

    response_lines = [f"Found {len(results)} matching profile(s) for: \"{query}\"\n"]
    for i, (score, name, pid, skills) in enumerate(results, 1):
        response_lines.append(f"{i}. **{name}** (Profile #{pid})")
        response_lines.append(f"   Matching skills: {', '.join(s.title() for s in skills[:8])}")
        response_lines.append(f"   Match score: {score}\n")

    return "\n".join(response_lines)


async def find_matching_profiles(query: str, profiles_data: list[dict]) -> str:
    system_prompt = """You are a talent management assistant. The user will describe what kind of team or profiles they need.
You have access to a database of candidate profiles with their skills.
Analyze the requirement and match it against available profiles.
Provide a clear, conversational response listing the best matches and why they match.
If no good matches are found, suggest what skills to look for when hiring."""

    profiles_summary = json.dumps(profiles_data, indent=2)
    user_prompt = f"""Requirement: {query}

Available Profiles:
{profiles_summary}

Find the best matching profiles for this requirement. Be specific about why each profile matches."""
    result = await call_ai(system_prompt, user_prompt)

    if result.startswith("AI_UNAVAILABLE"):
        return fallback_match_profiles(query, profiles_data)
    return result


def fallback_telecaller_script(questions: list[str], profile_info: dict) -> str:
    """Generate a basic telecaller script without AI."""
    name = profile_info.get("name", "Candidate")
    lines = [
        f"--- Telecaller Script for {name} ---\n",
        f"Hello, may I speak with {name}? This is [Your Name] calling from [Company Name].",
        f"I'm reaching out regarding a potential opportunity that matches your profile.\n",
        "Do you have a few minutes to answer some screening questions?\n",
        "--- Questions ---\n",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q}")
        lines.append(f"   [Wait for response and note it down]\n")

    lines.append("\n--- Closing ---")
    lines.append(f"Thank you so much for your time, {name}.")
    lines.append("We will review your responses and get back to you shortly.")
    lines.append("Have a great day!")
    return "\n".join(lines)


async def generate_telecaller_script(questions: list[str], profile_info: dict) -> str:
    system_prompt = """You are a professional telecaller assistant. Generate a natural, friendly phone call script
for screening a candidate. Include greetings, the questions provided, and a professional closing.
Keep it conversational and professional."""

    user_prompt = f"""Generate a telecaller script for this candidate:
Name: {profile_info.get('name', 'Candidate')}
Position related skills: {json.dumps(profile_info.get('skills', []))}

Questions to ask:
{json.dumps(questions, indent=2)}

Create a natural phone call script."""
    result = await call_ai(system_prompt, user_prompt)

    if result.startswith("AI_UNAVAILABLE"):
        return fallback_telecaller_script(questions, profile_info)
    return result
