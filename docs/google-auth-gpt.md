## 개요

현재 `test.myhome.com:8000`에 호스팅된 FastAPI 백엔드와 `test.myhome.com:8002`에 호스팅된 React 프론트엔드 사이에서 Google OAuth 인증을 설정하려고 하십니다. 이를 위해 제공된 백엔드 및 프론트엔드 코드와 API 함수를 분석하여 다음 사항을 검토하고자 합니다:

1. **백엔드 API 함수 분석**
2. **프론트엔드 API 함수 분석**
3. **엔드포인트 및 URL 구성 검토**
4. **CORS 및 보안 고려사항**
5. **종합 가이드 및 권장 사항**

각 항목을 자세히 살펴보겠습니다.

---

## 1. 백엔드 API 함수 분석

백엔드 코드(`msa/auth-fastapi/src/app/api/v1/endpoints/auth.py`)는 FastAPI를 사용하여 Google OAuth 인증을 처리합니다. 주요 API 함수는 다음과 같습니다:

### **1.1. 로그인 (`/users/login`)**

```python:msa/auth-fastapi/src/app/api/v1/endpoints/auth.py
@user_router.post(
    path="/login", 
    response_model=LoginResponse,
    summary="유저 로그인",
    description="유저 로그인",
)
async def login(
    request: LoginRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    ...
```

- **목적:** 사용자가 이메일과 소셜 제공자를 통해 로그인할 수 있도록 지원합니다.
- **입력:** `LoginRequest` 스키마 객체 (이메일, 제공자, 소셜 ID)
- **출력:** `LoginResponse` 스키마 객체 (사용자 정보 및 로그인 상태)

### **1.2. Google OAuth URL 생성 (`/users/google/auth`)**

```python:msa/auth-fastapi/src/app/api/v1/endpoints/auth.py
@user_router.get(
    path="/google/auth",
    response_model=GoogleAuthResponse,
    summary="Google OAuth 인증 URL 생성",
    description="Google OAuth 인증을 위한 URL을 생성합니다.",
)
async def google_auth(
    request: Request,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    ...
```

- **목적:** 클라이언트에게 Google OAuth 인증을 위한 URL을 제공합니다.
- **입력:** HTTP GET 요청
- **출력:** `GoogleAuthResponse` 스키마 객체 (생성된 인증 URL)

### **1.3. Google OAuth 콜백 처리 (`/users/google/callback`)**

```python:msa/auth-fastapi/src/app/api/v1/endpoints/auth.py
@user_router.post(
    path="/google/callback",
    response_model=LoginResponse,
    summary="Google OAuth 콜백 처리",
    description="Google OAuth 인증 후 콜백을 처리하고 로그인을 수행합니다.",
)
async def google_callback(
    request: GoogleAuthRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    ...
```

- **목적:** Google OAuth 인증 후 반환된 `code`를 처리하여 사용자 로그인을 완료합니다.
- **입력:** `GoogleAuthRequest` 스키마 객체 (인증 코드, 리디렉션 URI)
- **출력:** `LoginResponse` 스키마 객체 (사용자 정보 및 로그인 상태)

### **1.4. 사용자 생성 및 정보 조회**

- **새로운 사용자 생성 (`POST /users/`):** `create_user` 함수는 새로운 사용자를 생성합니다.
- **사용자 정보 조회 (`GET /users/{user_id}`):** `get_user` 함수는 특정 사용자 ID로 사용자 정보를 조회합니다.
- **소셜 계정 추가 (`POST /users/{user_id}/social-accounts`):** `add_social_account` 함수는 사용자의 소셜 계정을 추가합니다.
- **사용자 상태 변경 (`PATCH /users/{user_id}/state`):** `change_user_state` 함수는 사용자의 상태를 변경합니다.

**주요 포인트:**

- 모든 함수는 `UserService` 또는 `AuthServicePort`를 의존성으로 주입받아 동작합니다.
- 예외 처리 및 로깅이 잘 구현되어 있어 디버깅 및 유지보수가 용이합니다.

---

## 2. 프론트엔드 API 함수 분석

프론트엔드 코드(`msa/test-react/src/features/user/requests.ts`)는 Axios를 사용하여 백엔드 API와 통신합니다. 주요 함수는 다음과 같습니다:

### **2.1. Google 코드로 토큰 교환 (`googleCodeForToken`)**

```typescript:msa/test-react/src/features/user/requests.ts
export const googleCodeForToken = async (uri: string, code: string, redirectUri: string) => {
  try {
    const axiosInst = axios.create({
      baseURL: ENV_BACKEND_BASE_URL,
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      withCredentials: true,
    });
    const response = await axiosInst.post(uri, {
      code,
      redirect_uri: redirectUri,
    });

    return response.data;
  } catch (error) {
    throw error;
  }
};
```

- **목적:** Google OAuth 인증 후 반환된 `code`를 백엔드로 전송하여 토큰을 교환합니다.
- **입력:** `uri` (백엔드 엔드포인트 URL), `code` (Google 인증 코드), `redirectUri` (리디렉션 URI)
- **출력:** 백엔드의 응답 데이터 (`LoginResponse`)

### **2.2. 사용자 ID 조회 (`getUserId`)**

```typescript:msa/test-react/src/features/user/requests.ts
export const getUserId = async (uri: string): Promise<string | null> => {
  try {
    const axiosInst = axios.create({
      baseURL: ENV_BACKEND_BASE_URL,
      withCredentials: true,
    });

    const response = await axiosInst.get(uri);

    if (response.data.code >= 400) {
      throw response;
    }

    return response.data.data;
  } catch {
    return null;
  }
};
```

- **목적:** 현재 로그인된 사용자의 ID를 조회합니다.
- **입력:** `uri` (백엔드 사용자 정보 조회 엔드포인트 URL)
- **출력:** 사용자 ID 문자열 또는 `null`

**주요 포인트:**

- Axios 인스턴스가 `ENV_BACKEND_BASE_URL`을 기반으로 생성되어 백엔드와의 통신을 설정합니다.
- 에러 처리 로직이 포함되어 있어, 요청 실패 시 `null`을 반환합니다.

---

## 3. 엔드포인트 및 URL 구성 검토

### **3.1. 리디렉션 URI 설정**

- **백엔드:** `msa/auth-fastapi/src/app/api/v1/endpoints/auth.py`에서 `google_auth` 함수는 다음과 같이 `redirect_uri`를 생성합니다.

  ```python:msa/auth-fastapi/src/app/api/v1/endpoints/auth.py
  auth_url = await auth_service.get_google_auth_url(
      redirect_uri=str(request.base_url) + "api/v1/users/google/callback"
  )
  ```

  - **생성된 `redirect_uri`:** `https://test.myhome.com:8000/api/v1/users/google/callback`

- **프론트엔드:** `msa/test-react/src/pages/login.tsx`에서 `GOOGLE_URL`은 다음과 같이 구성됩니다.

  ```typescript:msa/test-react/src/pages/login.tsx
  const GOOGLE_URL = `https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.googleapis.com/auth/userinfo.email+https://www.googleapis.com/auth/userinfo.profile&include_granted_scopes=true&response_type=code&redirect_uri=${ENV_GOOGLE_REDIRECT_URL}&client_id=${ENV_GOOGLE_CLIENT_ID}&state=kr`;
  ```

  - **문제점:**
    - `redirect_uri`가 프론트엔드의 콜백 페이지 (`test.myhome.com:8002`)로 설정될 경우, 백엔드와 프론트엔드 간의 OAuth 흐름이 분리되어 복잡해집니다.
    - 백엔드에서 전체 OAuth 흐름을 처리하도록 구성하는 것이 권장됩니다.

  - **권장 사항:**
    - `redirect_uri`를 백엔드의 콜백 엔드포인트 (`https://test.myhome.com:8000/api/v1/users/google/callback`)로 설정하여 OAuth 흐름을 백엔드가 일관되게 처리하도록 합니다.

### **3.2. API 엔드포인트 일치 여부**

- **백엔드 엔드포인트:**
  - `GET /api/v1/users/google/auth` → Google 인증 URL 생성
  - `POST /api/v1/users/google/callback` → Google 인증 후 콜백 처리

- **프론트엔드 호출:**
  - `googleCodeForToken` 함수는 현재 백엔드의 `/auth/google/login` 엔드포인트로 요청을 보내고 있습니다.
  
  - **문제점:**
    - 백엔드는 `/api/v1/users/google/callback`에서 콜백을 처리하도록 구성되어 있으나, 프론트엔드는 `/auth/google/login`으로 요청을 보내고 있어 엔드포인트가 일치하지 않습니다.

  - **해결 방안:**
    - 프론트엔드에서 `googleCodeForToken` 함수가 호출하는 URL을 백엔드의 콜백 엔드포인트로 수정해야 합니다.

  - **수정 예시:**

    ```typescript:msa/test-react/src/pages/google/callback.tsx
    const res = await googleCodeForToken(`${ENV_BACKEND_BASE_URL}/api/v1/users/google/callback`, code, ENV_GOOGLE_REDIRECT_URL || "");
    ```

### **3.3. 환경 변수 설정**

- **프론트엔드 환경 변수 (`msa/test-react/.env`):**

  ```env
  REACT_APP_ENV_BACKEND_BASE_URL=https://test.myhome.com:8000
  REACT_APP_ENV_GOOGLE_CLIENT_ID=your-google-client-id
  # REACT_APP_ENV_GOOGLE_REDIRECT_URL은 백엔드에서 처리하는 경우 생략 가능
  ```

- **백엔드 환경 변수 (`msa/auth-fastapi/.env`):**

  ```env
  BACKEND_URL=https://test.myhome.com:8000
  GOOGLE_CLIENT_ID=your-google-client-id
  GOOGLE_CLIENT_SECRET=your-google-client-secret
  REDIRECT_URI=https://test.myhome.com:8000/api/v1/users/google/callback
  ```

- **주요 포인트:**
  - 환경 변수가 배포 설정을 정확하게 반영하도록 설정되어야 합니다.
  - `redirect_uri`는 백엔드의 콜백 엔드포인트로 정확하게 설정되어야 합니다.
  - 프론트엔드에서 `ENV_GOOGLE_REDIRECT_URL`을 사용하지 않도록 구성하여 혼동을 방지합니다.

---

## 4. CORS 및 보안 고려사항

### **4.1. CORS 구성**

백엔드가 프론트엔드의 출처(`https://test.myhome.com:8002`)에서 오는 요청을 허용하도록 CORS를 설정해야 합니다.

```python:msa/auth-fastapi/src/app/main.py
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://test.myhome.com:8002",
    # 필요한 경우 다른 출처 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- **설정 설명:**
  - `allow_origins`에 프론트엔드의 URL을 추가하여 프론트엔드에서 백엔드로의 요청을 허용합니다.
  - `allow_credentials`를 `True`로 설정하여 쿠키와 같은 자격 증명 정보도 전송할 수 있도록 합니다.

### **4.2. 보안 고려사항**

- **HTTPS 사용:** 모든 통신이 HTTPS를 통해 안전하게 이루어지도록 설정해야 합니다.
- **HTTP-Only 쿠키:** 토큰과 같은 민감한 정보는 HTTP-Only 쿠키에 저장하여 XSS 공격을 방지합니다.
- **CSRF 방지:** 필요 시 CSRF 토큰을 사용하여 교차 사이트 요청 위조 공격을 방지합니다.
- **입력 검증:** 모든 입력 데이터는 서버에서 철저히 검증하여 SQL 인젝션 및 기타 공격을 방지합니다.

---

## 5. 종합 가이드 및 권장 사항

### **5.1. 프론트엔드 콜백 처리 수정**

프론트엔드의 콜백 페이지(`msa/test-react/src/pages/google/callback.tsx`)에서 `googleCodeForToken` 함수를 호출할 때, 백엔드의 콜백 엔드포인트로 요청하도록 수정합니다.

```typescript:msa/test-react/src/pages/google/callback.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { googleCodeForToken } from '@/features/user/requests';
import { ENV_BACKEND_BASE_URL } from '@/shared/config';

const GoogleCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (!code) {
      navigate('/login');
      return;
    }

    const exchangeCode = async () => {
      try {
        const res = await googleCodeForToken(
          `${ENV_BACKEND_BASE_URL}/api/v1/users/google/callback`,
          code,
          // ENV_GOOGLE_REDIRECT_URL는 백엔드가 처리하므로 필요 없음
        );

        if (res.error) {
          throw new Error(res.error);
        }

        navigate('/'); // 인증 성공 후 홈 또는 대시보드로 리디렉션
      } catch (error) {
        navigate('/login'); // 오류 발생 시 로그인으로 리디렉션
      }
    };

    exchangeCode();
  }, [navigate]);

  return <div>Processing OAuth callback...</div>;
};

export default GoogleCallback;
```

**변경 사항:**

- `googleCodeForToken` 함수 호출 시 백엔드의 콜백 엔드포인트 URL로 수정.
- `redirectUri` 매개변수는 백엔드가 처리하므로 불필요하게 전달하지 않도록 수정.

### **5.2. 백엔드 콜백 엔드포인트 확인**

백엔드의 콜백 엔드포인트가 프론트엔드와 일치하도록 구성되어 있는지 확인합니다.

```python:msa/auth-fastapi/src/app/api/v1/endpoints/auth.py
@user_router.post(
    path="/google/callback",
    response_model=LoginResponse,
    summary="Google OAuth 콜백 처리",
    description="Google OAuth 인증 후 콜백을 처리하고 로그인을 수행합니다.",
)
async def google_callback(
    request: GoogleAuthRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    ...
```

- **확인 사항:**
  - `GoogleAuthRequest` 스키마에 `code`와 `redirect_uri`가 포함되어 있는지 확인합니다.
  - `redirect_uri`가 `https://test.myhome.com:8000/api/v1/users/google/callback`으로 정확히 설정되어 있는지 확인합니다.

### **5.3. 프론트엔드 로그인 버튼 구성 수정**

로그인 버튼이 백엔드의 Google Auth URL을 사용하도록 수정하여 OAuth 흐름을 백엔드가 처리하도록 합니다.

```typescript:msa/test-react/src/pages/login.tsx
const GOOGLE_URL = `${ENV_BACKEND_BASE_URL}/api/v1/users/google/auth`;
```

**설명:**

- **장점:**
  - OAuth 프로세스를 백엔드가 일관되게 처리하여 프론트엔드의 복잡성을 줄입니다.
  - 엔드포인트 사용의 일관성이 유지됩니다.
  - 보안상 이점을 제공합니다 (예: 클라이언트 시크릿 보호).

### **5.4. 환경 변수 정리 및 확인**

- **프론트엔드 (`msa/test-react/.env`):**

  ```env
  REACT_APP_ENV_BACKEND_BASE_URL=https://test.myhome.com:8000
  REACT_APP_ENV_GOOGLE_CLIENT_ID=your-google-client-id
  # REACT_APP_ENV_GOOGLE_REDIRECT_URL은 백엔드에서 처리하는 경우 생략
  ```

- **백엔드 (`msa/auth-fastapi/.env`):**

  ```env
  BACKEND_URL=https://test.myhome.com:8000
  GOOGLE_CLIENT_ID=your-google-client-id
  GOOGLE_CLIENT_SECRET=your-google-client-secret
  REDIRECT_URI=https://test.myhome.com:8000/api/v1/users/google/callback
  ```

- **확인 사항:**
  - 백엔드와 프론트엔드 모두 필요한 환경 변수가 정확히 설정되어 있는지 확인합니다.
  - `.env` 파일이 프로젝트의 루트 디렉토리에 위치하며, 애플리케이션이 이를 제대로 로드하고 있는지 검증합니다.

### **5.5. CORS 및 보안 설정 검토**

- **CORS 설정:**
  - 백엔드의 `main.py`에서 CORS 미들웨어가 올바르게 설정되어 있는지 다시 한 번 확인합니다.
  - 필요 시 추가적인 출처를 `origins` 리스트에 추가합니다.

- **보안 강화:**
  - HTTPS를 통해 모든 통신이 이루어지도록 서버 설정을 강화합니다.
  - HTTP-Only 쿠키를 사용하여 토큰을 안전하게 저장합니다.
  - CSRF 방지를 위한 추가적인 보안 조치를 고려합니다.

---

## 6. 결론

제공된 백엔드 및 프론트엔드 코드와 API 함수를 분석한 결과, 몇 가지 주요 수정 사항과 권장 사항을 도출할 수 있었습니다. 특히 프론트엔드와 백엔드 간의 엔드포인트 일관성을 유지하고, OAuth 흐름을 백엔드가 일관되게 처리하도록 구성하는 것이 핵심입니다. 또한, 환경 변수 설정과 CORS, 보안 설정을 정확하게 구성하여 인증 흐름의 안정성과 보안을 강화할 수 있습니다.

**주요 권장 사항 요약:**

1. **프론트엔드에서 백엔드 콜백 엔드포인트로 요청 수정**
2. **백엔드의 콜백 엔드포인트가 정확히 설정되었는지 확인**
3. **프론트엔드 로그인 버튼이 백엔드의 Google Auth URL을 사용하도록 수정**
4. **환경 변수 설정을 정확하게 구성 및 검증**
5. **CORS 및 보안 설정을 강화하여 안전한 인증 흐름 보장**

위의 권장 사항을 따르면, `test.myhome.com:8000` 백엔드와 `test.myhome.com:8002` 프론트엔드 간에 원활하고 안전한 Google OAuth 인증 흐름을 구현할 수 있을 것입니다. 추가적인 문제나 문의 사항이 있으시면 언제든지 도움을 드리겠습니다!
