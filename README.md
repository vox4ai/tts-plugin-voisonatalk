# tts-plugin-voisonatalk

[VoiSona Talk](https://voisona.com/talk/) Editor 組み込みの REST API を使用して、本体から音声を発声させるための `tts-plugin-bridge` プラグインです。

## ⚠️ 仕様上の注意
このプラグインは **VoiSona Talk 本体（スピーカー）からの直接発声** を目的としています。
そのため、`synthesize` メソッドの戻り値である `TTSResponse` には **音声データ（audio_data）は含まれません**。


## 📦 インストール
```bash
uv add tts-plugin-bridge tts-plugin-voisonatalk
```

## ⚙️ 前提条件
- VoiSona Talk エディタが起動しており、REST API サーバーが有効になっていること。
  - `設定 -> API -> REST API Server` を ON に設定。
- .envファイルにWindows側のHOST名/Port、Basic 認証（User/Password）を設定。

## 🖥️ WSL2 からの使用
WSL2 上から Windows 側で動いている VoiSona Talk を呼び出す場合は、`localhost`あるいは Windows 側の IP アドレスを指定する必要があります。

```python
# Windows 側の IP アドレスを取得して指定
# 例: http://192.168.1.10:32766
skill = TTSSkill(
    default_engine="voisonatalk", 
    server_url="http://<WINDOWS_IP>:32766"
)
```

## 🧩 使い方
```python
import asyncio
from tts_plugin_bridge import TTSSkill

async def main():
    # 認証情報が必要な場合は環境変数 VOISONA_USER / VOISONA_PASS または引数で指定
    async with TTSSkill(default_engine="voisonatalk") as skill:
        res = await skill.synthesize(
            text="こんにちは。ボイソナトーク本体からのテスト発声です。",
            speed=1.2,
            extra={
                "voice_name": "tanaka-san_ja_JP",
                "style_weights": [1.0, 0.0, 0.0, 0.0, 0.0]
            }
        )
        
        if res["status"] == "ok":
            print("✅ 発声成功（本体から音が出ました）")

asyncio.run(main())
```

## 📜 ライセンス
MIT License
