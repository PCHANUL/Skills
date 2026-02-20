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