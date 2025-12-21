"""Seed quiz questions for AI Readiness Quiz.

These questions are designed for a general audience, not just tech professionals.
They assess AI awareness, comfort level, and learning goals across 4 levels:
Novice, Beginner, Intermediate, Expert.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.quiz import QuizQuestion


QUIZ_QUESTIONS = [
    # Category: awareness - AI Familiarity & Understanding
    {
        "question_text": "How often do you use AI tools (like ChatGPT, Siri, Alexa, Google Assistant, or similar)?",
        "question_type": "multiple_choice",
        "category": "awareness",
        "options": [
            {"id": "a", "text": "Never - I haven't tried any AI tools", "score": 1},
            {"id": "b", "text": "Rarely - A few times in the past", "score": 2},
            {"id": "c", "text": "Sometimes - A few times a month", "score": 3},
            {"id": "d", "text": "Frequently - Multiple times a week or daily", "score": 5}
        ],
        "weight": 5,
        "order": 1
    },
    {
        "question_text": "Which of these AI tools have you heard of? (Select all that apply)",
        "question_type": "multi_select",
        "category": "awareness",
        "options": [
            {"id": "a", "text": "ChatGPT or Claude", "score": 1},
            {"id": "b", "text": "DALL-E, Midjourney, or image generators", "score": 1},
            {"id": "c", "text": "GitHub Copilot or coding assistants", "score": 1},
            {"id": "d", "text": "Voice assistants (Siri, Alexa)", "score": 1},
            {"id": "e", "text": "AI features in apps (Gmail suggestions, Netflix recommendations)", "score": 1}
        ],
        "weight": 4,
        "order": 2
    },
    {
        "question_text": "How would you describe your understanding of what AI can and cannot do?",
        "question_type": "multiple_choice",
        "category": "awareness",
        "options": [
            {"id": "a", "text": "Very limited - AI seems mysterious to me", "score": 1},
            {"id": "b", "text": "Basic - I know AI can answer questions and generate content", "score": 2},
            {"id": "c", "text": "Good - I understand AI's capabilities and common limitations", "score": 4},
            {"id": "d", "text": "Advanced - I understand how AI models work and their technical constraints", "score": 5}
        ],
        "weight": 5,
        "order": 3
    },

    # Category: daily_life - AI in Everyday Life
    {
        "question_text": "I feel comfortable using AI assistants for everyday tasks like writing emails, getting information, or creative projects.",
        "question_type": "self_assessment",
        "category": "daily_life",
        "scale_labels": {
            "1": "Not at all",
            "2": "Slightly",
            "3": "Moderately",
            "4": "Quite",
            "5": "Very comfortable"
        },
        "weight": 4,
        "order": 4
    },
    {
        "question_text": "I can usually tell when content (text, images, or videos) might be AI-generated.",
        "question_type": "self_assessment",
        "category": "daily_life",
        "scale_labels": {
            "1": "Never",
            "2": "Rarely",
            "3": "Sometimes",
            "4": "Often",
            "5": "Almost always"
        },
        "weight": 3,
        "order": 5
    },
    {
        "question_text": "I understand basic AI safety and privacy considerations when using AI tools.",
        "question_type": "self_assessment",
        "category": "daily_life",
        "scale_labels": {
            "1": "Not at all",
            "2": "Slightly",
            "3": "Somewhat",
            "4": "Well",
            "5": "Very well"
        },
        "weight": 4,
        "order": 6
    },

    # Category: goals - Learning & Goals
    {
        "question_text": "What brings you to the AI community?",
        "question_type": "multiple_choice",
        "category": "goals",
        "options": [
            {"id": "a", "text": "Curiosity - I want to understand what AI is about", "score": 2},
            {"id": "b", "text": "Learning - I want to improve my skills", "score": 3},
            {"id": "c", "text": "Career - I'm exploring AI-related job opportunities", "score": 4},
            {"id": "d", "text": "Business - I want to apply AI in my work or projects", "score": 5}
        ],
        "weight": 3,
        "order": 7
    },
    {
        "question_text": "What type of AI content interests you most?",
        "question_type": "multiple_choice",
        "category": "goals",
        "options": [
            {"id": "a", "text": "News and trends - What's happening in AI", "score": 2},
            {"id": "b", "text": "Tutorials - How to use AI tools effectively", "score": 3},
            {"id": "c", "text": "Tools - Finding the right AI tools for my needs", "score": 4},
            {"id": "d", "text": "Research - Deep dives into AI technology and papers", "score": 5}
        ],
        "weight": 3,
        "order": 8
    },
    {
        "question_text": "How do you prefer to learn about new topics?",
        "question_type": "multiple_choice",
        "category": "goals",
        "options": [
            {"id": "a", "text": "Videos and visual content", "score": 2},
            {"id": "b", "text": "Articles and written guides", "score": 3},
            {"id": "c", "text": "Hands-on practice and experiments", "score": 4},
            {"id": "d", "text": "Structured courses with exercises", "score": 5}
        ],
        "weight": 2,
        "order": 9
    },

    # Category: professional - Professional Context
    {
        "question_text": "AI is relevant to my current work or studies.",
        "question_type": "self_assessment",
        "category": "professional",
        "scale_labels": {
            "1": "Not relevant",
            "2": "Slightly",
            "3": "Somewhat",
            "4": "Quite relevant",
            "5": "Essential"
        },
        "weight": 4,
        "order": 10
    },
    {
        "question_text": "I have used AI to improve my productivity or complete tasks more efficiently.",
        "question_type": "self_assessment",
        "category": "professional",
        "scale_labels": {
            "1": "Never",
            "2": "Once or twice",
            "3": "Occasionally",
            "4": "Regularly",
            "5": "Daily"
        },
        "weight": 5,
        "order": 11
    },
    {
        "question_text": "I'm interested in AI career opportunities or integrating AI into my profession.",
        "question_type": "self_assessment",
        "category": "professional",
        "scale_labels": {
            "1": "Not interested",
            "2": "Slightly curious",
            "3": "Moderately interested",
            "4": "Very interested",
            "5": "Actively pursuing"
        },
        "weight": 4,
        "order": 12
    },

    # Category: comfort - Comfort & Confidence Level
    {
        "question_text": "I feel confident discussing AI topics with friends, colleagues, or in professional settings.",
        "question_type": "self_assessment",
        "category": "comfort",
        "scale_labels": {
            "1": "Not at all",
            "2": "Slightly",
            "3": "Somewhat",
            "4": "Quite",
            "5": "Very confident"
        },
        "weight": 4,
        "order": 13
    },
    {
        "question_text": "I can evaluate different AI tools and choose the right one for my specific needs.",
        "question_type": "self_assessment",
        "category": "comfort",
        "scale_labels": {
            "1": "Cannot at all",
            "2": "With difficulty",
            "3": "With some help",
            "4": "Independently",
            "5": "I could advise others"
        },
        "weight": 5,
        "order": 14
    },
    {
        "question_text": "I understand the ethical considerations around AI (bias, job impact, misinformation).",
        "question_type": "self_assessment",
        "category": "comfort",
        "scale_labels": {
            "1": "Not at all",
            "2": "Heard of them",
            "3": "Basic understanding",
            "4": "Good understanding",
            "5": "Could discuss in depth"
        },
        "weight": 4,
        "order": 15
    },

    # Additional awareness questions
    {
        "question_text": "Have you ever created something using AI (written content, images, code, music, etc.)?",
        "question_type": "multiple_choice",
        "category": "awareness",
        "options": [
            {"id": "a", "text": "No, I haven't tried", "score": 1},
            {"id": "b", "text": "Yes, once or twice to experiment", "score": 2},
            {"id": "c", "text": "Yes, several times for personal projects", "score": 4},
            {"id": "d", "text": "Yes, regularly for work or serious projects", "score": 5}
        ],
        "weight": 4,
        "order": 16
    },
    {
        "question_text": "When AI gives you an answer or result, how do you typically respond?",
        "question_type": "multiple_choice",
        "category": "comfort",
        "options": [
            {"id": "a", "text": "I accept it as correct", "score": 1},
            {"id": "b", "text": "I sometimes check if it seems wrong", "score": 2},
            {"id": "c", "text": "I usually verify important information", "score": 4},
            {"id": "d", "text": "I critically evaluate and fact-check outputs", "score": 5}
        ],
        "weight": 4,
        "order": 17
    },
]


async def seed_quiz_questions():
    """Seed the quiz questions into the database."""
    async with AsyncSessionLocal() as session:
        # Check if questions already exist
        result = await session.execute(select(QuizQuestion).limit(1))
        existing = result.scalar_one_or_none()

        if existing:
            print("Quiz questions already exist. Skipping seed.")
            print("To re-seed, delete existing questions first.")
            return

        # Insert questions
        for q_data in QUIZ_QUESTIONS:
            question = QuizQuestion(
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                category=q_data["category"],
                options=q_data.get("options"),
                scale_labels=q_data.get("scale_labels"),
                weight=q_data.get("weight", 1),
                is_active=True,
                order=q_data.get("order", 0),
            )
            session.add(question)

        await session.commit()
        print(f"Successfully seeded {len(QUIZ_QUESTIONS)} quiz questions.")


async def clear_and_reseed():
    """Clear existing questions and reseed."""
    async with AsyncSessionLocal() as session:
        # Delete all existing questions
        result = await session.execute(select(QuizQuestion))
        questions = result.scalars().all()
        for q in questions:
            await session.delete(q)
        await session.commit()
        print("Cleared existing questions.")

    await seed_quiz_questions()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed quiz questions")
    parser.add_argument("--reseed", action="store_true", help="Clear and reseed questions")
    args = parser.parse_args()

    if args.reseed:
        asyncio.run(clear_and_reseed())
    else:
        asyncio.run(seed_quiz_questions())
