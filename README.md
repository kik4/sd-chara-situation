# sd-chara-situation

Stable Diffusion WebUI / reForge 用の拡張機能です。キャラクターと状況を組み合わせて、矛盾のないプロンプトをランダム生成します。

## 概要

この拡張機能は、キャラクターの特徴を細かく定義し、状況に応じて不要な要素を自動的に除外することで、自然で矛盾のないプロンプトを生成します。

例えば「ビーチ」の状況では、キャラクターの通常の服装を除外し、ビキニや裸足などの状況に合った服装に自動的に置き換えます。

## インストール

1. Stable Diffusion WebUI / reForge の `extensions` フォルダにこのリポジトリをクローン:

```bash
cd extensions
git clone <repository-url> sd-chara-situation
```

2. WebUI を再起動

依存ライブラリ `pyyaml` は初回実行時に自動インストールされます。

## 使い方

### 基本的な使い方

プロンプト欄に以下の形式で入力:

```
@chara:キャラ名 @situation:状況名 その他のプロンプト
```

**例:**

```
@chara:reimu @situation:beach masterpiece, best quality
```

**生成されるプロンプト:**

```
1girl, black hair, hair tubes, red eyes, medium breasts, bikini, barefoot, standing, wet, beach, ocean, sunny, outdoors, blue sky, masterpiece, best quality
```

### ランダムな状況

状況をランダムに選択したい場合は `@situation:random` を使用:

```
@chara:reimu @situation:random masterpiece, best quality
```

## データファイルの編集

### キャラクター定義 (`data/characters.yaml`)

キャラクターの特徴を要素ごとに定義します:

```yaml
reimu:
  base: 1girl
  hair: black hair, hair tubes
  eye: red eyes
  top: white blouse, red vest
  bottom: red hakama
  shoes: brown boots
  accessory: hair ribbon, detached sleeves, yellow ascot
  body: medium breasts
```

**要素の種類:**

- `base`: 基本タグ (1girl, 1boy など)
- `hair`: 髪型・髪色
- `eye`: 目の色
- `top`: 上半身の服装
- `bottom`: 下半身の服装
- `shoes`: 履物
- `accessory`: アクセサリ・小物
- `body`: 体型

### 状況定義 (`data/situations.yaml`)

状況と、除外するキャラクター要素を定義します:

```yaml
beach:
  prompt: beach, ocean, sunny, outdoors, blue sky
  extra: bikini, barefoot, standing, wet
  exclude:
    - top
    - bottom
    - shoes
    - accessory
```

**パラメータ:**

- `prompt`: 背景・環境のプロンプト
- `extra`: この状況特有の服装・ポーズ・アイテム
- `exclude`: 除外するキャラクター要素のリスト

### 矛盾防止の仕組み

`exclude` で指定した要素はキャラクター定義から除外され、代わりに `extra` の内容が使用されます。

**例: beach (ビーチ)**

- 除外: `top`, `bottom`, `shoes`, `accessory` (通常の服装)
- 追加: `bikini, barefoot, standing, wet` (ビーチに適した服装)

**例: classroom (教室)**

- 除外: `top`, `bottom`, `accessory` (通常の服装)
- 追加: `school uniform, sitting, looking at viewer` (制服姿)

## プリセット状況

現在定義されている状況:

- `classroom`: 教室(制服姿)
- `beach`: ビーチ(ビキニ)
- `sleeping`: 寝室(パジャマ)
- `bath`: 温泉(裸)
- `bunny`: カジノ(バニースーツ)
- `maid`: 洋館(メイド服)
- `casual`: 街中(カジュアル服)

## キャラクターの追加

`data/characters.yaml` に新しいキャラクターを追加できます:

```yaml
your_character:
  base: 1girl
  hair: blue hair, short hair
  eye: green eyes
  top: jacket, shirt
  bottom: skirt
  shoes: sneakers
  accessory: necklace
  body: large breasts
```

## 状況の追加

`data/situations.yaml` に新しい状況を追加できます:

```yaml
your_situation:
  prompt: your background tags
  extra: your outfit and pose tags
  exclude:
    - top
    - bottom
```

## 動作仕様

- YAML ファイルは毎回の生成時に読み込まれるため、編集後すぐに反映されます(WebUI の再起動不要)
- 生成されたプロンプトはコンソールに出力されます
- バッチ生成にも対応しています

## ライセンス

MIT License

## 作者

kik4
