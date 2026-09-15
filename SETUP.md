# 깃헙에 올리기

이 폴더가 그대로 저장소 루트다. 아래를 순서대로 실행하면 된다.

## 1. 저장소 만들기

github.com 에서 새 저장소를 만든다. 이름 제안: `tetris-dynamic-tilings`
README / .gitignore / license 는 **추가하지 말 것** (여기 이미 있다).

## 2. 올리기

```sh
cd tetris-dynamic-tilings
git init
git add .
git commit -m "Tetromino tilings with line clears: classification and proofs"
git branch -M main
git remote add origin https://github.com/<계정>/tetris-dynamic-tilings.git
git push -u origin main
```

`CITATION.cff` 의 repository-code 와 authors 를 실제 계정으로 고칠 것.

## 3. 확인

- `make` 가 bin/ 에 실행파일을 만드는지
- `make check` 가 정리 4, 5 와 카운팅 표를 재현하는지

## 참고

- 공개(public) 로 두는 걸 권한다. 논문 투고 시 arXiv 나 저널에서 코드 링크로 쓸 수 있다.
- 볼트 백업 레포(DevVault)와는 별개로 두는 게 낫다. 이건 공개 연구물이다.
