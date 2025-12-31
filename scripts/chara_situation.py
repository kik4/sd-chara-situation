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
        self.characters = {}
        self.situations = {}
    
    def load_data(self):
        """YAMLファイルを読み込む（毎回読み込んで編集を即反映）"""
        chars_path = os.path.join(self.data_dir, "characters.yaml")
        sits_path = os.path.join(self.data_dir, "situations.yaml")

        if os.path.exists(chars_path):
            with open(chars_path, 'r', encoding='utf-8') as f:
                self.characters = yaml.safe_load(f) or {}
        else:
            print(f"[CharaSituation] ERROR: characters.yaml not found at {chars_path}")

        if os.path.exists(sits_path):
            with open(sits_path, 'r', encoding='utf-8') as f:
                self.situations = yaml.safe_load(f) or {}
        else:
            print(f"[CharaSituation] ERROR: situations.yaml not found at {sits_path}")
    
    def title(self):
        return "Chara Situation"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def process_batch(self, p, *args, **kwargs):
        """
        process_batchはseed値が確定した後に呼ばれるため、
        -1が実際のseed値に置き換わった状態でプロンプトを展開できる
        """
        self.load_data()

        for i, prompt in enumerate(p.prompts):
            # バッチ処理の場合、各プロンプトに対応するseedを取得
            seed = p.all_seeds[i] if i < len(p.all_seeds) else p.all_seeds[0]
            expanded = self.expand_prompt(prompt, seed)
            p.prompts[i] = expanded
            # all_promptsも更新して画像メタデータに反映
            if i < len(p.all_prompts):
                p.all_prompts[i] = expanded
    
    def expand_prompt(self, prompt, seed):
        # seedを使って決定的な乱数生成器を作成
        rng = random.Random(seed)

        # @chara:name または @chara:random を検出
        chara_match = re.search(r'@chara:(\w+)', prompt)
        if not chara_match:
            return prompt

        chara_name = chara_match.group(1)

        # キャラクターのランダム選択
        if chara_name == "random":
            chara_name = rng.choice(list(self.characters.keys()))

        if chara_name not in self.characters:
            print(f"[CharaSituation] Unknown character: {chara_name}")
            return prompt

        chara = self.characters[chara_name]

        # @situation:name または @situation:random を検出
        sit_match = re.search(r'@situation:(\w+)', prompt)
        situation = None
        sit_name = ""

        if sit_match:
            sit_name = sit_match.group(1)
            if sit_name == "random":
                # 同じrngを使って次の選択を行う
                sit_name = rng.choice(list(self.situations.keys()))
            
            if sit_name in self.situations:
                situation = self.situations[sit_name]
            else:
                print(f"[CharaSituation] Unknown situation: {sit_name}")
        
        # キャラクタープロンプトの組み立て
        chara_parts = []
        exclude = situation.get("exclude", []) if situation else []

        # キャラの各タグを処理
        for key, value in chara.items():
            if key not in exclude and value:
                chara_parts.append(value)

        chara_prompt = ", ".join(chara_parts)

        # シチュエーションプロンプトの組み立て
        situation_parts = []
        if situation and situation.get("prompt"):
            prompt_value = situation["prompt"]
            # promptが配列の場合は結合、文字列の場合はそのまま
            if isinstance(prompt_value, list):
                situation_parts.extend(prompt_value)
            else:
                situation_parts.append(prompt_value)

        situation_prompt = ", ".join(situation_parts) if situation_parts else ""

        # @chara:xxx を実際のキャラクタープロンプトに置換
        result = re.sub(r'@chara:\w+', chara_prompt, prompt)

        # @situation:xxx を実際のシチュエーションプロンプトに置換
        if situation_prompt:
            result = re.sub(r'@situation:\w+', situation_prompt, result)
        else:
            # situationが指定されていない場合は@situation:xxxを削除
            result = re.sub(r'@situation:\w+', '', result)

        # 連続カンマやスペースを整理
        result = re.sub(r',\s*,+', ',', result)
        result = re.sub(r'^\s*,\s*', '', result)  # 先頭のカンマを削除
        result = re.sub(r'\s*,\s*$', '', result)  # 末尾のカンマを削除
        result = re.sub(r'\s+', ' ', result)  # 連続スペースを1つに
        
        print(f"[CharaSituation] {chara_name} + {sit_name} => {result}")
        
        return result
