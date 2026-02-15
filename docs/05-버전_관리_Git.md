# 버전 관리 (Git / GitHub)

수정사항은 **받은 지시 → 진행한 과정**을 커밋 메시지와 CHANGELOG로 요약해 버전별로 관리합니다.

---

## 현재 상태 (v0.1.0)

- **초기 커밋 완료:** `chore: 초기 버전 v0.1.0 - VHDL 파서 백엔드 및 기획 문서`
- **CHANGELOG.md:** 버전별 요약 (받은 지시 / 진행한 과정)
- **생성물 제외:** `top_ast_tree.json`, `*_output.json` 등은 `.gitignore`로 커밋에서 제외

---

## GitHub에 올리기 (최초 1회)

1. **GitHub에서 저장소 생성**
   - https://github.com/new
   - Repository name: `vhdl_Viz` (또는 원하는 이름)
   - Public, **Add a README** 체크 해제 (이미 로컬에 있음)

2. **원격 추가 후 푸시**
   ```bash
   git remote add origin https://github.com/rldhkstopic/vhdl_Viz.git
   git branch -M main
   git push -u origin main
   ```
   (저장소 이름/경로를 바꿨다면 `origin` URL만 수정)

---

## 앞으로 커밋 규칙

- **커밋 메시지:** `[영역] 받은 지시 요약 → 진행한 작업`
  - 예: `feat(ast): process 노드 추출 추가 → extract_process_blocks 구현`
  - 예: `docs: REQ-10 추가 → CHANGELOG 갱신`
- **CHANGELOG.md:** 새 버전(예: [0.2.0]) 추가 시
  - **받은 지시 / 목표**
  - **진행한 과정** (항목별로 간단히)

이렇게 하면 “어떤 명령으로 어떤 작업을 했는지”가 버전별로 남습니다.
