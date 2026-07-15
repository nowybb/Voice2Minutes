# Voice2Minutes
음성을 텍스트로 변환하고 회의록을 요약해주는 웹 프로젝트 레퍼지토리입니다.

**Author** : 나연우

**GitHub** : https://github.com/nowybb

---

# 프로젝트 소개

Voice2Minutes는 음성 파일을 업로드하면 Return Zero STT API를 이용하여 음성을 텍스트로 변환하고, 회의록을 요약해주는 웹 애플리케이션입니다.

---

# 주요 기능

- MP3, M4A, MP4, WAV, FLAC, AMR 형식의 음성 파일 업로드
- Return Zero STT API를 이용한 음성 인식
- 전사 진행 상태를 실시간으로 확인 가능
- 전사 결과를 읽기 쉬운 회의록 형태의 화면으로 제공
- 생성된 회의록을 Markdown(.md) 파일로 다운로드
- 반응형 웹 인터페이스

---

# 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| Frontend | React 19 | 사용자 인터페이스 구현 |
|  | Vite | 프론트엔드 개발 환경 및 번들러 |
|  | JavaScript (ES6+) | 프론트엔드 개발 언어 |
|  | CSS3 | UI 스타일링 및 반응형 디자인 |
| Backend | FastAPI | REST API 서버 구축 |
|  | Uvicorn | ASGI 서버 |
|  | Python 3.13 | 백엔드 개발 언어 |
| API | Return Zero STT API | 음성 파일 전사(STT) |
| HTTP | Axios | 프론트엔드 API 통신 |
| 개발 도구 | Git | 버전 관리 |
|  | GitHub | 소스 코드 관리 |
|  | Visual Studio Code | 개발 환경 |
| AI Assistant | ChatGPT | 코드 리팩토링 지원 |
---

# 프로젝트 구조

```text
Voice2Minutes
├── backend
│   ├── app
│   │   ├── api
│   │   │   ├── models
│   │   │   ├── routes
│   │   │   └── router.py
│   │   ├── core
│   │   │   └── config.py
│   │   ├── schemas
│   │   ├── services
│   │   │   ├── rtzr
│   │   │   │   ├── auth.py
│   │   │   │   ├── client.py
│   │   │   │   ├── polling.py
│   │   │   │   └── transcription.py
│   │   │   ├── file_service.py
│   │   │   ├── job_service.py
│   │   │   ├── transcription_job_service.py
│   │   │   ├── markdown_service.py
│   │   │   └── meeting_minutes_service.py
│   │   └── main.py
│   ├── uploads
│   ├── outputs
│   ├── requirements.txt
│   └── .env
│
├── frontend
│   ├── src
│   │   ├── components
│   │   │   └── Header.jsx
│   │   ├── services
│   │   │   └── api.js
│   │   ├── styles
│   │   │   └── global.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
└── README.md
```

### 디렉터리 설명

| 디렉터리 | 역할 |
|----------|------|
| `backend/app/api` | API 엔드포인트 정의 |
| `backend/app/services` | 비즈니스 로직 및 RTZR STT API 연동 |
| `backend/app/core` | 환경 설정 및 공통 설정 |
| `backend/app/schemas` | 요청/응답 데이터 모델 |
| `backend/uploads` | 업로드된 음성 파일 저장 |
| `backend/outputs` | 생성된 회의록(Markdown) 저장 |
| `frontend/src/components` | React UI 컴포넌트 |
| `frontend/src/services` | 백엔드 API 호출 |
| `frontend/src/styles` | 전역 스타일 |

---

# 설치 및 실행 방법

## 1. 프로젝트 클론

```bash
git clone https://github.com/nowybb/voice2minutes.git
cd voice2minutes
```


## 2. Backend 실행

backend 디렉터리로 이동

```bash
cd backend
```

필요한 패키지 설치

```bash
pip install -r requirements.txt
```

환경 변수 설정

`.env` 파일을 생성한 뒤 아래 내용을 입력합니다.

```env
RTZR_CLIENT_ID=YOUR_CLIENT_ID
RTZR_CLIENT_SECRET=YOUR_CLIENT_SECRET
```

서버 실행

```bash
uvicorn app.main:app --reload
```

기본 주소

```
http://localhost:8000
```


## 3. Frontend 실행

새 터미널을 열어 frontend 디렉터리로 이동합니다.

```bash
cd frontend
```

필요한 패키지 설치

```bash
npm install
```

개발 서버 실행

```bash
npm run dev
```

브라우저에서 아래 주소로 접속합니다.

```
http://localhost:5173
```


## 4. 사용 방법

1. 웹페이지에 접속합니다.
2. 음성 파일(mp3, wav 등)을 업로드합니다.
3. STT 변환이 완료될 때까지 기다립니다.
4. 변환된 텍스트와 Markdown 형식의 회의록을 확인합니다.

---

# 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
VITE_RTZR_CLIENT_ID=YOUR_CLIENT_ID
VITE_RTZR_CLIENT_SECRET=YOUR_CLIENT_SECRET

```


> **API Key와 Secret 업로드 주의**

---

# 동작 과정

```text
음성 파일 업로드
        │
        ▼
Return Zero STT API 호출
        │
        ▼
음성 → 텍스트 변환
        │
        ▼
AI 요약
        │
        ▼
회의록 생성
        │
        ▼
결과 화면 출력
```

---

# 메인 화면


<img width="1488" height="811" alt="메인화면1" src="https://github.com/user-attachments/assets/7df9714c-f9a2-4cb3-b7a4-37579632adf1" />
<img width="1481" height="828" alt="메인화면2" src="https://github.com/user-attachments/assets/b38c1b9d-d832-4d45-93d1-b58806120edc" />
<img width="1493" height="836" alt="메인화면3" src="https://github.com/user-attachments/assets/41af0846-e5a2-4241-9e44-d84a1f332ab5" />
<img width="1474" height="840" alt="메인화면4" src="https://github.com/user-attachments/assets/b9595e81-c07a-4211-b14c-db8b5a5a9900" />

---

# 결과 화면
<img width="1511" height="763" alt="결과화면1" src="https://github.com/user-attachments/assets/d69761fa-b00c-4763-813f-bcc60f6e563c" />
<img width="1391" height="641" alt="결과화면3" src="https://github.com/user-attachments/assets/0a891fcc-8042-4453-84c7-f795a17869ff" />
<img width="1466" height="856" alt="결과화면2" src="https://github.com/user-attachments/assets/078fef0c-62da-4782-b2a2-bf7c9e3705b7" />

---

# 주요 코드 설명


## Backend

### `backend/app/main.py`

FastAPI 애플리케이션의 진입점입니다.

- FastAPI 앱 생성
- API 라우터 등록
- CORS 설정
- 서비스 이름, 버전, 설명 설정
- 서버 상태 확인용 기본 경로 제공

### `backend/app/api/router.py`

백엔드 API 라우터를 한곳에서 관리합니다.

- 상태 확인 API 등록
- 전사 작업 API 등록
- `/api/v1` 하위 경로 구성

### `backend/app/api/routes/health.py`

백엔드 서버가 정상적으로 실행되고 있는지 확인하는 API입니다.

```http
GET /api/v1/health
```

서버 상태, 서비스 이름, 버전 정보를 반환합니다.

### `backend/app/api/routes/transcription.py`

음성 전사와 관련된 주요 API 엔드포인트를 정의합니다.

주요 기능:

- 음성 파일 업로드
- 전사 작업 생성
- 전사 작업 상태 조회
- 완료된 전사 결과 조회
- Markdown 회의록 다운로드

주요 API 흐름:

```text
파일 업로드
    ↓
전사 작업 생성
    ↓
백그라운드 전사 실행
    ↓
작업 상태 조회
    ↓
전사 결과 확인
    ↓
Markdown 다운로드
```

### `backend/app/api/models/response.py`

API 응답 형식을 정의합니다.

응답 구조를 다음과 같이 일정하게 유지합니다.

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

이를 통해 프론트엔드가 각 API 응답을 일관된 방식으로 처리할 수 있습니다.

### `backend/app/schemas/transcription.py`

음성 전사 요청에 사용되는 옵션과 데이터 구조를 정의합니다.

주요 옵션:

- 화자 분리 사용 여부
- 예상 화자 수
- 간투어 제거 여부
- 문단 나누기 여부
- 인식 강화 키워드

Pydantic을 이용하여 요청 값을 검증합니다.

### `backend/app/core/config.py`

환경 변수를 불러오고 애플리케이션 설정을 관리합니다.

주요 설정:

- RTZR Client ID
- RTZR Client Secret
- API 기본 URL
- 업로드 파일 저장 경로
- 결과 파일 저장 경로
- 허용 파일 크기 및 확장자

민감한 인증 정보는 코드에 직접 작성하지 않고 `.env` 파일에서 불러옵니다.


## RTZR API 연동

### `backend/app/services/rtzr/auth.py`

RTZR API 인증을 담당합니다.

- `RTZR_CLIENT_ID`
- `RTZR_CLIENT_SECRET`

을 이용하여 RTZR 인증 서버에 요청하고 Access Token을 발급받습니다.

### `backend/app/services/rtzr/client.py`

RTZR API와 통신하기 위한 공통 HTTP 클라이언트입니다.

주요 역할:

- 인증 토큰을 포함한 요청 생성
- API 요청 헤더 구성
- 공통 오류 처리
- RTZR API 응답 처리

### `backend/app/services/rtzr/transcription.py`

RTZR STT API에 음성 파일을 전달하고 전사 작업을 생성합니다.

주요 기능:

- 음성 파일 업로드
- 전사 옵션 전달
- RTZR 전사 작업 ID 수신
- 전사 결과 조회

### `backend/app/services/rtzr/polling.py`

RTZR 전사 작업의 완료 여부를 반복해서 확인합니다.

```text
작업 생성
   ↓
상태 조회
   ↓
완료되지 않음 → 일정 시간 대기
   ↓
상태 다시 조회
   ↓
완료 → 전사 결과 반환
```

작업이 완료되거나 실패할 때까지 상태를 확인하며, 무한 요청을 방지하기 위한 대기 시간과 제한을 적용합니다.


## Service Layer

### `backend/app/services/file_service.py`

업로드된 음성 파일을 검증하고 저장합니다.

주요 기능:

- 파일 확장자 검증
- 파일 크기 검증
- 고유한 저장 파일명 생성
- 업로드 파일 저장
- 오류 발생 시 파일 삭제

지원 형식:

```text
MP3, M4A, MP4, WAV, FLAC, AMR
```

최대 파일 크기:

```text
2GB
```

### `backend/app/services/job_service.py`

전사 작업의 상태와 결과를 관리합니다.

주요 작업 상태:

| 상태 | 설명 |
|------|------|
| `queued` | 전사 작업 대기 중 |
| `transcribing` | 음성을 텍스트로 변환 중 |
| `summarizing` | 전사 결과를 회의록 형태로 정리 중 |
| `completed` | 작업 완료 |
| `failed` | 작업 실패 |

각 작업은 고유한 `job_id`를 사용하여 관리됩니다.

### `backend/app/services/transcription_job_service.py`

전사 작업 전체 흐름을 제어하는 핵심 서비스입니다.

주요 처리 과정:

```text
1. 업로드된 음성 파일 확인
2. RTZR 인증 토큰 발급
3. RTZR 전사 작업 생성
4. 전사 상태 반복 조회
5. 전사 결과 수신
6. 전사 결과를 회의록 구조로 정리
7. Markdown 파일 생성
8. 작업 상태를 completed로 변경
```

처리 중 오류가 발생하면 작업 상태를 `failed`로 변경하고 오류 정보를 저장합니다.

### `backend/app/services/meeting_minutes_service.py`

RTZR에서 반환된 전사 결과를 웹 화면에 표시하기 좋은 회의록 구조로 정리합니다.

정리되는 항목:

- 핵심 요약
- 결정 사항
- Action Items
- 주요 키워드
- 화자별 전체 전사문

이 프로젝트에서는 별도의 OpenAI API가 아니라, 전사 결과를 기반으로 회의록 데이터를 구성하는 서비스 계층으로 사용합니다.

### `backend/app/services/markdown_service.py`

구조화된 회의록 데이터를 Markdown 문서로 변환합니다.

생성되는 항목:

```text
회의 제목
핵심 요약
결정 사항
Action Items
주요 키워드
전체 전사문
```

완성된 파일은 `backend/outputs` 디렉터리에 저장되며, 사용자가 웹 화면에서 다운로드할 수 있습니다.


## Frontend

### `frontend/src/services/api.js`

프론트엔드와 백엔드 사이의 API 통신을 담당합니다.

주요 기능:

- 음성 파일 업로드
- 전사 작업 생성 요청
- 전사 상태 조회
- 전사 결과 조회
- Markdown 파일 다운로드

API 기본 주소는 프론트엔드 `.env` 파일에서 불러옵니다.

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### `frontend/src/App.jsx`

Voice2Minutes의 주요 화면과 상태를 관리하는 핵심 컴포넌트입니다.

주요 기능:

- 음성 파일 선택
- 드래그 앤 드롭 업로드
- 파일 형식 및 용량 검증
- 전사 옵션 선택
- 백엔드 전사 API 호출
- 작업 진행 상태 표시
- 전사 결과 출력
- Markdown 다운로드
- 로고 클릭 시 초기 화면으로 복귀
- Features, How it works, Preview 섹션 출력

주요 상태 흐름:

```text
파일 대기
   ↓
파일 선택 완료
   ↓
전사 요청
   ↓
진행 상태 조회
   ↓
작업 완료
   ↓
회의록 결과 출력
   ↓
Markdown 다운로드
```

### `frontend/src/components/Header.jsx`

상단 헤더와 내비게이션을 담당합니다.

주요 기능:

- Voice2Minutes 로고 표시
- 로고 클릭 시 홈 화면 초기화
- Features 섹션 이동
- How it works 섹션 이동
- Preview 섹션 이동

### `frontend/src/styles/global.css`

프로젝트 전체 UI 스타일을 관리합니다.

주요 스타일:

- 다크 테마와 하늘색 포인트 컬러
- 반응형 레이아웃
- 음성 업로드 카드
- 진행 상태 바
- 회의록 결과 카드
- 전사문 목록
- Features 카드
- How it works 카드
- Preview 화면

모바일, 태블릿, 데스크톱 화면 크기에 따라 레이아웃이 자동으로 조정됩니다.

---
# 전체 데이터 흐름

```text
사용자
  ↓
React에서 음성 파일 선택
  ↓
FormData로 FastAPI에 업로드
  ↓
파일 검증 및 로컬 저장
  ↓
전사 Job 생성
  ↓
RTZR 인증 및 STT API 호출
  ↓
전사 작업 상태 Polling
  ↓
RTZR 전사 결과 수신
  ↓
회의록 데이터 구조화
  ↓
Markdown 파일 생성
  ↓
React 결과 화면 출력
  ↓
사용자 Markdown 다운로드
```

---

# 테스트 환경

- macOS
- Node.js 22
- npm 10

테스트 음성

- AI 허브 무료 음성 데이터
- https://aihub.or.kr/aihubnews/faq/list.do?currMenu=146&topMenu=104 
- 약 3분 길이

---

# 제한 사항

- 긴 음성 파일은 처리 시간이 길어질 수 있습니다.

---

# 향후 개선 사항
- 실시간 음성 인식
- PDF 회의록 저장
- 키워드 하이라이트
- 전문 검색 기능

---

# AI 활용

본 프로젝트는 개발 과정에서 AI 코딩 도구의 도움을 받아 제작되었습니다.

AI는 아래 작업에 활용되었습니다.

- 코드 초안 작성
- 리팩토링
- CSS 개선

최종 코드의 수정, 테스트 및 검증은 직접 수행하였습니다.

---

# 라이선스
MIT License © 2026 nowybb


