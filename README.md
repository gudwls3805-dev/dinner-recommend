# 🍽️ 오늘 뭐 먹지 — AI 저녁 메뉴 추천

기분과 상황만 고르면 AI가 오늘 저녁 메뉴를 대신 골라주는 웹 서비스.
"퇴근길 배달앱 무한스크롤"을 30초로 줄이는 것이 목표.

**배포 URL:** `https://여기에-본인-vercel-주소.vercel.app`

---

## 🧩 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| 프론트엔드 | 바닐라 HTML / CSS / JavaScript (프레임워크 미사용) |
| 백엔드 | Vercel Serverless Functions (Python) |
| AI | Google Gemini API (`gemini-2.5-flash`) |
| 배포 | Vercel + GitHub 연동 |
| 폰트 | Black Han Sans, Pretendard |

---

## 📂 프로젝트 구조

```
.
├── index.html          # 메인 (히어로 / 추천 / 사용법 / 문의 4개 섹션)
├── css/style.css       # 스타일 (다크 dusk 테마 · 반응형)
├── js/main.js          # 폼 처리 · fetch · 실패 처리
├── api/
│   └── recommend.py    # Gemini 호출 서버리스 함수 (POST /api/recommend)
├── requirements.txt    # Python 의존성 (requests)
├── vercel.json         # Vercel 빌드 설정
├── .env.example        # 환경 변수 예시
└── README.md
```

---

## 🚀 실행 / 배포 방법

### 1) 로컬에서 확인 (프론트만)
프론트는 정적 파일이라 브라우저로 바로 열어도 화면은 확인돼.
단, `/api/recommend`(AI 기능)는 Vercel 환경에서 동작하므로
전체 기능은 아래 배포 후 확인한다.

```bash
# 예: 간단한 로컬 서버로 프론트 확인
python -m http.server 3000
# → http://localhost:3000
```

### 2) Vercel 배포
1. 이 저장소를 GitHub에 push
2. [vercel.com](https://vercel.com) → **Add New → Project** → 저장소 Import
3. 아래 **환경 변수**를 등록 (중요)
4. **Deploy** 클릭 → 배포 URL 발급
5. 수정 사항이 생기면 GitHub에 push → 자동 재배포

---

## 🔑 환경 변수 설정

API 키는 **코드에 절대 하드코딩하지 않고** 환경 변수로만 관리한다.

| 변수명 | 설명 |
|--------|------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급한 키 |

**Vercel 등록 방법**
`Project → Settings → Environment Variables`
→ Name: `GEMINI_API_KEY`, Value: 발급받은 키 → Save → **Redeploy**

**로컬 테스트 시**
`.env.example`을 참고해 값을 채우되, `.env`는 `.gitignore`에 포함되어
커밋되지 않는다. (키가 커밋 이력에 노출되면 즉시 폐기·재발급할 것)

---

## 🤖 AI 기능 동작 흐름

```
[사용자] 상황·기분·예산·제외재료 선택
   │  (js/main.js: fetch POST)
   ▼
[/api/recommend] Python 함수가 프롬프트 조립 → Gemini 호출
   │  Gemini가 JSON(메뉴 3개 + 이유 + 검색어) 반환
   ▼
[화면] 메뉴 카드 3개로 렌더링
```

### 실패 처리 기준
| 상황 | 처리 |
|------|------|
| 빈 입력(상황·기분 미선택) | "상황과 기분은 꼭 골라줘!" 안내 (요청 전 차단) |
| API 오류 (4xx/5xx) | "메뉴를 불러오지 못했어" + 다시 시도 버튼 |
| 지연/타임아웃 (20초 초과) | "응답이 너무 늦네…" 안내 후 재시도 유도 |

---

## ✅ 요구사항 체크

- [x] 3개 이상 섹션 + 네비게이션 이동
- [x] 반응형 (모바일/데스크톱)
- [x] AI API 연동 기능 1개 (입력 → 결과 출력)
- [x] 프론트(HTML/CSS/JS) / 백엔드(api/) 구조 분리
- [x] 환경 변수로 키 관리
- [x] 실패 처리 3종 (빈 입력 / API 오류 / 타임아웃)
