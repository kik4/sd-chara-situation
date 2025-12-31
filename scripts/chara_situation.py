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
    
    def process(self, p):
        self.load_data()

        for i, prompt in enumerate(p.all_prompts):
            # バッチ処理の場合、各プロンプトに対応するseedを取得
            seed = p.all_seeds[i] if i < len(p.all_seeds) else p.seed
            p.all_prompts[i] = self.expand_prompt(prompt, seed)
    
    def expand_prompt(self, prompt, seed):
        # @chara:name または @chara:random を検出
        chara_match = re.search(r'@chara:(\w+)', prompt)
        if not chara_match:
            return prompt

        chara_name = chara_match.group(1)

        # キャラクターのランダム選択
        if chara_name == "random":
            rng = random.Random(seed)
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
                # seedを使って決定的にランダム選択
                rng = random.Random(seed)
                sit_name = rng.choice(list(self.situations.keys()))
            
            if sit_name in self.situations:
                situation = self.situations[sit_name]
            else:
                print(f"[CharaSituation] Unknown situation: {sit_name}")
        
        # プロンプト組み立て
        parts = []
        exclude = situation.get("exclude", []) if situation else []
        
        # キャラの各タグを処理
        for key, value in chara.items():
            if key not in exclude and value:
                parts.append(value)
        
        # シチュエーションの extra を追加
        if situation:
            if situation.get("extra"):
                parts.append(situation["extra"])
            if situation.get("prompt"):
                parts.append(situation["prompt"])
        
        # 組み立て
        replacement = ", ".join(parts)
        
        # @chara:xxx と @situation:xxx を置換
        result = re.sub(r'@chara:\w+', '', prompt)
        result = re.sub(r'@situation:\w+', '', result)
        result = re.sub(r'^[\s,]+', '', result)
        result = re.sub(r'[\s,]+$', '', result)
        
        # 置換したパーツを先頭に
        if result:
            result = f"{replacement}, {result}"
        else:
            result = replacement
        
        # 連続カンマを整理
        result = re.sub(r',\s*,+', ',', result)
        result = re.sub(r'\s+', ' ', result)
        
        print(f"[CharaSituation] {chara_name} + {sit_name} => {result}")
        
        return result
