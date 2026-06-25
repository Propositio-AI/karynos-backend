from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.gateways import dreamer_gateway
from app.services.onboarding.schemas import (
    GetInitQuestionsResponse,
    InitAnswerHistoryItem,
    InitAnswerResponse,
    InitAnswersSubmitResponse,
    InitQuestionOptionResponse,
    InitQuestionResponse,
    SubmitInitAnswersRequest,
)


class OnboardingService:
    def get_questions(self, version: int = 1) -> GetInitQuestionsResponse:
        questions_response = dreamer_gateway.list_init_questions(version)
        self._ensure_success(questions_response)
        questions_data = questions_response["data"]
        if not questions_data:
            raise HTTPException(
                status_code=404, detail=f"バージョン {version} の質問が見つかりません"
            )

        questions_with_options = []
        for question in questions_data:
            options_response = dreamer_gateway.list_question_options(
                question.question_id
            )
            self._ensure_success(options_response)
            options = options_response["data"] or []
            options_list = [
                InitQuestionOptionResponse(
                    option_id=opt.option_id,
                    option_text=opt.option_text,
                    option_order=opt.option_order,
                )
                for opt in sorted(options, key=lambda x: x.option_order)
            ]
            questions_with_options.append(
                InitQuestionResponse(
                    question_id=question.question_id,
                    category=question.category,
                    question_text=question.question_text,
                    question_order=question.question_order,
                    version=question.version,
                    options=options_list,
                )
            )

        questions_with_options.sort(key=lambda x: x.question_order)
        return GetInitQuestionsResponse(
            questions=questions_with_options,
            version=version,
            total_questions=len(questions_with_options),
        )

    def submit_answers(
        self, request: SubmitInitAnswersRequest, dreamer_id: UUID
    ) -> InitAnswersSubmitResponse:
        dreamer_response = dreamer_gateway.get_dreamer(str(dreamer_id))
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(
                status_code=404,
                detail="このユーザーは dreamer として登録されていません",
            )

        saved_answers = []
        for answer_request in request.answers:
            question_response = dreamer_gateway.get_answer_question(
                str(answer_request.question_id)
            )
            if not question_response["success"] or not question_response["data"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"質問 {answer_request.question_id} が見つかりません",
                )

            option_response = dreamer_gateway.get_answer_option(
                str(answer_request.option_id)
            )
            if not option_response["success"] or not option_response["data"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"選択肢 {answer_request.option_id} が見つかりません",
                )

            save_response = dreamer_gateway.create_answer(
                {
                    "dreamer_id": str(dreamer_id),
                    "question_id": str(answer_request.question_id),
                    "option_id": str(answer_request.option_id),
                    "question_version": answer_request.question_version,
                    "answered_at": datetime.now(timezone.utc),
                }
            )
            self._ensure_success(save_response)

            saved = save_response["data"]
            saved_answers.append(
                InitAnswerResponse(
                    answer_id=saved.answer_id,
                    dreamer_id=saved.dreamer_id,
                    question_id=saved.question_id,
                    option_id=saved.option_id,
                    question_version=saved.question_version,
                    answered_at=(
                        saved.answered_at.isoformat() if saved.answered_at else ""
                    ),
                )
            )

        return InitAnswersSubmitResponse(
            total_saved=len(saved_answers), answers=saved_answers
        )

    def get_answer_history(self, dreamer_id: UUID) -> list[InitAnswerHistoryItem]:
        answers_response = dreamer_gateway.list_answer_history(str(dreamer_id))
        self._ensure_success(answers_response)

        result = []
        for answer in answers_response["data"] or []:
            question_response = dreamer_gateway.get_answer_question(
                str(answer.question_id)
            )
            option_response = dreamer_gateway.get_answer_option(str(answer.option_id))

            question_text = (
                question_response["data"][0].question_text
                if question_response["success"] and question_response["data"]
                else ""
            )
            option_text = (
                option_response["data"][0].option_text
                if option_response["success"] and option_response["data"]
                else ""
            )

            result.append(
                InitAnswerHistoryItem(
                    answer_id=answer.answer_id,
                    question_id=answer.question_id,
                    question_text=question_text,
                    option_id=answer.option_id,
                    option_text=option_text,
                    question_version=answer.question_version,
                    answered_at=(
                        answer.answered_at.isoformat() if answer.answered_at else ""
                    ),
                )
            )
        return result

    def _ensure_success(self, response: dict) -> None:
        if response["success"]:
            return
        message = response.get("message", "gateway error")
        if isinstance(message, list):
            message = ", ".join(message)
        raise HTTPException(status_code=500, detail=message)


onboarding_service = OnboardingService()
