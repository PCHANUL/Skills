# Flutter Migration GitHub 프로젝트 관리 가이드

## 📋 개요

Flutter 멀티플랫폼 전환 프로젝트를 GitHub Projects, Milestones, Issues로 관리하는 방법입니다.

---

## 🎯 구조

```
Repository: PCHANUL/IIIF
├── Project: "IIIF Flutter Migration"
├── 8 Milestones (Phase 1-8)
├── 220+ Issues (작업 단위)
└── Labels (우선순위, Phase, 타입, 플랫폼)
```

---

## 🚀 빠른 시작

### 1. GitHub CLI 인증

```bash
gh auth login
```

### 2. Issues 자동 생성

```bash
cd /Users/chanulpark/IIIF
./scripts/create_flutter_issues.sh
```

이 스크립트는 자동으로:
- ✅ 8개 Milestones 생성 (Phase 1-8, 마감일 포함)
- ✅ 24개 Labels 생성 (우선순위/Phase/타입/플랫폼)
- ✅ 220+ Issues 생성 (FLUTTER_TODO.md 기반)
- ✅ Project Board에 자동 추가

---

## 📊 Project Board 설정

### 1. Project 생성 (수동)

1. https://github.com/users/PCHANUL/projects 접속
2. "New project" 클릭
3. 이름: `IIIF Flutter Migration`
4. Template: `Board` 선택

### 2. View 설정

#### View 1: Kanban Board (기본)

**Columns:**
```
📝 Backlog    - 계획된 작업
🔜 Ready      - 시작 가능
🏗️ In Progress - 진행 중
👀 In Review  - 리뷰 중
✅ Done       - 완료
```

**설정 방법:**
1. Project 열기
2. "+" 버튼 → "New view" → "Board"
3. Group by: Status
4. 각 컬럼 이름 변경

#### View 2: Timeline (Gantt)

**설정 방법:**
1. "+" 버튼 → "New view" → "Roadmap"
2. Start date: Created date
3. Target date: Milestone due date
4. Group by: Milestone

#### View 3: Table (전체 목록)

**Columns:**
- Title
- Status
- Priority
- Phase
- Assignee
- Milestone
- Labels

### 3. Custom Fields 추가

1. Project 설정 (⚙️) → "Fields"
2. 다음 필드 추가:

```yaml
Priority (Single select):
  - P0 - Critical 🔴
  - P1 - High 🟠
  - P2 - Medium 🟡
  - P3 - Low 🟢

Phase (Single select):
  - Phase 1: Foundation
  - Phase 2: Auth & Home
  - Phase 3: Card System
  - Phase 4: Gacha
  - Phase 5: Story
  - Phase 6: Card Creation
  - Phase 7: Testing
  - Phase 8: Deployment

Estimated Days (Number):
  - 0.5, 1, 2, 3, 5

Platform (Multi select):
  - iOS
  - Android
  - Web
  - All
```

---

## 🏷️ Labels 시스템

### 우선순위
- `priority/P0` 🔴 - Critical (앱 동작 필수)
- `priority/P1` 🟠 - High (핵심 기능)
- `priority/P2` 🟡 - Medium (중요하지만 나중 가능)
- `priority/P3` 🟢 - Low (Nice to have)

### Phase
- `phase/1-foundation` - Phase 1
- `phase/2-auth` - Phase 2
- ... (총 8개)

### 타입
- `type/feature` - 새 기능
- `type/bug` - 버그 수정
- `type/refactor` - 리팩토링
- `type/docs` - 문서
- `type/test` - 테스트

### 플랫폼
- `platform/ios` - iOS 전용
- `platform/android` - Android 전용
- `platform/web` - Web 전용
- `platform/all` - 모든 플랫폼

---

## 📝 Issue 생성 규칙

### Issue 제목 형식

```
[Phase N] 작업 ID 작업 내용
```

**예시:**
```
[Phase 1] Flutter 프로젝트 초기 설정
[Phase 3] 카드 UI 컴포넌트 구현
[Phase 5] AI 스토리 생성 연동
```

### Issue 본문 템플릿

```markdown
## Context
- Phase: Phase N
- Section: 섹션명
- Source: Docs/flutter/FLUTTER_TODO.md

## Task
작업 설명

## Details
상세 내용 (체크리스트, 코드 예시 등)

## Acceptance Criteria
- [ ] 조건 1
- [ ] 조건 2
- [ ] 조건 3

## Files
- `lib/features/xxx/xxx.dart`

## Related Issues
- Depends on #XX
- Blocks #XX

## Estimated
N days
```

---

## 🔄 Workflow

### 1. 작업 시작

```bash
# 1. Issue를 "Ready" → "In Progress"로 이동
# 2. 자신을 Assignee로 설정
# 3. Branch 생성
git checkout -b feature/phase-1/setup-project

# 4. 작업 진행...
```

### 2. 작업 완료

```bash
# 1. Commit (Conventional Commits)
git commit -m "feat(phase-1): Flutter 프로젝트 초기 설정 (#1)"

# 2. Push
git push origin feature/phase-1/setup-project

# 3. Pull Request 생성
gh pr create --title "[Phase 1] Flutter 프로젝트 초기 설정" \
  --body "Closes #1" \
  --label "phase/1-foundation,priority/P0"

# 4. Issue를 "In Progress" → "In Review"로 이동
```

### 3. 리뷰 & 머지

```bash
# 1. 코드 리뷰 완료
# 2. PR 머지
# 3. Issue 자동으로 "Done"으로 이동 (Closes #1)
# 4. Branch 삭제
```

---

## 📈 진행 상황 추적

### Milestone 진행률 확인

```bash
gh api "/repos/PCHANUL/IIIF/milestones" \
  --jq '.[] | "\(.title): \(.open_issues)/\(.closed_issues + .open_issues) (\(.closed_issues * 100 / (.closed_issues + .open_issues) | floor)%)"'
```

### Phase별 Issue 목록

```bash
# Phase 1 Issues
gh issue list --label "phase/1-foundation" --state all

# 진행 중인 Issues
gh issue list --label "phase/1-foundation" --state open
```

### Project Board 상태별 조회

```bash
# 스크립트 사용
./scripts/gh_project_items_list_by_status.sh \
  --project "IIIF Flutter Migration" \
  --status "In Progress"
```

---

## 🛠️ 유틸리티 스크립트

### Issue 내 체크박스 토글

```bash
./scripts/gh_issue_checklist_toggle_item.sh \
  --issue 123 \
  --item "Flutter 프로젝트 생성"
```

### Issue에 체크리스트 댓글 추가

```bash
./scripts/gh_issue_comment_add_checklist.sh \
  --issue 123 \
  --checklist "- [ ] 작업 1\n- [ ] 작업 2"
```

### Project Item 상태 변경

```bash
./scripts/gh_project_item_set_status.sh \
  --project "IIIF Flutter Migration" \
  --issue 123 \
  --status "In Progress"
```

---

## 📊 대시보드 & 리포트

### README 배지 추가

```markdown
## Progress

![Phase 1](https://img.shields.io/github/milestones/progress/PCHANUL/IIIF/1?label=Phase%201)
![Phase 2](https://img.shields.io/github/milestones/progress/PCHANUL/IIIF/2?label=Phase%202)
![Phase 3](https://img.shields.io/github/milestones/progress/PCHANUL/IIIF/3?label=Phase%203)
...
```

### Burndown Chart

GitHub Projects에서 자동 생성:
1. Project → Insights
2. Burndown chart 확인

---

## 🎨 Branch 전략

```
main (production)
  ↑
develop (integration)
  ↑
feature/phase-N/feature-name
  ├─ feature/phase-1/setup-project
  ├─ feature/phase-1/firebase-setup
  ├─ feature/phase-2/auth-ui
  └─ feature/phase-3/card-view
```

### Branch 명명 규칙

```
feature/phase-N/short-description
fix/phase-N/bug-description
refactor/phase-N/refactor-description
test/phase-N/test-description
```

---

## 📝 Commit Convention

```
<type>(<scope>): <subject> (#issue)

type:
  - feat: 새 기능
  - fix: 버그 수정
  - refactor: 리팩토링
  - test: 테스트
  - docs: 문서
  - style: 코드 스타일
  - chore: 기타

scope: phase-N

예시:
feat(phase-1): Flutter 프로젝트 초기 설정 (#1)
feat(phase-2): 로그인 UI 구현 (#15)
fix(phase-3): 카드 애니메이션 버그 수정 (#42)
test(phase-7): 카드 뷰 위젯 테스트 추가 (#180)
```

---

## 🔍 Issue 검색 팁

### GitHub 검색 쿼리

```bash
# Phase 1의 열린 Issues
is:issue is:open label:phase/1-foundation

# P0 우선순위 Issues
is:issue label:priority/P0

# 나에게 할당된 Issues
is:issue assignee:@me

# 특정 Milestone
is:issue milestone:"Phase 1: Foundation"

# 여러 조건 조합
is:issue is:open label:phase/1-foundation label:priority/P0 assignee:@me
```

---

## 📚 참고 링크

- **Repository**: https://github.com/PCHANUL/IIIF
- **Project Board**: https://github.com/users/PCHANUL/projects
- **Issues**: https://github.com/PCHANUL/IIIF/issues
- **Milestones**: https://github.com/PCHANUL/IIIF/milestones
- **GitHub CLI Docs**: https://cli.github.com/manual/

---

## ❓ FAQ

### Q: Issue가 너무 많아요. 어떻게 관리하나요?
A: Milestone과 Label을 활용하세요. 현재 Phase의 P0/P1만 집중하면 됩니다.

### Q: Project Board에 Issue가 자동 추가 안 돼요.
A: 스크립트 실행 시 `--project` 옵션을 확인하세요. 또는 수동으로 추가 가능합니다.

### Q: Milestone 날짜를 변경하고 싶어요.
A: GitHub에서 직접 수정하거나 API로 업데이트하세요.

```bash
gh api "/repos/PCHANUL/IIIF/milestones/1" \
  -X PATCH \
  -f due_on="2026-03-10T23:59:59Z"
```

### Q: 기존 Issue를 업데이트하고 싶어요.
A: `--update-existing` 옵션 사용:

```bash
./scripts/gh_issues_create_from_checklist_md.sh \
  --file Docs/flutter/FLUTTER_TODO.md \
  --update-existing
```

---

**Happy Coding! 🚀**
