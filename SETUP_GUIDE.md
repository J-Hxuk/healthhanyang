# 프로젝트 설정 가이드

다른 기기에서 이 프로젝트를 이어서 작업하는 방법입니다.

## 1. 저장소 클론

### 처음 설정하는 경우

```bash
# 원하는 디렉토리로 이동
cd ~/Desktop  # 또는 원하는 경로

# GitHub에서 클론
git clone https://github.com/J-Hxuk/healthhanyang.git

# 프로젝트 디렉토리로 이동
cd healthhanyang
```

### 이미 클론한 경우 (최신 변경사항 가져오기)

```bash
# 프로젝트 디렉토리로 이동
cd healthhanyang

# 최신 변경사항 가져오기
git pull origin main
```

## 2. Python 환경 설정

### Python 버전 확인

Python 3.8 이상이 필요합니다.

```bash
python --version
# 또는
python3 --version
```

### 가상환경 생성 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 3. 프로젝트 구조 확인

```
cat_health_copilot/
├── app.py                    # Streamlit 메인 앱
├── flask_server.py           # ESP32 데이터 수신 서버
├── esp32_code.ino           # ESP32 Arduino 코드
├── requirements.txt          # Python 의존성
├── ESP32_SETUP.md           # ESP32 연동 가이드
├── SETUP_GUIDE.md           # 이 파일
├── config/                   # 설정 파일
├── data/                     # 데이터 저장소
│   ├── raw/                 # 원본 센서 데이터
│   ├── processed/           # 처리된 데이터
│   ├── events/              # 감지된 이벤트
│   ├── profiles/            # 고양이 프로필
│   ├── baseline/            # 기준선 히스토리
│   └── alerts/              # 알림 데이터
├── src/                      # 소스 코드
│   ├── data/                # 데이터 수신 및 검증
│   ├── preprocessing/       # 전처리 (필터링, 기준선)
│   ├── events/              # 이벤트 감지 및 분류
│   ├── identification/      # 고양이 식별
│   ├── tracking/            # 체중 추적
│   ├── alerts/              # 알림 생성
│   ├── simulation/          # 시뮬레이션 도구
│   ├── storage/             # 데이터베이스
│   └── ui/                  # UI 페이지
└── .kiro/                    # Kiro 스펙 파일
    └── specs/
        └── advanced-simulation-and-tracking/
```

## 4. 애플리케이션 실행

### Streamlit 대시보드 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 열립니다 (보통 http://localhost:8501)

포트가 사용 중인 경우:
```bash
streamlit run app.py --server.port 8502
```

### Flask 서버 실행 (ESP32 연동용)

```bash
python flask_server.py
```

서버가 http://0.0.0.0:5000 에서 실행됩니다.

## 5. 작업 후 변경사항 저장

### 변경사항 확인

```bash
git status
```

### 변경사항 커밋

```bash
# 변경된 파일 추가
git add .

# 커밋 (의미있는 메시지 작성)
git commit -m "feat: 새로운 기능 추가"
# 또는
git commit -m "fix: 버그 수정"
# 또는
git commit -m "docs: 문서 업데이트"
```

### GitHub에 푸시

```bash
git push origin main
```

## 6. 다른 기기에서 작업 이어하기

### 최신 변경사항 가져오기

```bash
# 프로젝트 디렉토리로 이동
cd healthhanyang

# 최신 변경사항 가져오기
git pull origin main

# 의존성 업데이트 (새로운 패키지가 추가된 경우)
pip install -r requirements.txt
```

## 7. Git 커밋 메시지 규칙

일관성 있는 커밋 메시지를 위해 다음 규칙을 따릅니다:

- `feat:` - 새로운 기능 추가
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `style:` - 코드 포맷팅 (기능 변경 없음)
- `refactor:` - 코드 리팩토링
- `test:` - 테스트 추가/수정
- `chore:` - 빌드 프로세스, 도구 설정 등

예시:
```bash
git commit -m "feat: 체중 추적 페이지 추가"
git commit -m "fix: 기준선 계산 오류 수정"
git commit -m "docs: ESP32 연동 가이드 업데이트"
```

## 8. 문제 해결

### 의존성 충돌

```bash
# 가상환경 삭제 후 재생성
rm -rf venv  # Mac/Linux
# 또는
rmdir /s venv  # Windows

# 가상환경 재생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 의존성 재설치
pip install -r requirements.txt
```

### Git 충돌 해결

```bash
# 로컬 변경사항 임시 저장
git stash

# 최신 변경사항 가져오기
git pull origin main

# 임시 저장한 변경사항 복원
git stash pop

# 충돌이 있는 경우 수동으로 해결 후
git add .
git commit -m "merge: 충돌 해결"
```

### 포트 충돌

Streamlit 포트 변경:
```bash
streamlit run app.py --server.port 8502
```

Flask 포트 변경:
```python
# flask_server.py 마지막 줄 수정
app.run(host='0.0.0.0', port=5001, debug=True)  # 5000 → 5001
```

## 9. 개발 워크플로우

### 일반적인 작업 흐름

1. **작업 시작 전**
   ```bash
   git pull origin main
   ```

2. **코드 작성 및 테스트**
   ```bash
   streamlit run app.py
   ```

3. **변경사항 확인**
   ```bash
   git status
   git diff
   ```

4. **커밋 및 푸시**
   ```bash
   git add .
   git commit -m "feat: 설명"
   git push origin main
   ```

### 브랜치 사용 (선택사항)

큰 기능을 개발할 때는 브랜치를 사용하는 것이 좋습니다:

```bash
# 새 브랜치 생성 및 이동
git checkout -b feature/new-feature

# 작업 후 커밋
git add .
git commit -m "feat: 새 기능 구현"

# 브랜치 푸시
git push origin feature/new-feature

# GitHub에서 Pull Request 생성 후 main에 병합
```

## 10. 유용한 명령어

### Git 로그 확인
```bash
git log --oneline --graph --all
```

### 특정 파일 변경 이력
```bash
git log --follow -- src/tracking/weight_tracker.py
```

### 변경사항 취소
```bash
# 작업 디렉토리 변경사항 취소
git checkout -- filename

# 스테이징 취소
git reset HEAD filename

# 마지막 커밋 취소 (변경사항 유지)
git reset --soft HEAD~1
```

### 원격 저장소 정보
```bash
git remote -v
```

## 11. 추가 리소스

- **GitHub 저장소**: https://github.com/J-Hxuk/healthhanyang
- **ESP32 연동**: `ESP32_SETUP.md` 참조
- **건강 모니터링 가이드**: `HEALTH_MONITORING_GUIDE.md` 참조
- **배포 가이드**: `DEPLOY.md` 참조

## 12. 팀 협업 시 주의사항

1. **항상 pull 먼저**: 작업 시작 전 `git pull`
2. **자주 커밋**: 작은 단위로 자주 커밋
3. **의미있는 메시지**: 커밋 메시지는 명확하게
4. **충돌 최소화**: 같은 파일을 동시에 수정하지 않기
5. **테스트 후 푸시**: 동작 확인 후 푸시

## 문의

문제가 발생하면 GitHub Issues에 등록하거나 팀원에게 문의하세요.
