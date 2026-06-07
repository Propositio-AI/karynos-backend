from typing import Any

from app.gateways.db.base_prisma_gateway import BasePrismaGateway
from app.gateways.result import GatewayResult
from app.gen.prisma import types as prisma_types
from app.gen.prisma.models import (
    Dreamer,
    DreamerGroup,
    DreamerGroupMember,
    InitQuestion,
    InitQuestionOption,
    UserInitialAnswer,
)


class DreamerGateway(BasePrismaGateway):
    DREAMER = "dreamer"
    GROUP = "dreamergroup"
    MEMBER = "dreamergroupmember"
    INIT_QUESTION = "initquestion"
    INIT_OPTION = "initquestionoption"
    INIT_ANSWER = "userinitialanswer"

    def create_dreamer(self, payload: prisma_types.DreamerCreateInput | dict[str, Any]) -> GatewayResult[Dreamer]:
        return self.create(self.DREAMER, payload)

    def get_dreamer(self, dreamer_id: str) -> GatewayResult[list[Dreamer]]:
        return self.find_many(self.DREAMER, {"dreamer_id": str(dreamer_id)})

    def update_dreamer(
        self,
        dreamer_id: str,
        payload: prisma_types.DreamerUpdateInput | dict[str, Any],
    ) -> GatewayResult[list[Dreamer]]:
        return self.update_many_and_fetch(self.DREAMER, {"dreamer_id": str(dreamer_id)}, payload)

    def delete_dreamer(self, dreamer_id: str) -> GatewayResult[list[Dreamer]]:
        return self.delete_many_and_return_before(self.DREAMER, {"dreamer_id": str(dreamer_id)})

    def create_group(self, payload: prisma_types.DreamerGroupCreateInput | dict[str, Any]) -> GatewayResult[DreamerGroup]:
        return self.create(self.GROUP, payload)

    def get_group(self, group_id: str) -> GatewayResult[list[DreamerGroup]]:
        return self.find_many(self.GROUP, {"group_id": str(group_id)})

    def update_group(
        self,
        group_id: str,
        payload: prisma_types.DreamerGroupUpdateInput | dict[str, Any],
    ) -> GatewayResult[list[DreamerGroup]]:
        return self.update_many_and_fetch(self.GROUP, {"group_id": str(group_id)}, payload)

    def delete_group(self, group_id: str) -> GatewayResult[list[DreamerGroup]]:
        return self.delete_many_and_return_before(self.GROUP, {"group_id": str(group_id)})

    def list_members_by_dreamer(self, dreamer_id: str) -> GatewayResult[list[DreamerGroupMember]]:
        return self.find_many(self.MEMBER, {"dreamer_id": str(dreamer_id)})

    def list_members_by_group(self, group_id: str) -> GatewayResult[list[DreamerGroupMember]]:
        return self.find_many(self.MEMBER, {"group_id": str(group_id)})

    def create_group_member(
        self,
        payload: prisma_types.DreamerGroupMemberCreateInput | dict[str, Any],
    ) -> GatewayResult[DreamerGroupMember]:
        return self.create(self.MEMBER, payload)

    def delete_members_by_dreamer(self, dreamer_id: str) -> GatewayResult[list[DreamerGroupMember]]:
        return self.delete_many_and_return_before(self.MEMBER, {"dreamer_id": str(dreamer_id)})

    def delete_members_by_group(self, group_id: str) -> GatewayResult[list[DreamerGroupMember]]:
        return self.delete_many_and_return_before(self.MEMBER, {"group_id": str(group_id)})

    def delete_group_member(self, group_id: str, dreamer_id: str) -> GatewayResult[list[DreamerGroupMember]]:
        return self.delete_many_and_return_before(
            self.MEMBER,
            {"group_id": str(group_id), "dreamer_id": str(dreamer_id)},
        )

    def list_init_questions(self, version: int) -> GatewayResult[list[InitQuestion]]:
        return self.find_many(self.INIT_QUESTION, {"version": int(version), "is_active": True})

    def list_question_options(self, question_id: str) -> GatewayResult[list[InitQuestionOption]]:
        return self.find_many(self.INIT_OPTION, {"question_id": str(question_id)})

    def list_answer_history(self, dreamer_id: str) -> GatewayResult[list[UserInitialAnswer]]:
        return self.find_many(self.INIT_ANSWER, {"dreamer_id": str(dreamer_id)})

    def create_answer(
        self,
        payload: prisma_types.UserInitialAnswerCreateInput | dict[str, Any],
    ) -> GatewayResult[UserInitialAnswer]:
        return self.create(self.INIT_ANSWER, payload)

    def get_answer_question(self, question_id: str) -> GatewayResult[list[InitQuestion]]:
        return self.find_many(self.INIT_QUESTION, {"question_id": str(question_id)})

    def get_answer_option(self, option_id: str) -> GatewayResult[list[InitQuestionOption]]:
        return self.find_many(self.INIT_OPTION, {"option_id": str(option_id)})


dreamer_gateway = DreamerGateway()
