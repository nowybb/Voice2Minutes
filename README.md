# Voice2Minutes

> Return Zero STT API를 활용하여 음성을 텍스트로 변환하고 회의록을 요약해주는 웹

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

> 나중에 추가

---

# 결과 화면
> 나중에 추가

---

# 주요 코드 설명

나중에 추가

---

# 테스트 환경

- macOS
- Node.js 22
- npm 10

테스트 음성

- 무료 음성 데이터
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

나중에 추가


