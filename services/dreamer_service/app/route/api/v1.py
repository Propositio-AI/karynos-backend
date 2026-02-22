from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from datetime import datetime

from crud import (dreamer_crud, dreamer_group_crud, dreamer_group_members_crud,
                  init_question_crud, init_question_option_crud, user_initial_answer_crud)
from schemas import (NewDreamerRequest, NewDreamerResponse, UpdateDreamerRequest,
                     DreamerResponse, NewDreamerGroupRequest, NewDreamerGroupResponse, 
                     DreamerGroupResponse, UpdateDreamerGroupRequest, DreamerToGroupRequest, 
                     DreamerToGroupResponse,DreamerInGroup,DreamerGroupSummary,
                     GetInitQuestionsResponse, InitQuestionResponse, InitQuestionOptionResponse,
                     SubmitInitAnswersRequest, InitAnswersSubmitResponse, InitAnswerResponse,
                     UserInitialAnswerHistoryResponse)
from shared.utils.security import random_string
from shared.lib.API import Client
from shared.lib.auth import get_current_user_id
from models.DreamerTable import DreamerTableSchema
from models.DreamerGroupTable import DreamerGroupTableSchema
from models.DreamerGroupMembersTable import DreamerGroupMembersTableSchema
from models.UserInitialAnswerTable import UserInitialAnswerTableSchema


# /api/v1/dreamer
router = APIRouter()

# ================
# Dreamer Admin
# ================

@router.post("/admin/new", response_model=NewDreamerResponse)
async def create_dreamer(request: NewDreamerRequest):
    """新しいアカウントの作成"""
    # organizationが存在するか事前チェック（存在しないIDでの登録を防止）
    client = Client()
    org_url = f"http://organization-service:8000/api/v1/organization/{request.organization_id}"
    org_response = client.get(org_url)
    if not org_response["success"]:
        raise HTTPException(status_code=400, detail="organization_id が存在しません")

    create_response = dreamer_crud.create(DreamerTableSchema(**request.model_dump(), login_id = random_string()))
    if not create_response["success"]:
        raise HTTPException(status_code=500, detail=create_response["message"])
    return NewDreamerResponse.model_validate(create_response["data"])


@router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
async def get_dreamer(dreamer_id: str):
    """dreamer情報の取得"""
    dreamer_response = dreamer_crud.read(
        [
            ["dreamer_id", "==", dreamer_id]
        ] 
    )
    if not dreamer_response["success"] or not dreamer_response["data"]:
        raise HTTPException(status_code=404, detail="dreamer が見つかりません")
    dreamer = dreamer_response["data"][0]
    
    # dreamerが所属するグループを取得
    members_response = dreamer_group_members_crud.read(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    if not members_response["success"]:
        raise HTTPException(status_code=500, detail=members_response["message"])
    members = members_response["data"]
    
    # グループ情報を取得
    groups = []
    if members:
        for member in members:
            group_response = dreamer_group_crud.read(
                [
                    ["group_id", "==", member.group_id]
                ]
            )
            if group_response["success"] and group_response["data"]:
                group = group_response["data"][0]
                groups.append(DreamerGroupSummary(name=group.name, group_id=group.group_id))
    
    return DreamerResponse(
        login_id=dreamer.login_id,
        organization_id=dreamer.organization_id,
        name_family=dreamer.name_family,
        name_given=dreamer.name_given,
        groups=groups
    )


@router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
async def update_dreamer(dreamer_id: str, request: UpdateDreamerRequest):
    """dreamer情報の更新"""
    update_response = dreamer_crud.update(
        [
            ["dreamer_id", "==", dreamer_id]
        ], 
    request.model_dump(exclude_unset=True)
    )
    if not update_response["success"] or not update_response["data"]:
        raise HTTPException(status_code=500, detail=update_response["message"])
    return DreamerResponse.model_validate(update_response["data"][0])


@router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
async def delete_dreamer(dreamer_id: str):
    """dreamer情報の削除"""
    # 所属している全グループから削除
    delete_members_response = dreamer_group_members_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    if not delete_members_response["success"]:
        raise HTTPException(status_code=500, detail=delete_members_response["message"])
    
    # dreamerを削除
    delete_response = dreamer_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    if not delete_response["success"] or not delete_response["data"]:
        raise HTTPException(status_code=404, detail="dreamer が見つかりません")
    return DreamerResponse.model_validate(delete_response["data"][0])

# ================
# Dreamer Groups
# ================

@router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(request: NewDreamerGroupRequest):
    """新しいグループの作成"""
    # メンバーに指定された dreamer_id を事前に全件確認（存在しなければ 400）
    for dreamer_id in request.dreamers:
        dreamer_response = dreamer_crud.read(
            [["dreamer_id", "==", dreamer_id]]
        )
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

    group_data = request.model_dump(exclude={"dreamers"})
    group_instance = DreamerGroupTableSchema(**group_data)

    group_response = dreamer_group_crud.create(group_instance)
    if not group_response["success"]:
        raise HTTPException(status_code=500, detail=group_response["message"])
    group_result = group_response["data"]
    group_id = group_result.group_id

    # メンバー登録
    added_dreamers = []
    for dreamer_id in request.dreamers:
        member_instance = DreamerGroupMembersTableSchema(
            group_id=group_id,
            dreamer_id=dreamer_id
        )
        member_response = dreamer_group_members_crud.create(member_instance)
        if not member_response["success"]:
            raise HTTPException(status_code=500, detail=member_response["message"])
        added_dreamers.append(member_response["data"])

    return NewDreamerGroupResponse.model_validate(group_result)


@router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
async def get_group(group_id: str):
    """グループ情報の取得"""
    group_response = dreamer_group_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not group_response["success"] or not group_response["data"]:
        raise HTTPException(status_code=404, detail="group が見つかりません")

    group = group_response["data"][0]
    members_response = dreamer_group_members_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not members_response["success"]:
        raise HTTPException(status_code=500, detail=members_response["message"])
    members = members_response["data"]
    
    # 各メンバーのdreamer情報を取得
    dreamers = []
    if members:
        for member in members:
            dreamer_response = dreamer_crud.read(
                [
                    ["dreamer_id", "==", member.dreamer_id]
                ]
            )
            if dreamer_response["success"] and dreamer_response["data"]:
                dreamer = dreamer_response["data"][0]
                full_name = f"{dreamer.name_family} {dreamer.name_given}"
                dreamers.append(DreamerInGroup(name=full_name, dreamer_id=dreamer.dreamer_id))
        
    return DreamerGroupResponse(
        name=group.name,
        description=group.description,
        dreamers=dreamers
    )


@router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
async def update_group(group_id: str, request: UpdateDreamerGroupRequest):
    """グループ情報の更新"""
    update_response = dreamer_group_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    if not update_response["success"] or not update_response["data"]:
        raise HTTPException(status_code=500, detail=update_response["message"])
    return DreamerGroupResponse.model_validate(update_response["data"][0])


@router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
async def delete_group(group_id: str):
    """グループを削除"""
    # グループのメンバーを全て削除
    delete_members_response = dreamer_group_members_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not delete_members_response["success"]:
        raise HTTPException(status_code=500, detail=delete_members_response["message"])
    
    # グループを削除
    delete_response = dreamer_group_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not delete_response["success"] or not delete_response["data"]:
        raise HTTPException(status_code=500, detail=delete_response["message"])
    return DreamerGroupResponse.model_validate(delete_response["data"][0])

#================
# Dreamer Group Members
#================

@router.put("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
async def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
    """グループにdreamerを追加"""
    # グループの存在確認
    group_response = dreamer_group_crud.read(
        [["group_id", "==", group_id]]
    )
    if not group_response["success"] or not group_response["data"]:
        raise HTTPException(status_code=404, detail="group が見つかりません")

    # 追加対象 dreamer_id を事前に全件確認（外部キー違反防止）
    for dreamer_id in request.dreamers:
        dreamer_response = dreamer_crud.read(
            [["dreamer_id", "==", dreamer_id]]
        )
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

    added_dreamers = []

    for dreamer_id in request.dreamers:
        member_instance = DreamerGroupMembersTableSchema(
            group_id=group_id,
            dreamer_id=dreamer_id
        )
        member_response = dreamer_group_members_crud.create(member_instance)
        if not member_response["success"]:
            raise HTTPException(status_code=500, detail=member_response["message"])
        added_dreamers.append(member_response["data"])

    dreamer_ids = [member.dreamer_id for member in added_dreamers]
    return DreamerToGroupResponse.model_validate({"dreamers": dreamer_ids})


@router.delete("/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse)
async def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
    """グループからdreamerを削除"""
    deleted_ids = []

    for dreamer_id in request.dreamers:
        delete_response = dreamer_group_members_crud.delete(
            [
                ["group_id", "==", group_id],
                ["dreamer_id", "==", dreamer_id]
            ]
        )
        if delete_response["success"] and delete_response["data"]:
            deleted_ids.append(dreamer_id)
    return DreamerToGroupResponse.model_validate({"dreamers": deleted_ids})


# ================
# 初期診断質問 API
# ================

@router.get("/init-questions", response_model=GetInitQuestionsResponse)
async def get_init_questions(version: int = 1):
    """
    初期診断質問を取得（選択肢を含む）
    
    Args:
        version: 質問セットのバージョン（デフォルト: 1）
    
    Returns:
        全5問の質問と選択肢
    """
    try:
        # 指定されたバージョンで有効な質問を全て取得
        questions_response = init_question_crud.read(
            [
                ["version", "==", version],
                ["is_active", "==", True]
            ]
        )
        
        if not questions_response["success"]:
            raise HTTPException(status_code=500, detail=questions_response["message"])
        
        questions_data = questions_response["data"]
        if not questions_data:
            raise HTTPException(status_code=404, detail=f"バージョン {version} の質問が見つかりません")
        
        # 各質問に対する選択肢を取得
        questions_with_options = []
        for question in questions_data:
            options_response = init_question_option_crud.read(
                [
                    ["question_id", "==", question.question_id]
                ]
            )
            
            if not options_response["success"]:
                raise HTTPException(status_code=500, detail=options_response["message"])
            
            options = options_response["data"] or []
            options_list = [
                InitQuestionOptionResponse(
                    option_id=opt.option_id,
                    option_text=opt.option_text,
                    option_order=opt.option_order
                )
                for opt in sorted(options, key=lambda x: x.option_order)
            ]
            
            question_resp = InitQuestionResponse(
                question_id=question.question_id,
                category=question.category,
                question_text=question.question_text,
                question_order=question.question_order,
                version=question.version,
                options=options_list
            )
            questions_with_options.append(question_resp)
        
        # 表示順でソート
        questions_with_options.sort(key=lambda x: x.question_order)
        
        return GetInitQuestionsResponse(
            questions=questions_with_options,
            version=version,
            total_questions=len(questions_with_options)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init-answers", response_model=InitAnswersSubmitResponse)
async def submit_init_answers(
    request: SubmitInitAnswersRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    ユーザーの初期診断回答を保存
    
    Args:
        request: 複数の回答データ
        user_id: 認証から取得したユーザーID
    
    Returns:
        保存された回答の一覧
    """
    try:
        # ユーザーが dreamer として存在するか確認
        dreamer_response = dreamer_crud.read(
            [["dreamer_id", "==", str(user_id)]]
        )
        
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=404, detail="このユーザーは dreamer として登録されていません")
        
        saved_answers = []
        
        for answer_request in request.answers:
            # 質問と選択肢が存在するか確認
            question_response = init_question_crud.read(
                [["question_id", "==", str(answer_request.question_id)]]
            )
            
            if not question_response["success"] or not question_response["data"]:
                raise HTTPException(status_code=400, detail=f"質問 {answer_request.question_id} が見つかりません")
            
            option_response = init_question_option_crud.read(
                [["option_id", "==", str(answer_request.option_id)]]
            )
            
            if not option_response["success"] or not option_response["data"]:
                raise HTTPException(status_code=400, detail=f"選択肢 {answer_request.option_id} が見つかりません")
            
            # 回答を保存
            answer_schema = UserInitialAnswerTableSchema(
                dreamer_id=user_id,
                question_id=answer_request.question_id,
                option_id=answer_request.option_id,
                question_version=answer_request.question_version,
                answered_at=datetime.now()
            )
            
            save_response = user_initial_answer_crud.create(answer_schema)
            
            if not save_response["success"]:
                raise HTTPException(status_code=500, detail=save_response["message"])
            
            saved_answer = save_response["data"]
            response_obj = InitAnswerResponse(
                answer_id=saved_answer.answer_id,
                dreamer_id=saved_answer.dreamer_id,
                question_id=saved_answer.question_id,
                option_id=saved_answer.option_id,
                question_version=saved_answer.question_version,
                answered_at=saved_answer.answered_at.isoformat() if saved_answer.answered_at else ""
            )
            saved_answers.append(response_obj)
        
        return InitAnswersSubmitResponse(
            total_saved=len(saved_answers),
            answers=saved_answers
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/init-answers/history", response_model=list[UserInitialAnswerHistoryResponse])
async def get_init_answers_history(
    user_id: UUID = Depends(get_current_user_id)
):
    """
    ユーザーの初期診断回答履歴を取得
    
    Args:
        user_id: 認証から取得したユーザーID
    
    Returns:
        ユーザーの全ての初期診断回答
    """
    try:
        # ユーザーが dreamer として存在するか確認
        dreamer_response = dreamer_crud.read(
            [["dreamer_id", "==", str(user_id)]]
        )
        
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=404, detail="このユーザーは dreamer として登録されていません")
        
        # ユーザーの全ての回答を取得
        answers_response = user_initial_answer_crud.read(
            [["dreamer_id", "==", str(user_id)]]
        )
        
        if not answers_response["success"]:
            raise HTTPException(status_code=500, detail=answers_response["message"])
        
        answers_data = answers_response["data"] or []
        
        result = []
        for answer in answers_data:
            # 質問文を取得
            question_response = init_question_crud.read(
                [["question_id", "==", str(answer.question_id)]]
            )
            
            question_text = ""
            if question_response["success"] and question_response["data"]:
                question_text = question_response["data"][0].question_text
            
            # 選択肢テキストを取得
            option_response = init_question_option_crud.read(
                [["option_id", "==", str(answer.option_id)]]
            )
            
            option_text = ""
            if option_response["success"] and option_response["data"]:
                option_text = option_response["data"][0].option_text
            
            history_item = UserInitialAnswerHistoryResponse(
                answer_id=answer.answer_id,
                question_id=answer.question_id,
                question_text=question_text,
                option_id=answer.option_id,
                option_text=option_text,
                question_version=answer.question_version,
                answered_at=answer.answered_at.isoformat() if answer.answered_at else ""
            )
            result.append(history_item)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))