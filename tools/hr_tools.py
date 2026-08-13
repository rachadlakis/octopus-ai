"""
HR Agent Tools - Recruitment, policies, and employee management.
"""
import re
from datetime import datetime


def generate_job_description(
    title: str,
    department: str,
    responsibilities: list,
    requirements: list,
    nice_to_have: list = None,
    employment_type: str = "Full-time",
    location: str = "Remote"
) -> dict:
    """
    Generate a professional job description.

    Args:
        title: Job title
        department: Department name
        responsibilities: List of key responsibilities
        requirements: List of required qualifications
        nice_to_have: Optional list of preferred qualifications
        employment_type: Full-time, Part-time, Contract, etc.
        location: Work location or Remote

    Returns:
        dict: Contains formatted job description
    """
    responsibilities_md = "\n".join(f"- {r}" for r in responsibilities)
    requirements_md = "\n".join(f"- {r}" for r in requirements)
    nice_to_have_md = ""

    if nice_to_have:
        nice_to_have_md = "\n\n### Nice to Have\n\n" + "\n".join(f"- {n}" for n in nice_to_have)

    content = f"""# {title}

**Department:** {department}
**Employment Type:** {employment_type}
**Location:** {location}

## About the Role

We are looking for a talented {title} to join our {department} team. This is an exciting opportunity to make a significant impact in a dynamic environment.

## Responsibilities

{responsibilities_md}

## Requirements

{requirements_md}
{nice_to_have_md}

## What We Offer

- Competitive salary and benefits
- Flexible working arrangements
- Professional development opportunities
- Collaborative and inclusive culture

## How to Apply

Please submit your resume and a brief cover letter explaining why you're interested in this role.

---
*We are an equal opportunity employer and value diversity at our company.*
"""

    return {
        "title": title,
        "content": content.strip(),
        "word_count": len(content.split())
    }


def parse_resume(resume_text: str) -> dict:
    """
    Parse resume text to extract key information.

    Args:
        resume_text: Plain text content of resume

    Returns:
        dict: Extracted information (name, email, phone, skills, etc.)
    """
    result = {
        "email": None,
        "phone": None,
        "skills": [],
        "education": [],
        "experience_years": None,
        "links": []
    }

    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, resume_text)
    if emails:
        result["email"] = emails[0]

    # Extract phone
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3,6}[-\s\.]?[0-9]{3,6}'
    phones = re.findall(phone_pattern, resume_text)
    if phones:
        result["phone"] = phones[0]

    # Extract URLs/links
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, resume_text)
    result["links"] = urls[:5]  # Limit to 5

    # Extract potential skills (common tech skills)
    common_skills = [
        'python', 'javascript', 'java', 'c\\+\\+', 'c#', 'ruby', 'go', 'rust', 'php',
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'git', 'ci/cd', 'agile', 'scrum', 'jira',
        'machine learning', 'ai', 'data science', 'analytics',
        'figma', 'sketch', 'photoshop', 'ui/ux',
        'excel', 'powerpoint', 'salesforce', 'hubspot'
    ]

    text_lower = resume_text.lower()
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + skill + r'\b', text_lower):
            found_skills.append(skill.replace('\\+', '+'))
    result["skills"] = found_skills

    # Try to extract years of experience
    exp_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience[:\s]*(\d+)\+?\s*years?',
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["experience_years"] = int(match.group(1))
            break

    # Extract education keywords
    education_keywords = [
        "bachelor", "master", "phd", "doctorate", "mba", "bs", "ba", "ms", "ma",
        "computer science", "engineering", "business", "mathematics"
    ]
    found_education = [kw for kw in education_keywords if kw in text_lower]
    result["education"] = found_education

    return result


def generate_interview_questions(role: str, level: str = "mid", question_type: str = "mixed") -> dict:
    """
    Generate interview questions for a specific role.

    Args:
        role: Job role (developer, designer, manager, marketing, sales, etc.)
        level: Experience level (junior, mid, senior, lead)
        question_type: Type of questions (behavioral, technical, mixed)

    Returns:
        dict: List of interview questions
    """
    behavioral_questions = [
        "Tell me about a time you faced a challenging deadline. How did you handle it?",
        "Describe a situation where you had to work with a difficult team member.",
        "Give an example of a project you're particularly proud of and why.",
        "Tell me about a time you received critical feedback. How did you respond?",
        "Describe a situation where you had to learn something new quickly.",
        "Tell me about a time you disagreed with your manager. How did you handle it?",
        "Give an example of when you went above and beyond for a project.",
        "Describe a failure you experienced and what you learned from it."
    ]

    role_questions = {
        "developer": {
            "junior": [
                "What programming languages are you most comfortable with?",
                "Describe your debugging process when code isn't working.",
                "How do you stay updated with new technologies?",
                "Walk me through a project you've built from scratch.",
                "What's your experience with version control (Git)?"
            ],
            "mid": [
                "How do you approach designing a new feature?",
                "Describe your experience with code reviews.",
                "How do you balance code quality with delivery speed?",
                "Tell me about a complex bug you solved and your approach.",
                "What's your experience with testing strategies?"
            ],
            "senior": [
                "How do you make architectural decisions?",
                "Describe your approach to mentoring junior developers.",
                "How do you handle technical debt?",
                "Tell me about a system you designed for scalability.",
                "How do you evaluate and introduce new technologies?"
            ]
        },
        "designer": {
            "junior": [
                "Walk me through your design process.",
                "What design tools are you proficient in?",
                "How do you handle feedback on your designs?",
                "Describe a project from your portfolio.",
                "How do you stay inspired and current with design trends?"
            ],
            "mid": [
                "How do you balance user needs with business goals?",
                "Describe your experience with user research.",
                "How do you handle disagreements about design decisions?",
                "Tell me about a design that significantly improved metrics.",
                "How do you ensure consistency across a product?"
            ],
            "senior": [
                "How do you build and maintain a design system?",
                "Describe your approach to leading design projects.",
                "How do you measure design success?",
                "Tell me about your experience with design strategy.",
                "How do you mentor and grow other designers?"
            ]
        },
        "manager": {
            "mid": [
                "How do you prioritize tasks for your team?",
                "Describe your approach to giving feedback.",
                "How do you handle underperforming team members?",
                "Tell me about how you've built team culture.",
                "How do you balance individual contributors' needs with team goals?"
            ],
            "senior": [
                "How do you develop your team members' careers?",
                "Describe a time you had to make an unpopular decision.",
                "How do you manage up and communicate with executives?",
                "Tell me about building a team from scratch.",
                "How do you handle organizational change?"
            ]
        },
        "marketing": {
            "mid": [
                "What marketing channels have you managed?",
                "How do you measure campaign success?",
                "Describe a successful campaign you've led.",
                "How do you stay updated with marketing trends?",
                "What's your experience with marketing analytics?"
            ],
            "senior": [
                "How do you develop a marketing strategy?",
                "Describe your experience with brand positioning.",
                "How do you allocate budget across channels?",
                "Tell me about managing a marketing team.",
                "How do you align marketing with sales and product?"
            ]
        }
    }

    # Get role-specific questions or use generic
    role_lower = role.lower()
    role_key = None
    for key in role_questions:
        if key in role_lower:
            role_key = key
            break

    level_key = "mid" if level.lower() not in ["junior", "mid", "senior", "lead"] else level.lower()
    if level_key == "lead":
        level_key = "senior"

    technical = []
    if role_key and role_key in role_questions:
        if level_key in role_questions[role_key]:
            technical = role_questions[role_key][level_key]
        else:
            technical = role_questions[role_key].get("mid", [])

    # Build final question list
    if question_type == "behavioral":
        questions = behavioral_questions[:6]
    elif question_type == "technical":
        questions = technical[:6] if technical else behavioral_questions[:3]
    else:  # mixed
        questions = behavioral_questions[:4] + (technical[:4] if technical else [])

    return {
        "role": role,
        "level": level,
        "question_type": question_type,
        "questions": questions,
        "tip": "Use the STAR method (Situation, Task, Action, Result) to evaluate behavioral answers"
    }


def create_onboarding_checklist(role: str, department: str) -> dict:
    """
    Generate an onboarding checklist for new employees.

    Args:
        role: Job role/title
        department: Department name

    Returns:
        dict: Onboarding checklist with tasks
    """
    # Common tasks for all roles
    common_tasks = {
        "Before Day 1": [
            "Send welcome email with start date details",
            "Prepare workstation/equipment",
            "Set up email and accounts",
            "Add to relevant Slack/Teams channels",
            "Assign onboarding buddy",
            "Schedule first week meetings"
        ],
        "Day 1": [
            "Welcome meeting with manager",
            "Office/virtual tour",
            "IT setup and security training",
            "Review company handbook and policies",
            "Complete HR paperwork",
            "Meet the team introductions",
            "Lunch with buddy/team"
        ],
        "Week 1": [
            "Complete required compliance training",
            "Set up development environment (if applicable)",
            "Review team processes and workflows",
            "1:1 with direct manager",
            "Shadow team members",
            "Access to relevant tools and systems",
            "Review current projects overview"
        ],
        "First 30 Days": [
            "Complete all onboarding training",
            "Understand team goals and OKRs",
            "Take on first small project/task",
            "Meet with key stakeholders",
            "30-day check-in with manager",
            "Provide onboarding feedback"
        ],
        "First 90 Days": [
            "Full integration into team workflow",
            "Complete first significant deliverable",
            "Participate in team planning sessions",
            "Build relationships across teams",
            "90-day performance conversation",
            "Set goals for next quarter"
        ]
    }

    # Role-specific additions
    role_specific = {
        "developer": [
            "Review codebase and architecture docs",
            "Set up local development environment",
            "Complete first code review",
            "Merge first pull request",
            "Understand CI/CD pipeline"
        ],
        "designer": [
            "Access design tools and libraries",
            "Review brand guidelines and design system",
            "Understand design review process",
            "Complete first design task",
            "Meet with product and engineering"
        ],
        "manager": [
            "Meet with each direct report",
            "Review team performance data",
            "Understand current team challenges",
            "Review budget and resources",
            "Meet with peer managers"
        ],
        "marketing": [
            "Review brand voice and style guide",
            "Access marketing tools and analytics",
            "Review current campaigns",
            "Understand content calendar",
            "Meet with sales team"
        ],
        "sales": [
            "Review product/service offerings",
            "Access CRM and sales tools",
            "Shadow sales calls",
            "Review sales playbook",
            "Meet with customer success team"
        ]
    }

    # Add role-specific tasks if applicable
    role_lower = role.lower()
    additional_tasks = []
    for key in role_specific:
        if key in role_lower:
            additional_tasks = role_specific[key]
            break

    if additional_tasks:
        common_tasks["Week 1"].extend(additional_tasks[:2])
        common_tasks["First 30 Days"].extend(additional_tasks[2:])

    return {
        "role": role,
        "department": department,
        "checklist": common_tasks,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "tip": "Customize this checklist based on your company's specific needs"
    }


def calculate_salary_range(role: str, level: str, location: str = "US") -> dict:
    """
    Estimate salary range based on role, level, and location.

    Args:
        role: Job role
        level: Experience level (junior, mid, senior, lead)
        location: Location/market (US, EU, Remote, etc.)

    Returns:
        dict: Estimated salary range

    Note: These are rough estimates for illustration. Use actual market data for real decisions.
    """
    # Base salary ranges (US market, in thousands)
    base_ranges = {
        "developer": {"junior": (60, 85), "mid": (90, 130), "senior": (130, 180), "lead": (160, 220)},
        "designer": {"junior": (50, 70), "mid": (75, 110), "senior": (110, 150), "lead": (140, 190)},
        "manager": {"mid": (90, 130), "senior": (130, 180), "lead": (170, 250)},
        "marketing": {"junior": (45, 65), "mid": (70, 100), "senior": (100, 150), "lead": (140, 200)},
        "sales": {"junior": (45, 60), "mid": (60, 90), "senior": (90, 140), "lead": (130, 200)},
        "hr": {"junior": (45, 60), "mid": (65, 95), "senior": (95, 140), "lead": (130, 180)},
        "analyst": {"junior": (55, 75), "mid": (80, 115), "senior": (115, 160), "lead": (150, 200)},
    }

    # Location multipliers
    location_multipliers = {
        "us": 1.0,
        "sf": 1.3,
        "nyc": 1.25,
        "seattle": 1.15,
        "austin": 0.95,
        "eu": 0.85,
        "uk": 0.9,
        "remote": 0.95,
        "asia": 0.6,
        "latam": 0.5
    }

    # Find matching role
    role_lower = role.lower()
    role_key = "developer"  # default
    for key in base_ranges:
        if key in role_lower:
            role_key = key
            break

    # Get level
    level_lower = level.lower()
    if level_lower not in ["junior", "mid", "senior", "lead"]:
        level_lower = "mid"

    # Get base range
    if level_lower in base_ranges[role_key]:
        low, high = base_ranges[role_key][level_lower]
    else:
        low, high = base_ranges[role_key].get("mid", (70, 100))

    # Apply location multiplier
    location_lower = location.lower()
    multiplier = 1.0
    for loc, mult in location_multipliers.items():
        if loc in location_lower:
            multiplier = mult
            break

    final_low = int(low * multiplier)
    final_high = int(high * multiplier)
    midpoint = int((final_low + final_high) / 2)

    return {
        "role": role,
        "level": level,
        "location": location,
        "salary_range": {
            "min": final_low * 1000,
            "max": final_high * 1000,
            "midpoint": midpoint * 1000,
            "currency": "USD"
        },
        "formatted": f"${final_low}K - ${final_high}K",
        "note": "Estimates based on general market data. Use actual salary surveys for accurate compensation planning."
    }


def generate_policy_template(policy_type: str) -> dict:
    """
    Generate HR policy templates.

    Args:
        policy_type: Type of policy (pto, remote, code_of_conduct, expenses, etc.)

    Returns:
        dict: Policy template content
    """
    templates = {
        "pto": """# Paid Time Off (PTO) Policy

## Overview
This policy outlines the company's paid time off benefits for eligible employees.

## Eligibility
All full-time employees are eligible for PTO benefits starting from their first day of employment.

## PTO Allowance
- **First Year:** 15 days (120 hours)
- **Years 2-4:** 20 days (160 hours)
- **Years 5+:** 25 days (200 hours)

## Requesting Time Off
1. Submit requests through the HR system at least 2 weeks in advance
2. Manager approval is required for all PTO requests
3. Requests during blackout periods may be limited

## Carryover
- Up to 5 days may be carried over to the next calendar year
- Carried-over days must be used by March 31

## Holidays
The company observes the following paid holidays in addition to PTO:
- New Year's Day
- Memorial Day
- Independence Day
- Labor Day
- Thanksgiving (2 days)
- Christmas (2 days)

*Last Updated: {date}*
""",
        "remote": """# Remote Work Policy

## Overview
This policy establishes guidelines for employees working remotely.

## Eligibility
Remote work arrangements may be available to employees whose job duties can be performed outside the office.

## Requirements
- Reliable internet connection (minimum 25 Mbps)
- Dedicated workspace free from distractions
- Availability during core hours (10 AM - 4 PM local time)
- Responsive on communication channels (Slack, email)

## Equipment
The company will provide:
- Laptop computer
- One-time $500 home office stipend

## Communication
- Respond to messages within 2 hours during work hours
- Keep calendar up to date
- Use video for meetings when possible

## Security
- Use company VPN when accessing sensitive data
- Lock computer when away
- Report lost/stolen equipment immediately

*Last Updated: {date}*
""",
        "code_of_conduct": """# Code of Conduct

## Our Commitment
We are committed to providing a welcoming and inclusive environment for everyone.

## Expected Behavior
- Treat all colleagues with respect and professionalism
- Communicate openly and constructively
- Value diverse perspectives and experiences
- Take responsibility for your actions
- Support your teammates

## Unacceptable Behavior
- Harassment, discrimination, or bullying
- Offensive or inappropriate language
- Sharing confidential information
- Conflicts of interest without disclosure
- Substance abuse in the workplace

## Reporting
If you witness or experience violations:
1. Report to your manager or HR
2. Use the anonymous reporting hotline
3. All reports will be investigated promptly

## Consequences
Violations may result in disciplinary action up to and including termination.

*Last Updated: {date}*
""",
        "expenses": """# Expense Reimbursement Policy

## Overview
This policy outlines procedures for business expense reimbursement.

## Eligible Expenses
- Business travel (flights, hotels, ground transportation)
- Client meals and entertainment
- Professional development and training
- Office supplies for remote workers
- Software and tools required for work

## Approval Requirements
- Under $100: No pre-approval needed
- $100-$500: Manager approval
- Over $500: Department head approval

## Submission Process
1. Submit expenses within 30 days
2. Include itemized receipts
3. Provide business justification
4. Use expense management system

## Travel Guidelines
- Book flights 14+ days in advance when possible
- Economy class for flights under 6 hours
- Hotels: Up to $200/night (varies by city)
- Meals: Up to $75/day

## Reimbursement Timeline
Approved expenses are reimbursed within 2 pay periods.

*Last Updated: {date}*
"""
    }

    policy_type_lower = policy_type.lower().replace(" ", "_")
    template = templates.get(policy_type_lower)

    if template:
        content = template.format(date=datetime.now().strftime("%B %Y"))
        return {
            "policy_type": policy_type,
            "content": content,
            "note": "This is a template. Review and customize for your organization."
        }
    else:
        available = list(templates.keys())
        return {
            "error": f"Template not found. Available: {', '.join(available)}"
        }