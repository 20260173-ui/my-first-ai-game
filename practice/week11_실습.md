# Week 11 실습

## 오늘 한 것

- PyInstaller 설치 및 빌드
- `resource_path()` 함수 추가
- `--add-data` 옵션으로 에셋 포함
- `.exe` 실행 확인

---


## `resource_path()`를 써야 하는 이유

PyInstaller는 임시폴더에 압축을 풀면서 그 경로를 `sys._MEIPASS` 변수에 저장해둠.  
(`sys._MEIPASS` 가 있으면 → 빌드된 실행 파일 안에서 돌고 있다는 뜻)

exe 위치(CWD)와 실제 파일 위치(임시 폴더)가 다르기 때문에 오류가 발생함

`resource_path()`는 개발 중과 빌드 후 모두 동작하는 경로를 반환한다.  
그러므로 게임 코드에 파일을 열거나 로드하는 곳에 전부 `resource_path`를 사용한 경로로 수정해야한다.

---

## 빌드 명령어

```bash
pip install pyinstaller
pyinstaller space_dodger.py
```

---

## `resource_path()` 함수

```python
import sys, os

def resource_path(relative_path):
    #"""개발 중과 빌드 후 모두 동작하는 경로 반환"""
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)

print(resource_path("assets/enemy.png"))
```

---

## 파일을 열거나 로드하는 곳에 `resource_path` 추가

```python
# 변경 전
pygame.mixer.music.load("./assets/dodge_bgm.wav")

# 변경 후
pygame.mixer.music.load(resource_path("./assets/dodge_bgm.wav"))
```

---

## 에셋 추가 및 빌드

```bash
pyinstaller --onefile --add-data "assets;assets" --name=space_driver space_dodger.py
```

이후 `.exe` 파일 실행 후 오류 확인
