# Skills

이 레포지토리는 AI 기반으로 소프트웨어 프로젝트를 관리하고 실행하기 위한 다양한 스킬(가이드 및 자동화 스크립트)을 포함하고 있습니다. 핵심이 되는 전체 운영 가이드는 `project-workflow` 스킬에 정의되어 있습니다.

## Project Workflow 개요

`project-workflow`는 Antigravity Skill System을 사용하여 소프트웨어 프로젝트를 자율적으로 실행하는 표준 작업 절차(SOP)를 문서화한 가이드입니다. 워크플로우는 크게 4개의 단계로 이루어져 있습니다.

### 1. Planning Phase (`project-planner`)
- **목표**: 어떤 기능을 만들지 정의합니다.
- **주요 작업**: 프로젝트 마일스톤과 세부 이슈들을 정리하여 `PROJECT_TODO.md` 문서를 작성합니다.

### 2. Setup Phase (`project-setup`)
- **목표**: 작성된 계획을 GitHub에 동기화합니다.
- **주요 작업**: `sync_to_github.py` 스크립트를 사용하여 GitHub 공간에 마일스톤과 이슈를 생성하고, 안전한 작업을 위한 **통합 브랜치(`milestone/phase-1` 등)**를 자동 생성합니다.

### 3. Execution Phase (`project-driver`)
- **목표**: 계획을 바탕으로 작업을 자율적으로 실행합니다. `project-driver` 루프가 이슈들을 순차적으로 처리합니다.
  1. **Start (`project-task-start`)**: 이슈에 대한 피처 브랜치(feat/issue-N)를 생성하거나, 이미 있다면 해당 브랜치에서 재개합니다.
  2. **Implementation (`project-task-implementer`)**: `track_progress.py`를 외부 뇌(External Brain)처럼 활용해 목표를 세분화하고 코드를 작성합니다.
  3. **Finish (`project-task-finish`)**: 수정된 사항을 커밋하고 PR(Pull Request)을 생성합니다.
  4. **Review (`project-task-review`)**: PR에 대한 코드 리뷰를 진행합니다. **품질 검수에 실패하면 다시 구현(Implementation) 단계로 돌아가 수정**하고, **통과하면 통합 브랜치에 자동으로 병합**합니다.

### 4. Completion Phase
- **목표**: 달성한 마일스톤을 배포합니다.
- **주요 작업**: 통합 브랜치의 모든 작업이 병합되어 완료되면, 최종적으로 `main` 브랜치로 PR을 날려 배포 준비를 마칩니다.

> 각 스킬 폴더 내부의 `SKILL.md`를 확인하면 구체적인 명령어 사용 방법과 작동 원리를 파악할 수 있습니다.

---

## Quick Start — Install

### 원라인 설치 (새 프로젝트에 처음 적용할 때)

```bash
curl -fsSL https://raw.githubusercontent.com/PCHANUL/Skills/main/install.sh | bash
```

### 기존 프로젝트에 서브모듈로 추가

```bash
git submodule add https://github.com/PCHANUL/Skills.git Skills
bash Skills/install.sh
```

### 설치 과정에서 묻는 항목

1. **호스트 에이전트 선택** — 사용 중인 AI 에이전트에 맞는 스킬 디렉토리를 선택합니다.
   ```
   1) Universal / Multiple (.agents)
   2) Antigravity          (.agent)
   3) Claude Code          (.claude)
   4) Cline                (.cline)
   ...
   ```
   선택하면 해당 경로(예: `.agent/skills/`)에 스킬들이 심볼릭 링크로 연결됩니다.

2. **GitHub Actions 설치 여부** — CI/CD 자동화 워크플로우를 프로젝트에 설치할지 선택합니다.
   - `agent.yml` — 이슈 코멘트로 AI 에이전트를 트리거하는 Cloud Agent
   - `ci-auto-fix.yml` — 테스트 실패 시 자동으로 에이전트를 호출하는 Self-Healing CI

### 업데이트

```bash
bash ~/Skills/install.sh --update
```

---

## 사용법 — Project Workflow

`project-workflow`는 프로젝트의 기획부터 배포까지 전체 사이클을 자동화하는 마스터 가이드입니다.

### Step 1. 기획 (Planning)

AI 에이전트에게 프로젝트를 설명하면, `project-planner` 스킬이 마일스톤과 이슈를 정리한 `PROJECT_TODO.md`를 작성합니다.

```
> "project-planner로 Todo 앱을 기획해줘"
```

### Step 2. GitHub 동기화 (Setup)

작성된 계획을 GitHub 마일스톤 및 이슈로 동기화합니다.

```bash
python3 ~/Skills/project-setup/scripts/sync_to_github.py \
  --file PROJECT_TODO.md \
  --repo owner/repo
```

### Step 3. 자동 실행 (Execution)

`project-driver`가 이슈를 순서대로 처리합니다. 각 이슈마다 브랜치 생성 → 구현 → PR 생성 → 코드 리뷰 → 병합 사이클을 자동으로 수행합니다.

```bash
python3 ~/Skills/project-driver/scripts/drive.py --milestone "Phase 1: MVP"
```

중간에 중단된 경우 아래 명령으로 이어서 재개할 수 있습니다.

```bash
python3 ~/Skills/project-driver/scripts/drive.py --resume
```

### Step 4. 배포 (Completion)

마일스톤의 모든 이슈가 완료되면, 통합 브랜치(`milestone/phase-1`)에서 `main`으로의 Release PR이 자동 생성됩니다.

### 주요 명령어 요약

| 단계 | 명령어 |
| :--- | :--- |
| **기획** | `PROJECT_TODO.md` 작성 (에이전트에게 요청) |
| **동기화** | `python3 ~/Skills/project-setup/scripts/sync_to_github.py --file PROJECT_TODO.md --repo owner/repo` |
| **실행** | `python3 ~/Skills/project-driver/scripts/drive.py --milestone "Phase 1: MVP"` |
| **재개** | `python3 ~/Skills/project-driver/scripts/drive.py --resume` |
| **진행률** | `python3 ~/Skills/project-task-implementer/scripts/track_progress.py list` |