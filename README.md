# 🏦 티끌모아(Ttiglemoa) - 개인 자산 관리 플랫폼

> "티끌 모아 태산" - 작은 자산부터 체계적으로 관리하여 큰 부를 이루어가는 개인 금융 관리 솔루션

배포 사이트 URL : https://ttiglemoa.onrender.com

## 📋 프로젝트 개요

티끌모아는 개인의 다양한 금융 자산을 체계적으로 관리하고 실시간으로 추적할 수 있는 종합 자산 관리 웹 애플리케이션입니다. 예금/적금, 주식, 채권 등 다양한 자산 클래스를 통합 관리하며, 실시간 시세 업데이트와 수익률 분석 기능을 제공합니다.

### 🎯 핵심 가치
- **통합 관리**: 은행 예적금부터 주식, 채권까지 한 곳에서 관리
- **실시간 추적**: FinanceDataReader, pykrx를 활용한 실시간 시세 업데이트
- **스마트 계산**: 복리 계산, 수익률 분석 등 자동화된 평가 시스템
- **직관적 UI**: 사용자 친화적인 인터페이스로 쉬운 자산 관리

## ✨ 주요 기능

### 👤 사용자 관리 (tm_account)
- **회원 인증**: django-allauth 기반 회원가입/로그인 시스템
- **프로필 관리**: 사용자 정보 수정 및 프로필 이미지 업로드
- **보안**: 커스텀 User 모델로 확장된 인증 시스템

### 💰 자산 관리 (tm_assets)
#### 📊 예금/적금 관리
- 은행별 상품 등록 및 관리
- 복리 계산 엔진 (월복리, 분기복리, 연복리)
- 만기일 기반 예상 수익 계산
- 수동 평가액 입력 지원

#### 📈 주식 포트폴리오
- 국내/해외 주식 구분 관리
- FinanceDataReader 연동 실시간 시세 업데이트
- 매수평균단가 대비 수익률 계산
- 다양한 통화 지원 (KRW, USD, JPY, EUR)

#### 🏛️ 채권 투자
- 채권별 상세 정보 관리 (발행처, 표면금리, 만기일)
- pykrx 라이브러리 연동 현재가 업데이트
- 액면가 대비 수익률 계산

#### 📊 자산 추적
- 실시간 가격 히스토리 저장
- 자산별 수익률 변동 추이 분석
- 포트폴리오 총 평가액 계산

### 🏠 메인 페이지 (tm_begin)
- 대시보드 형태의 자산 현황 요약
- 최근 자산 변동 내역 표시

### 📞 고객 지원 (tm_mylink)
- 사용자 문의 접수 시스템
- 문의 내역 관리

## 🛠️ 기술 스택

### Backend
- **Framework**: Django 5.2.6
- **Language**: Python 3.12
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Authentication**: django-allauth
- **File Storage**: AWS S3 (Supabase)

### Frontend
- **Template Engine**: Django Templates
- **Styling**: Bootstrap 5 (crispy-forms)
- **Icons & UI**: Custom CSS + Bootstrap components

### Data & APIs
- **Stock Data**: FinanceDataReader
- **Bond Data**: pykrx
- **Web Scraping**: BeautifulSoup4, feedparser
- **Data Processing**: pandas, numpy

### Deployment & Infrastructure
- **Platform**: Render
- **Static Files**: WhiteNoise
- **File Storage**: Supabase Storage (S3 compatible)
- **Database**: Supabase PostgreSQL

### Development Tools
- **Code Quality**: ruff (linting)
- **Package Management**: pip + requirements.txt
- **Environment**: python-decouple

## 📂 프로젝트 구조

```
ttiglemoa/
├── 📁 apps/                    # Django 앱 모음
│   ├── 📁 tm_account/          # 사용자 인증 및 프로필 관리
│   │   ├── 📁 forms/           # 폼 정의 (패스워드, 프로필)
│   │   ├── 📁 views/           # 뷰 로직 (인증, 프로필, 회원가입)
│   │   ├── 📁 migrations/      # 데이터베이스 마이그레이션
│   │   └── models.py           # 커스텀 User 모델
│   ├── 📁 tm_assets/           # 자산 관리 핵심 모듈
│   │   ├── 📁 management/      # Django 관리 명령어
│   │   │   └── commands/       # 자산 가격 업데이트 명령어
│   │   ├── models.py           # 예적금, 주식, 채권 모델
│   │   ├── forms.py            # 자산 등록/수정 폼
│   │   └── views.py            # 자산 관리 뷰
│   ├── 📁 tm_begin/            # 메인 페이지 및 대시보드
│   └── 📁 tm_mylink/           # 사용자 문의 시스템
├── 📁 config/                  # Django 설정
│   ├── settings.py             # 메인 설정 파일
│   ├── urls.py                 # URL 라우팅
│   └── wsgi.py                 # WSGI 설정
├── 📁 templates/               # HTML 템플릿
├── 📁 static/                  # 정적 파일 (CSS, JS, Images)
├── 📁 media/                   # 사용자 업로드 파일
├── requirements.txt            # Python 의존성
├── Procfile                    # Render 배포 설정
└── manage.py                   # Django 관리 스크립트
```

## 🚀 개발 환경 설정

### 1. 저장소 클론 및 환경 설정

```bash
# 저장소 클론
git clone https://github.com/daemonXid/ttiglemoa.git
cd ttiglemoa

# Python 가상환경 생성 (conda 사용)
conda create -n ttiglemoa python=3.12
conda activate ttiglemoa

```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:

```bash
# .env 파일 생성
cp .env.example .env
```

**필수 환경 변수:**
```env
# Django 시크릿 키
SECRET_KEY="your-secret-key"

# 개발 모드 설정
DEBUG=True

# 데이터베이스 URL (개발용은 SQLite 기본값 사용)
DATABASE_URL=""

# Supabase 스토리지 설정 (파일 업로드용)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_STORAGE_BUCKET_NAME=""
AWS_S3_ENDPOINT_URL=""
AWS_S3_REGION_NAME=""
```

### 4. 데이터베이스 설정

```bash
# 마이그레이션 적용
python manage.py migrate

# 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser
```

### 5. 개발 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000`에 접속하여 애플리케이션이 정상 동작하는지 확인하세요.

## 🎯 주요 기능 사용법

### 자산 가격 업데이트
```bash
# 모든 주식 가격 업데이트
python manage.py update_asset_prices

# 특정 자산 타입만 업데이트
python manage.py update_asset_prices --stocks-only
python manage.py update_asset_prices --bonds-only
```

## 🌐 배포 (Render)

### 환경 변수 설정
Render 대시보드에서 다음 환경 변수들을 설정하세요:

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `SECRET_KEY` | Django 시크릿 키 | `django-insecure-...` |
| `DEBUG` | 프로덕션에서는 False | `False` |
| `DATABASE_URL` | PostgreSQL 연결 문자열 | `postgresql://user:pass@host:5432/db` |
| `AWS_ACCESS_KEY_ID` | Supabase 스토리지 키 | |
| `AWS_SECRET_ACCESS_KEY` | Supabase 스토리지 시크릿 | |
| `AWS_STORAGE_BUCKET_NAME` | 스토리지 버킷명 | |
| `AWS_S3_ENDPOINT_URL` | Supabase 스토리지 엔드포인트 | |
| `AWS_S3_REGION_NAME` | 리전 | `ap-northeast-2` |

### 배포 명령어
```bash
# 정적 파일 수집
python manage.py collectstatic --noinput

# 마이그레이션 적용
python manage.py migrate
```

## 🤝 개발 가이드라인

### 브랜치 전략
- `main`: 프로덕션 배포용 안정 브랜치
- `develop`: 개발 통합 브랜치
- `feature/기능명`: 새로운 기능 개발
- `bugfix/버그명`: 버그 수정
- `hotfix/긴급수정`: 프로덕션 긴급 수정

### 커밋 메시지 규칙
```
type(scope): subject

body (선택사항)

footer (선택사항)
```

**Type:**
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드 프로세스 또는 보조 도구 변경

**예시:**
```
feat(assets): add real-time stock price update
fix(auth): resolve login redirect issue
docs(readme): update installation guide
```

## 📈 성능 최적화

### 데이터베이스 최적화
- 자산 가격 히스토리 인덱스 활용
- 쿼리 최적화 (select_related, prefetch_related)
- 캐싱 전략 적용

### API 최적화
- FinanceDataReader 요청 최적화
- 배치 처리를 통한 대량 업데이트
- 에러 핸들링 및 재시도 로직

## 🐛 문제 해결

### 일반적인 문제들
1. **환경 변수 누락**: `.env` 파일 확인
2. **데이터베이스 연결 오류**: `DATABASE_URL` 확인
3. **정적 파일 문제**: `collectstatic` 실행
4. **패키지 충돌**: `pip install -r requirements.txt` 재실행

### 로그 확인
```bash
# Render 로그 확인
render logs --tail

# 로컬 디버그 모드 활성화
DEBUG=True python manage.py runserver
```

## 📚 추가 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [FinanceDataReader 문서](https://financedata.github.io/FinanceDataReader/)
- [pykrx 문서](https://github.com/sharebook-kr/pykrx)
- [Render 배포 가이드](https://render.com/docs/deploy-django)

## 📧 연락처

프로젝트 관련 문의사항은 이슈 또는 팀 디스코드를 통해 연락주세요.

---

<div align="center">
  <strong>💰 티끌모아와 함께 체계적인 자산 관리를 시작하세요! 💰</strong>
</div>