# 티끌모아 서비스 Django 프로젝트

## 프로젝트 개요

티끌모아(Ttiglemoa)는 사용자가 자신의 금융 자산을 효과적으로 관리하고 추적할 수 있도록 돕는 개인용 자산 관리 웹 애플리케이션입니다. 예금, 적금, 주식, 채권 등 다양한 유형의 자산을 등록하고 현재 가치를 추정하며, 자산 변동 내역을 시각적으로 확인할 수 있는 기능을 제공합니다.

## 주요 기능

- **사용자 관리**: 회원가입, 로그인, 프로필 수정 및 프로필 이미지 변경 기능을 제공합니다.
- **자산 관리**:
    - **예/적금**: 은행, 상품명, 원금, 이율 등 상세 정보를 등록하고, 만기일과 복리 주기에 따른 예상 평가액을 계산합니다.
    - **주식**: 국내/해외 주식 정보를 등록하고, FinanceDataReader 라이브러리를 통해 최신 종가를 반영하여 현재 가치를 추정합니다.
    - **채권**: 채권명, 발행처, 표면금리 등 정보를 등록하고, pykrx 라이브러리를 활용해 현재가를 업데이트합니다.
- **자산 내역 기록**: 각 자산의 가격 및 평가액 변동 내역을 주기적으로 기록하여 자산 추이를 확인할 수 있습니다.
- **사용자 문의**: 사용자가 서비스에 대한 문의를 작성하고 제출할 수 있는 기능을 제공합니다.

## 기술 스택

- **백엔드**: Django, Python
- **데이터베이스**: (SQLite, Django 기본 설정에 따름)
- **주요 라이브러리**:
    - `FinanceDataReader`: 주식 가격 데이터 수집
    - `pykrx`: 채권 가격 데이터 수집
    - `beautifulsoup4`: 웹 스크래핑 (뉴스 등)
    - `pandas`: 데이터 처리
- **프론트엔드**: HTML, CSS, JavaScript

## 프로젝트 구조

- `config/`: 프로젝트의 주요 설정(settings) 및 URL 구성을 담당합니다.
- `apps/`: 개별 기능별로 모듈화된 Django 앱이 위치합니다.
    - `tm_account`: 사용자 인증 및 프로필 관리를 담당합니다.
    - `tm_assets`: 예/적금, 주식, 채권 등 자산 관리를 위한 핵심 로직을 포함합니다.
    - `tm_begin`: 애플리케이션의 초기 화면 또는 정적 페이지를 담당합니다.
    - `tm_mylink`: 사용자 문의(Inquiry) 기능을 담당합니다.

---

### ttiglemoa 프로젝트 참여를 위한 초기 설정 

```
git clone https://github.com/daemonXid/ttiglemoa.git
cd ttiglemoa

conda create -n ttiglemoa python=3.12
conda activate ttiglemoa

pip install -r requirements.txt
```

*ttiglemoa 폴더 내에 .env.example 파일이 있습니다. 
이 파일을 복사해서 새로운 파일명을 .env 로 생성해주세요
필요한 환경변수는 디스코드에 올리겠습니다. 

```
python manage.py migrate
python manage.py runserver
```

서버 실행 후 Django 기본 화면이 뜨는이 확인해주세요


---

## 팀 규칙
### 브랜치 전략


### 커밋 메시지 규칙