四边界 `top / bottom / left / right`，`while top <= bottom and left <= right` 里依次走 → ↓ ← ↑，每走完一条边就把那条边界往里收一格。

⚠ ← 前守 `top <= bottom`，↑ 前守 `left <= right`，否则只剩单行 / 单列时会被输出两次。
