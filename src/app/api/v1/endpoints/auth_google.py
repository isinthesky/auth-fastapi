import jwt
import requests
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone, timedelta
from src.app.api.v1.dependencies.user import get_user_service
from src.app.api.v1.schemas.response import create_response, create_error_response
from src.app.api.v1.schemas.common import Response
from src.app.core.services.user_service import UserService
from src.settings.environment import GoogleEnvironment,SecretKeyEnvironment
from urllib.parse import urlencode
from icecream import ic

auth_google_router = APIRouter(prefix="/api/v1/auth/google", tags=["auth"])

GOOGLE_CLIENT_ID = GoogleEnvironment.GOOGLE_CLIENT_ID.value
GOOGLE_CLIENT_SECRET = GoogleEnvironment.GOOGLE_CLIENT_SECRET.value
GOOGLE_REDIRECT_URI = GoogleEnvironment.GOOGLE_REDIRECT_URI.value
FRONTEND_REDIRECT_URL = GoogleEnvironment.FRONTEND_REDIRECT_URL.value

@auth_google_router.get("/login")
def google_login():
    """
    1) 프론트엔드가 이 엔드포인트로 접근하면,
       - 백엔드가 구글 OAuth 승인 URL 생성
       - 곧바로 구글로 Redirect
    """
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": "kr",  # 임의의 state (CSRF 방지용)
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url=google_auth_url)


@auth_google_router.get("/callback")
async def google_callback(code: str, state: str, user_service: UserService = Depends(get_user_service)):
    """
    2) 구글이 여기로 Authorization Code를 전달해줌.
       - code -> access_token (Google) 교환
       - userinfo 획득 -> DB 처리 (생략 or 구현)
       - JWT access token 생성 후 쿠키에 저장
       - 프론트엔드로 리다이렉트
    """
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No code provided")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not set")

    # -- (1) code -> access_token, id_token 교환 --
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_res = requests.post(token_url, data=data)
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange token with Google")
    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access_token in token response")

    # -- (2) 구글 사용자 정보 조회 --
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_res = requests.get(userinfo_url, headers=headers)
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    userinfo = userinfo_res.json()

    google_id = userinfo.get("id")
    email = userinfo.get("email")
    name = userinfo.get("name", "")

    # -- (3) 내부 DB에서 사용자 조회/생성 --
    user = await user_service.get_user_by_email(email)

    ic("get_user_by_email", user)

    if not user:
        # 새로운 유저 생성 (name, email)
        user = await user_service.create_user(
            name=name, 
            email=email
        )
        # 구글 소셜 계정 정보를 추가
        user = await user_service.add_social_account(
            user_id=user.user_id, 
            provider="google", 
            provider_id=google_id
        )
    else:
        # 이미 존재하는 유저인데, 구글 계정이 없다면 추가
        if not await user_service.has_social_account(user.user_id, "google"):
            user = await user_service.add_social_account(
                user_id=user.user_id,
                provider="google",
                provider_id=google_id
            )

    ic("social_account", user)
            
    # -- (4) JWT Access Token 발급 --
    #     - 유효기간 30분 예시
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub": google_id,
        "email": email,
        "name": name,
        "exp": expire,
    }
    jwt_access_token = jwt.encode(payload, SecretKeyEnvironment.get_secret_key(), algorithm=SecretKeyEnvironment.get_algorithm())

    # -- (5) JWT를 Cookie에 셋팅 후, 프론트엔드로 리다이렉트 --
    redirect_resp = RedirectResponse(url=FRONTEND_REDIRECT_URL, status_code=302)
    redirect_resp.set_cookie(
        key="access_token",
        value=jwt_access_token,
        httponly=True,   # JS에서 접근 불가
        secure=False,    # HTTPS가 아닌 환경 테스트 시 False (실서버에서는 True 권장)
        samesite="lax",
        max_age=1800,    # 30분(1800초)
    )

    return redirect_resp



@auth_google_router.get("/verify")
def verify_cookie(request: Request):
    """
    사용자의 쿠키에 있는 'access_token'이 유효한지 확인하는 엔드포인트
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No access token cookie found")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    # 토큰이 유효하면 payload 내부 정보를 반환(예시)
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "exp": payload.get("exp")
    }


@auth_google_router.get("/logout")
def logout():
    """
    쿠키를 삭제하여 로그아웃 처리
    """
    redirect_resp = RedirectResponse(url=FRONTEND_REDIRECT_URL, status_code=302)
    redirect_resp.delete_cookie(key="access_token")
    return redirect_resp