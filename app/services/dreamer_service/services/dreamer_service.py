from datetime import datetime

from fastapi import HTTPException

from app.gateways import dreamer_gateway
from app.services.dreamer_service.schemas import (
    DreamerGroupResponse,
    DreamerGroupSummary,
    DreamerInGroup,
    DreamerResponse,
    DreamerToGroupRequest,
    DreamerToGroupResponse,
    GetInitQuestionsResponse,
    InitAnswerResponse,
    InitAnswersSubmitResponse,
    InitQuestionOptionResponse,
    InitQuestionResponse,
    NewDreamerGroupRequest,
    NewDreamerGroupResponse,
    NewDreamerRequest,
    NewDreamerResponse,
    SubmitInitAnswersRequest,
    UpdateDreamerGroupRequest,
    UpdateDreamerRequest,
    UserInitialAnswerHistoryResponse,
)
from app.utils.security import random_string


class DreamerService:
    def create_dreamer(self, request: NewDreamerRequest):
        create_response = dreamer_gateway.create_dreamer(
            {
                "organization_id": request.organization_id,
                "name_family": request.name_family,
                "name_given": request.name_given,
                "login_id": random_string(),
            }
        )
        self._ensure_success(create_response)
        return NewDreamerResponse.model_validate(create_response["data"])

    def get_dreamer(self, dreamer_id: str):
        dreamer_response = dreamer_gateway.get_dreamer(dreamer_id)
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")

        dreamer = dreamer_response["data"][0]
        members_response = dreamer_gateway.list_members_by_dreamer(dreamer_id)
        self._ensure_success(members_response)

        groups = []
        for member in members_response["data"]:
            group_response = dreamer_gateway.get_group(member.group_id)
            if group_response["success"] and group_response["data"]:
                group = group_response["data"][0]
                groups.append(DreamerGroupSummary(name=group.name, group_id=group.group_id))

        return DreamerResponse(
            login_id=dreamer.login_id,
            organization_id=dreamer.organization_id,
            name_family=dreamer.name_family,
            name_given=dreamer.name_given,
            groups=groups,
        )

    def update_dreamer(self, dreamer_id: str, request: UpdateDreamerRequest):
        response = dreamer_gateway.update_dreamer(dreamer_id, request.model_dump(exclude_unset=True))
        if not response["success"]:
            raise HTTPException(status_code=500, detail=self._message(response))
        if not response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")
        return DreamerResponse.model_validate(response["data"][0])

    def delete_dreamer(self, dreamer_id: str):
        delete_members_response = dreamer_gateway.delete_members_by_dreamer(dreamer_id)
        self._ensure_success(delete_members_response)

        delete_response = dreamer_gateway.delete_dreamer(dreamer_id)
        if not delete_response["success"] or not delete_response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")
        return DreamerResponse.model_validate(delete_response["data"][0])

    def create_group(self, request: NewDreamerGroupRequest):
        for dreamer_id in request.dreamers:
            dreamer_response = dreamer_gateway.get_dreamer(str(dreamer_id))
            if not dreamer_response["success"] or not dreamer_response["data"]:
                raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

        group_response = dreamer_gateway.create_group(
            {
                "name": request.name,
                "description": request.description,
            }
        )
        self._ensure_success(group_response)
        group_result = group_response["data"]

        for dreamer_id in request.dreamers:
            member_response = dreamer_gateway.create_group_member(
                {
                    "group_id": str(group_result.group_id),
                    "dreamer_id": str(dreamer_id),
                }
            )
            self._ensure_success(member_response)

        return NewDreamerGroupResponse.model_validate(group_result)

    def get_group(self, group_id: str):
        group_response = dreamer_gateway.get_group(group_id)
        if not group_response["success"] or not group_response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")

        group = group_response["data"][0]
        members_response = dreamer_gateway.list_members_by_group(group_id)
        self._ensure_success(members_response)

        dreamers = []
        for member in members_response["data"]:
            dreamer_response = dreamer_gateway.get_dreamer(member.dreamer_id)
            if dreamer_response["success"] and dreamer_response["data"]:
                dreamer = dreamer_response["data"][0]
                dreamers.append(
                    DreamerInGroup(name=f"{dreamer.name_family} {dreamer.name_given}", dreamer_id=dreamer.dreamer_id)
                )

        return DreamerGroupResponse(name=group.name, description=group.description, dreamers=dreamers)

    def update_group(self, group_id: str, request: UpdateDreamerGroupRequest):
        response = dreamer_gateway.update_group(group_id, request.model_dump(exclude_unset=True))
        if not response["success"]:
            raise HTTPException(status_code=500, detail=self._message(response))
        if not response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")
        return DreamerGroupResponse.model_validate(response["data"][0])

    def delete_group(self, group_id: str):
        delete_members_response = dreamer_gateway.delete_members_by_group(group_id)
        self._ensure_success(delete_members_response)

        delete_response = dreamer_gateway.delete_group(group_id)
        if not delete_response["success"]:
            raise HTTPException(status_code=500, detail=self._message(delete_response))
        if not delete_response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")
        return DreamerGroupResponse.model_validate(delete_response["data"][0])

    def add_dreamer_to_group(self, group_id: str, request: DreamerToGroupRequest):
        added_dreamers = []
        for dreamer_id in request.dreamers:
            member_response = dreamer_gateway.create_group_member(
                {
                    "group_id": str(group_id),
                    "dreamer_id": str(dreamer_id),
                }
            )
            self._ensure_success(member_response)
            added_dreamers.append(member_response["data"])

        return DreamerToGroupResponse.model_validate(
            {"dreamers": [member.dreamer_id for member in added_dreamers]}
        )

    def remove_dreamer_from_group(self, group_id: str, request: DreamerToGroupRequest):
        deleted_ids = []
        for dreamer_id in request.dreamers:
            delete_response = dreamer_gateway.delete_group_member(group_id, str(dreamer_id))
            if delete_response["success"] and delete_response["data"]:
                deleted_ids.append(dreamer_id)
        return DreamerToGroupResponse.model_validate({"dreamers": deleted_ids})

    def get_init_questions(self, version: int = 1):
        questions_response = dreamer_gateway.list_init_questions(version)
        self._ensure_success(questions_response)
        questions_data = questions_response["data"]
        if not questions_data:
            raise HTTPException(status_code=404, detail=f"バージョン {version} の質問が見つかりません")

        questions_with_options = []
        for question in questions_data:
            options_response = dreamer_gateway.list_question_options(question.question_id)
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

    def submit_init_answers(self, request: SubmitInitAnswersRequest, user_id):
        dreamer_response = dreamer_gateway.get_dreamer(str(user_id))
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=404, detail="このユーザーは dreamer として登録されていません")

        saved_answers = []
        for answer_request in request.answers:
            question_response = dreamer_gateway.get_answer_question(str(answer_request.question_id))
            if not question_response["success"] or not question_response["data"]:
                raise HTTPException(status_code=400, detail=f"質問 {answer_request.question_id} が見つかりません")

            option_response = dreamer_gateway.get_answer_option(str(answer_request.option_id))
            if not option_response["success"] or not option_response["data"]:
                raise HTTPException(status_code=400, detail=f"選択肢 {answer_request.option_id} が見つかりません")

            save_response = dreamer_gateway.create_answer(
                {
                    "dreamer_id": str(user_id),
                    "question_id": str(answer_request.question_id),
                    "option_id": str(answer_request.option_id),
                    "question_version": answer_request.question_version,
                    "answered_at": datetime.now(),
                }
            )
            self._ensure_success(save_response)

            saved_answer = save_response["data"]
            saved_answers.append(
                InitAnswerResponse(
                    answer_id=saved_answer.answer_id,
                    dreamer_id=saved_answer.dreamer_id,
                    question_id=saved_answer.question_id,
                    option_id=saved_answer.option_id,
                    question_version=saved_answer.question_version,
                    answered_at=saved_answer.answered_at.isoformat() if saved_answer.answered_at else "",
                )
            )

        return InitAnswersSubmitResponse(total_saved=len(saved_answers), answers=saved_answers)

    def get_init_answers_history(self, user_id):
        answers_response = dreamer_gateway.list_answer_history(str(user_id))
        self._ensure_success(answers_response)

        result = []
        for answer in answers_response["data"] or []:
            question_response = dreamer_gateway.get_answer_question(str(answer.question_id))
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
                UserInitialAnswerHistoryResponse(
                    answer_id=answer.answer_id,
                    question_id=answer.question_id,
                    question_text=question_text,
                    option_id=answer.option_id,
                    option_text=option_text,
                    question_version=answer.question_version,
                    answered_at=answer.answered_at.isoformat() if answer.answered_at else "",
                )
            )
        return result

    def _ensure_success(self, response: dict):
        if response["success"]:
            return
        raise HTTPException(status_code=500, detail=self._message(response))

    def _message(self, response: dict):
        message = response.get("message", "gateway error")
        if isinstance(message, list):
            return ", ".join(message)
        return message


dreamer_service = DreamerService()
