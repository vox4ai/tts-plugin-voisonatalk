# tts-plugin-voisonatalk

[VoiSona Talk](https://voisona.com/talk/) Editor 組み込みの REST API を使用して、`tts-plugin-bridge` から音声を発声させるためのプラグインです。

## 🛠 概要
- **役割**: VoiSona Talk 本体（スピーカー）からの直接発声を実現する。
- **主要機能**:
    - VoiSona Talk の REST API を介した音声制御。
    - 話者、スタイル、重みなどの詳細なパラメータ指定。

## ⚠️ 注意事項
- **音声データは含まれません**: このプラグインは「本体からの発声」を目的としているため、`synthesize` メソッドの戻り値に音声データは含まれません。

## ⚙️ 前提条件
- **VoiSona Talk エディタ** が起動しており、REST API サーバーが有効であること。

## 🚀 開発・実行
- **パッケージ管理**: `uv`
- **テスト**: `pytest`

## 🔗 関連リポジトリ
- `repos/tts-plugin-bridge`: コアフレームワーク
