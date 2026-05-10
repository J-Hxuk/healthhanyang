# 배포 가이드

## GitHub에 푸시하기

```bash
# 변경사항 추가
git add .

# 커밋
git commit -m "Fix: Streamlit Cloud 배포를 위한 의존성 및 설정 수정

- requirements.txt 단순화 (불필요한 의존성 제거)
- .gitignore 추가 (데이터 파일 제외)
- .streamlit/config.toml 추가 (Streamlit 설정)
- .python-version 추가 (Python 3.11 명시)
- README.md 업데이트 (사용법 및 기능 설명)
- .gitkeep 파일 추가 (디렉토리 구조 유지)"

# GitHub에 푸시
git push origin main
```

## Streamlit Cloud 배포

1. **Streamlit Cloud 접속**
   - https://share.streamlit.io/ 접속
   - GitHub 계정으로 로그인

2. **새 앱 배포**
   - "New app" 버튼 클릭
   - Repository: `your-username/cat_health_copilot` 선택
   - Branch: `main` 선택
   - Main file path: `app.py` 입력
   - "Deploy!" 버튼 클릭

3. **배포 완료**
   - 몇 분 후 앱이 배포됩니다
   - URL: `https://your-app-name.streamlit.app`

## 문제 해결

### 의존성 오류가 발생하는 경우

1. **requirements.txt 확인**
   ```
   streamlit>=1.28.0
   python-dateutil>=2.8.2
   ```
   - 최소한의 의존성만 포함
   - pandas, numpy는 streamlit에 포함되어 있음

2. **Python 버전 확인**
   - `.python-version` 파일에 `3.11` 명시
   - Streamlit Cloud는 Python 3.9-3.11 지원

3. **로그 확인**
   - Streamlit Cloud 대시보드에서 "Manage app" 클릭
   - "Logs" 탭에서 오류 메시지 확인

### 데이터 파일 문제

- `.gitignore`에서 실제 데이터 파일은 제외
- `.gitkeep` 파일로 디렉토리 구조만 유지
- 앱 실행 시 자동으로 데이터 디렉토리 생성

## 팀원과 공유

1. **GitHub 저장소 공유**
   - Repository URL 공유
   - 팀원을 Collaborator로 추가

2. **Streamlit Cloud URL 공유**
   - 배포된 앱 URL 공유
   - 누구나 접속 가능 (공개 앱)

3. **데이터 초기화**
   - 공유 전 "설정" → "전체 데이터 초기화"
   - 깨끗한 상태로 시작

## 업데이트

코드 수정 후:

```bash
git add .
git commit -m "Update: 기능 설명"
git push origin main
```

Streamlit Cloud가 자동으로 재배포합니다 (약 1-2분 소요).
