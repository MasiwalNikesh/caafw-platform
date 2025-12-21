"""Quiz API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.quiz import QuizQuestion, QuizResult
from app.models.user import User, UserProfile
from app.schemas.quiz import (
    QuizSubmission, QuizQuestionResponse,
    QuizResultResponse, QuizResultDetailResponse
)
from app.core.deps import get_current_user

router = APIRouter()


def compute_level(percentage: int) -> str:
    """
    Compute user level from quiz percentage.

    Levels:
    - Novice: 0-24%
    - Beginner: 25-49%
    - Intermediate: 50-74%
    - Expert: 75-100%
    """
    if percentage >= 75:
        return "expert"
    elif percentage >= 50:
        return "intermediate"
    elif percentage >= 25:
        return "beginner"
    else:
        return "novice"


@router.get("/questions", response_model=List[QuizQuestionResponse])
async def get_quiz_questions(db: AsyncSession = Depends(get_db)):
    """
    Get all active quiz questions.
    No authentication required - questions are public.
    """
    query = (
        select(QuizQuestion)
        .where(QuizQuestion.is_active == True)
        .order_by(QuizQuestion.order, QuizQuestion.id)
    )
    result = await db.execute(query)
    questions = result.scalars().all()

    # Return questions without exposing scores in options
    return [
        QuizQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            category=q.category,
            options=[
                {"id": opt.get("id"), "text": opt.get("text")}
                for opt in (q.options or [])
            ] if q.options else None,
            scale_labels=q.scale_labels,
            order=q.order,
        )
        for q in questions
    ]


@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz(
    submission: QuizSubmission,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit quiz answers and get result.
    Requires authentication.
    """
    # Get all questions by IDs from submission
    question_ids = [a.question_id for a in submission.answers]
    query = select(QuizQuestion).where(
        QuizQuestion.id.in_(question_ids),
        QuizQuestion.is_active == True
    )
    result = await db.execute(query)
    questions = {q.id: q for q in result.scalars().all()}

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid questions found"
        )

    # Score answers
    total_score = 0
    max_score = 0
    answers_detail = []
    category_scores = {}
    category_max = {}

    for answer in submission.answers:
        question = questions.get(answer.question_id)
        if not question:
            continue

        # Calculate max possible score for this question
        question_max_score = question.weight

        # For multiple choice and multi-select, find max score from options
        if question.question_type in ["multiple_choice", "multi_select"] and question.options:
            option_scores = [opt.get("score", 0) for opt in question.options]
            if option_scores:
                question_max_score = max(option_scores) * question.weight

        # For self-assessment (1-5 scale), max is 5
        if question.question_type == "self_assessment":
            question_max_score = 5 * question.weight

        max_score += question_max_score
        category = question.category

        if category not in category_scores:
            category_scores[category] = 0
            category_max[category] = 0
        category_max[category] += question_max_score

        # Calculate score based on question type
        score = 0

        if question.question_type == "multiple_choice":
            # Find score for selected option
            for opt in (question.options or []):
                if opt.get("id") == answer.answer:
                    score = opt.get("score", 0) * question.weight
                    break

        elif question.question_type == "multi_select":
            # Sum scores for all selected options (comma-separated)
            selected = answer.answer.split(",")
            for opt in (question.options or []):
                if opt.get("id") in selected:
                    score += opt.get("score", 0) * question.weight

        elif question.question_type == "self_assessment":
            # Scale 1-5, use value directly
            try:
                scale_value = int(answer.answer)
                if 1 <= scale_value <= 5:
                    score = scale_value * question.weight
            except ValueError:
                score = 0

        total_score += score
        category_scores[category] += score

        answers_detail.append({
            "question_id": answer.question_id,
            "answer": answer.answer,
            "score": score,
        })

    # Convert category scores to percentages
    for cat in category_scores:
        if category_max[cat] > 0:
            category_scores[cat] = int((category_scores[cat] / category_max[cat]) * 100)

    # Calculate overall percentage
    percentage = int((total_score / max_score * 100)) if max_score > 0 else 0
    computed_level = compute_level(percentage)

    # Save result
    quiz_result = QuizResult(
        user_id=user.id,
        total_score=int(total_score),
        max_possible_score=int(max_score),
        percentage=percentage,
        computed_level=computed_level,
        answers=answers_detail,
        category_scores=category_scores,
    )
    db.add(quiz_result)

    # Update user profile
    profile_query = select(UserProfile).where(UserProfile.user_id == user.id)
    profile_result = await db.execute(profile_query)
    profile = profile_result.scalar_one_or_none()

    if profile:
        profile.ai_level = computed_level
        profile.ai_level_score = percentage
        profile.has_completed_quiz = True

    await db.commit()
    await db.refresh(quiz_result)

    return QuizResultResponse.model_validate(quiz_result)


@router.get("/results", response_model=List[QuizResultResponse])
async def get_quiz_results(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's quiz history."""
    query = (
        select(QuizResult)
        .where(QuizResult.user_id == user.id)
        .order_by(QuizResult.created_at.desc())
    )
    result = await db.execute(query)
    results = result.scalars().all()

    return [QuizResultResponse.model_validate(r) for r in results]


@router.get("/results/{result_id}", response_model=QuizResultDetailResponse)
async def get_quiz_result_detail(
    result_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed quiz result with answers."""
    query = select(QuizResult).where(
        QuizResult.id == result_id,
        QuizResult.user_id == user.id
    )
    result = await db.execute(query)
    quiz_result = result.scalar_one_or_none()

    if not quiz_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz result not found"
        )

    return QuizResultDetailResponse.model_validate(quiz_result)
