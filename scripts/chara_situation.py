import modules.scripts as scripts
import random
import re
import os

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "pyyaml"])
    import yaml


class CharaSituationScript(scripts.Script):

    def __init__(self):
        # このスクリプトファイルの場所から拡張機能のルートを特定
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extension_dir = os.path.dirname(script_dir)  # scriptsの親ディレクトリ
        self.data_dir = os.path.join(extension_dir, "data")

    def load_yaml(self, filename):
        """指定されたYAMLファイルを読み込む（毎回読み込んで編集を即反映）"""
        yaml_path = os.path.join(self.data_dir, f"{filename}.yaml")

        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            print(f"[CharaSituation] WARNING: {filename}.yaml not found at {yaml_path}")
            return {}
    
    def title(self):
        return "Chara Situation"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def before_process_batch(self, p, *args, **kwargs):
        """
        before_process_batchはLORA抽出の前に呼ばれるため、ここでプロンプトを展開する
        ただしseedはまだ確定していないので、seed=0で仮展開してLORAタグを抽出させる
        """
        # p.promptsがまだNoneの場合は何もしない（初期化前）
        if p.prompts is None or len(p.prompts) == 0:
            return

        # 元のプロンプトを保存（LORA抽出前）
        if not hasattr(p, 'chara_situation_original_prompts'):
            p.chara_situation_original_prompts = p.prompts.copy()

        # seed=0で仮展開してLORAタグを抽出させる（ログは出力しない）
        for i in range(len(p.prompts)):
            expanded = self.expand_prompt(p.prompts[i], 0, silent=True)
            p.prompts[i] = expanded

    def process_batch(self, p, *args, **kwargs):
        """
        process_batchはseed値が確定した後に呼ばれるため、
        ここで正しいseedを使って再展開する（randomの再現性を保つため）
        """
        # 元のプロンプトを取得（before_process_batch()で保存したもの）
        if hasattr(p, 'chara_situation_original_prompts'):
            original_prompts = p.chara_situation_original_prompts
        else:
            # フォールバック：all_promptsを使用
            original_prompts = p.all_prompts if hasattr(p, 'all_prompts') else p.prompts

        for i in range(len(p.prompts)):
            # バッチ処理の場合、各プロンプトに対応するseedを取得
            seed = p.all_seeds[i] if i < len(p.all_seeds) else p.all_seeds[0]

            # 元のプロンプトから正しいseedで再展開
            if i < len(original_prompts):
                source_prompt = original_prompts[i]
            else:
                source_prompt = p.prompts[i]

            expanded = self.expand_prompt(source_prompt, seed)

            # 両方を更新
            p.prompts[i] = expanded
            if i < len(p.all_prompts):
                p.all_prompts[i] = expanded
    
    def expand_prompt(self, prompt, seed, silent=False):
        # seedを使って決定的な乱数生成器を作成
        rng = random.Random(seed)

        # @filename:key の形式をすべて検出
        # filenameはサブディレクトリをサポートするため、パス区切り文字(/)を含む
        tag_pattern = r'@([\w/]+):(\w+)'
        matches = list(re.finditer(tag_pattern, prompt))

        if not matches:
            return prompt

        # Step 1: すべてのタグを解析して、データを読み込む
        tag_data = []
        for match in matches:
            filename = match.group(1)
            key = match.group(2)
            full_tag = match.group(0)

            # YAMLファイルを読み込む
            data = self.load_yaml(filename)

            if not data:
                print(f"[CharaSituation] File not found or empty: {filename}.yaml")
                continue

            # random キーの処理
            if key == "random":
                if data:
                    key = rng.choice(list(data.keys()))
                else:
                    print(f"[CharaSituation] No keys available in {filename}.yaml for random selection")
                    continue

            # キーが存在するか確認
            if key not in data:
                print(f"[CharaSituation] Key '{key}' not found in {filename}.yaml")
                continue

            entry = data[key]
            tag_data.append({
                'full_tag': full_tag,
                'filename': filename,
                'key': key,
                'entry': entry
            })

        # Step 2: すべてのシチュエーション定義(exclude/includeフィールドを持つもの)を収集
        all_excludes = []
        all_includes = []
        has_include = False
        has_exclude = False

        for item in tag_data:
            entry = item['entry']
            if isinstance(entry, dict):
                # excludeとincludeの同時指定をチェック（同一エントリ内）
                if 'exclude' in entry and 'include' in entry:
                    print(f"[CharaSituation] ERROR: Cannot specify both 'exclude' and 'include' in {item['filename']}:{item['key']}")
                    continue

                if 'exclude' in entry:
                    all_excludes.extend(entry.get('exclude', []))
                    has_exclude = True
                elif 'include' in entry:
                    all_includes.extend(entry.get('include', []))
                    has_include = True

        # includeとexcludeの混在チェック（複数のシチュエーション間）
        if has_include and has_exclude:
            print(f"[CharaSituation] ERROR: Cannot mix 'include' and 'exclude' across multiple situations")
            # エラー時はタグを展開せずに元のプロンプトを返す
            return prompt

        # Step 3: 各タグを展開
        result = prompt
        expanded_tags = []

        for item in tag_data:
            entry = item['entry']
            full_tag = item['full_tag']
            filename = item['filename']
            key = item['key']

            # エントリがシチュエーション定義かキャラクター定義かを判定
            if isinstance(entry, dict) and ('exclude' in entry or 'include' in entry):
                # シチュエーション定義の場合
                expanded = self.expand_situation(entry)
            else:
                # キャラクター定義の場合 - all_excludes/all_includesを使用
                if has_include:
                    expanded = self.expand_character_with_include(entry, all_includes)
                else:
                    expanded = self.expand_character_with_exclude(entry, all_excludes)

            expanded_tags.append(f"{filename}:{key}")

            # タグを展開された内容で置換
            result = result.replace(full_tag, expanded, 1)

        # 連続カンマやスペースを整理（改行と行末のカンマは保持）
        result = re.sub(r',[ \t]*,+', ',', result)  # 連続カンマを1つに
        result = re.sub(r'^[ \t]*,[ \t]*', '', result, flags=re.MULTILINE)  # 各行の先頭のカンマを削除（改行は保持）
        result = re.sub(r'[ \t]+', ' ', result)  # 連続スペース（タブも含む）を1つのスペースに（改行は保持）

        if expanded_tags and not silent:
            print(f"[CharaSituation] {' + '.join(expanded_tags)} => {result}")

        return result

    def expand_character_with_exclude(self, chara, excludes):
        """キャラクター定義を展開（exclude方式）"""
        if not isinstance(chara, dict):
            return str(chara)

        chara_parts = []

        # キャラの各タグを処理（excludeに含まれないものを出力）
        for key, value in chara.items():
            if key not in excludes and value:
                # valueが配列の場合は結合、文字列の場合はそのまま
                if isinstance(value, list):
                    chara_parts.append(", ".join(str(v) for v in value))
                else:
                    chara_parts.append(str(value))

        return ", ".join(chara_parts)

    def expand_character_with_include(self, chara, includes):
        """キャラクター定義を展開（include方式）"""
        if not isinstance(chara, dict):
            return str(chara)

        chara_parts = []

        # キャラの各タグを処理（includeに含まれるもののみ出力）
        for key, value in chara.items():
            if key in includes and value:
                # valueが配列の場合は結合、文字列の場合はそのまま
                if isinstance(value, list):
                    chara_parts.append(", ".join(str(v) for v in value))
                else:
                    chara_parts.append(str(value))

        return ", ".join(chara_parts)

    def expand_situation(self, situation):
        """シチュエーション定義を展開"""
        if not isinstance(situation, dict):
            return str(situation)

        situation_parts = []
        if situation.get("prompt"):
            prompt_value = situation["prompt"]
            # promptが配列の場合は結合、文字列の場合はそのまま
            if isinstance(prompt_value, list):
                situation_parts.extend(prompt_value)
            else:
                situation_parts.append(str(prompt_value))

        return ", ".join(situation_parts)
