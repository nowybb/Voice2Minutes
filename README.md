# Voice2Minutes
음성을 텍스트로 변환하고 회의록을 ai 기반으로 요약해주는 웹 프로젝트 레퍼지토리입니다.

**Author** : 나연우

**GitHub** : https://github.com/nowybb

---

# 프로젝트 소개

Voice2Minutes는 음성 파일을 업로드하면 Return Zero STT API를 이용하여 음성을 텍스트로 변환하고, ai를 활용하여 회의록을 요약해주는 웹 애플리케이션입니다.

---

# 주요 기능

- MP3, M4A, MP4, WAV, FLAC, AMR 형식의 음성 파일 업로드
- Return Zero STT API를 이용한 음성 인식
- Google Gemini 기반 AI 회의 요약 및 핵심 키워드 추출
- 결정 사항(Decisions) 및 Action Items 자동 생성
- 전사 진행 상태를 실시간으로 확인 가능
- 전사 결과를 읽기 쉬운 회의록 형태의 화면으로 제공
- 생성된 회의록을 Markdown(.md) 파일로 다운로드
- 반응형 웹 인터페이스 제공

---

# 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| Frontend | React 19 | 사용자 인터페이스 구현 |
| | Vite | 프론트엔드 개발 환경 및 번들러 |
| | JavaScript (ES6+) | 프론트엔드 개발 언어 |
| | CSS3 | UI 스타일링 및 반응형 디자인 |
| Backend | FastAPI | REST API 서버 구축 |
| | Python 3.13 | 백엔드 개발 언어 |
| | Uvicorn | ASGI 서버 |
| AI | Return Zero STT API | 음성 파일 전사(STT) |
| | Google Gemini API | AI 회의 요약 및 키워드 추출 |
| | Pydantic | Structured Output(JSON Schema) 처리 |
| HTTP | Axios | 프론트엔드 API 통신 |
| DevOps | Git | 버전 관리 |
| | GitHub | 소스 코드 관리 |
| Development | Visual Studio Code | 개발 환경 |
| AI Assistant | ChatGPT | 코드 설계 및 리팩터링 지원 |
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
│   │   │   ├── gemini_minutes_service.py
│   │   │   ├── meeting_minutes_service.py
│   │   │   ├── transcription_job_service.py
│   │   │   ├── markdown_service.py
│   │   │   ├── file_service.py
│   │   │   └── job_service.py
│   │   └── main.py
│   ├── uploads
│   ├── outputs
│   ├── requirements.txt
│   └── .env.example
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

## 디렉터리 설명

| 디렉터리 | 역할 |
|----------|------|
| `backend/app/api` | REST API 엔드포인트 정의 |
| `backend/app/services/rtzr` | Return Zero STT API 인증 및 음성 전사 처리 |
| `backend/app/services/gemini_minutes_service.py` | Gemini API를 이용한 AI 회의 요약, 키워드 및 Action Items 생성 |
| `backend/app/services/meeting_minutes_service.py` | Gemini 실패 시 사용하는 규칙 기반 회의록 생성(Fallback) |
| `backend/app/services/transcription_job_service.py` | 전사 → AI 분석 → 회의록 생성 전체 워크플로우 관리 |
| `backend/app/services/markdown_service.py` | 회의록 Markdown(.md) 생성 |
| `backend/app/services/file_service.py` | 업로드 파일 저장 및 삭제 |
| `backend/app/services/job_service.py` | 작업(Job) 상태 관리 |
| `backend/app/core` | 환경 변수 및 공통 설정 |
| `backend/app/schemas` | 요청·응답 데이터 모델 |
| `backend/uploads` | 업로드된 음성 파일 저장 |
| `backend/outputs` | 생성된 회의록 저장 |
| `frontend/src/components` | React UI 컴포넌트 |
| `frontend/src/services` | 백엔드 API 호출 |
| `frontend/src/styles` | 전역 스타일 및 UI 디자인 |
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
4. 변환된 텍스트, 요약본과 Markdown 형식의 회의록을 확인합니다.

---

# 환경 변수 설정

## Backend

`backend/.env` 파일을 생성합니다.

```env
# Return Zero STT API
RTZR_CLIENT_ID=YOUR_RTZR_CLIENT_ID
RTZR_CLIENT_SECRET=YOUR_RTZR_CLIENT_SECRET

# Google Gemini API
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite
```

## Frontend

`frontend/.env` 파일을 생성합니다.

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

> **주의**
>
> - API Key 및 Secret은 절대 GitHub에 업로드하지 마세요.
> - `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다.
> - 저장소에는 `.env` 대신 `.env.example`만 포함합니다.
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

<img width="1488" height="588" alt="결과화면1" src="https://github.com/user-attachments/assets/1b0a3711-ed62-42f4-b591-647c18af51ba" />
<img width="1468" height="737" alt="결과화면2" src="https://github.com/user-attachments/assets/20d73640-60ae-4c44-b166-2e4f0ba82799" />
<img width="1242" height="502" alt="결과화면3" src="https://github.com/user-attachments/assets/00b5d76c-b4ea-49c2-becd-2b8d1f3a1feb" />


---

# 주요 코드 설명

## Backend

### `backend/app/main.py`

FastAPI 애플리케이션의 진입점입니다.

주요 기능

- FastAPI 애플리케이션 생성
- API 라우터 등록
- CORS 설정
- Swagger(OpenAPI) 문서 제공
- 서버 상태 확인 API 제공

### `backend/app/api/router.py`

모든 API 라우터를 등록하는 파일입니다.

등록 API

- Health API
- Transcription API

모든 API는 `/api/v1` 하위에서 동작합니다.

### `backend/app/api/routes/transcription.py`

음성 전사 및 회의록 생성과 관련된 API를 제공합니다.

주요 기능

- 음성 파일 업로드
- 전사 작업(Job) 생성
- 작업 상태 조회
- 회의록 결과 조회
- Markdown 다운로드

처리 흐름

```text
파일 업로드
    ↓
RTZR STT 요청
    ↓
백그라운드 작업 실행
    ↓
AI 회의록 생성
    ↓
결과 조회
    ↓
Markdown 다운로드
```

### `backend/app/core/config.py`

환경 변수를 관리하는 설정 파일입니다.

주요 설정

- RTZR Client ID
- RTZR Client Secret
- Gemini API Key
- Gemini Model
- 업로드 경로
- 출력 경로
- 파일 크기 제한

민감한 정보는 `.env`에서 관리합니다.

## RTZR API

### `backend/app/services/rtzr/auth.py`

RTZR 인증 토큰을 발급합니다.

---

### `backend/app/services/rtzr/client.py`

RTZR API와 통신하는 공통 HTTP Client입니다.

주요 기능

- Access Token 관리
- 공통 Header 생성
- API 요청
- 예외 처리

### `backend/app/services/rtzr/transcription.py`

RTZR STT API를 호출하여 음성 파일을 전사합니다.

주요 기능

- 음성 업로드
- STT 옵션 전달
- 전사 Job 생성

### `backend/app/services/rtzr/polling.py`

전사 완료 여부를 주기적으로 조회합니다.

```text
전사 요청
    ↓
상태 조회
    ↓
진행 중
    ↓
재조회
    ↓
완료
```

## AI Service

### `backend/app/services/gemini_minutes_service.py`

Google Gemini API를 이용하여 전사 결과를 AI 기반 회의록으로 분석합니다.

주요 기능

- 핵심 요약 생성
- 결정 사항 추출
- Action Items 생성
- 핵심 키워드 추출
- Structured Output(JSON Schema) 사용
- API 오류 발생 시 재시도(Exponential Backoff)

### `backend/app/services/meeting_minutes_service.py`

Gemini API를 사용할 수 없는 경우를 대비한 규칙 기반(Fallback) 회의록 생성 서비스입니다.

주요 기능

- 규칙 기반 핵심 요약
- 규칙 기반 키워드 추출
- 기본 Action Items 생성
- Gemini 장애 시 자동 대체

### `backend/app/services/transcription_job_service.py`

프로젝트의 핵심 Workflow를 담당합니다.

처리 과정

```text
음성 파일 업로드
        ↓
RTZR STT 요청
        ↓
전사 완료 대기
        ↓
Gemini AI 분석
        ↓
(실패 시 Rule-based Fallback)
        ↓
회의록 생성
        ↓
Markdown 생성
        ↓
작업 완료
```

### `backend/app/services/job_service.py`

전사 작업(Job)의 상태를 관리합니다.

상태

| 상태 | 설명 |
|------|------|
| queued | 작업 대기 |
| transcribing | STT 진행 |
| summarizing | AI 회의록 생성 |
| completed | 완료 |
| failed | 실패 |

### `backend/app/services/file_service.py`

업로드 파일을 검증하고 저장합니다.

주요 기능

- 파일 확장자 검사
- 파일 크기 검사
- UUID 기반 저장
- 임시 파일 삭제

지원 형식

```text
MP3
M4A
MP4
WAV
FLAC
AMR
```

### `backend/app/services/markdown_service.py`

회의록 데이터를 Markdown 문서로 변환합니다.

생성 항목

- 핵심 요약
- 결정 사항
- Action Items
- 핵심 키워드
- 전체 전사문

## Frontend

### `frontend/src/services/api.js`

Axios를 이용하여 백엔드 API와 통신합니다.

주요 기능

- 음성 파일 업로드
- 작업 상태 조회
- 회의록 조회
- Markdown 다운로드

### `frontend/src/App.jsx`

프로젝트의 메인 화면입니다.

주요 기능

- Drag & Drop 업로드
- 전사 옵션 설정
- 진행 상태 표시
- AI 회의록 출력
- Markdown 다운로드
- Preview 화면 제공

### `frontend/src/components/Header.jsx`

상단 네비게이션을 제공합니다.

- 로고
- Features
- How it works
- Preview

### `frontend/src/styles/global.css`

프로젝트 전체 UI 스타일을 관리합니다.

주요 구성

- 다크 테마
- 반응형 레이아웃
- 업로드 카드
- 진행 상태 UI
- AI 회의록 카드
- Markdown 다운로드 버튼
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
- 약 1시간 30분 길이

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


