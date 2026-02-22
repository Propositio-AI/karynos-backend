"""
認証関連のユーティリティ

将来的にAmazon Cognitoでの認証を実装する予定
現在は開発用の固定UUIDを返す
"""
from uuid import UUID
from typing import Optional
from fastapi import Header, HTTPException, Depends

# 開発用の固定ユーザーID
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> UUID:
    """
    現在のユーザーIDを取得する（FastAPI Dependency）
    
    将来的な実装:
    - authorizationヘッダーからBearerトークンを取得
    - Amazon Cognitoでトークンを検証
    - 検証されたユーザーIDを返す
    
    現在の実装:
    - 固定のUUID(00000000-0000-0000-0000-000000000001)を返す
    
    Args:
        authorization: Authorizationヘッダー（将来的に使用）
    
    Returns:
        UUID: ユーザーID
    
    Raises:
        HTTPException: 認証に失敗した場合（将来的に実装）
    """
    # TODO: Amazon Cognito認証の実装
    # if authorization:
    #     try:
    #         # Bearer トークンを取得
    #         scheme, token = authorization.split()
    #         if scheme.lower() != 'bearer':
    #             raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    #         
    #         # Cognitoでトークンを検証
    #         user_id = verify_cognito_token(token)
    #         return UUID(user_id)
    #     except Exception as e:
    #         raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # 開発用：固定UUIDを返す
    return DEFAULT_USER_ID


def get_current_user_id_str(
    user_id: UUID = Depends(get_current_user_id)
) -> str:
    """
    現在のユーザーIDを文字列形式で取得する
    
    Args:
        user_id: get_current_user_idから取得したUUID
    
    Returns:
        str: ユーザーIDの文字列表現
    """
    return str(user_id)


def get_default_user_id() -> str:
    """
    デフォルトのユーザーIDを文字列形式で取得する
    
    WebSocketなど、Dependsが使用できない場所で使用する
    
    Returns:
        str: デフォルトユーザーIDの文字列表現
    """
    return str(DEFAULT_USER_ID)
