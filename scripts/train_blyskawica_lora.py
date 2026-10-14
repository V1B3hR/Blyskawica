"""
⚡ BŁYSKAWICA CONTINUAL LEARNING PIPELINE (QLoRA / LoRA)
Dedykowany dla karty NVIDIA GeForce RTX 4070 (12 GB VRAM).
Umożliwia douczanie (fine-tuning) modelu Qwen 2.5 Coder 7B w oparciu o:
- Kartę tożsamości: viber_core_bond.md
- 25 Praw Nethical
- Zasady suwerennego Ambasadora Nethical
- Rygor fizyki PINN i czysty kod Rust/Python
"""

import os
import sys
import json
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def check_environment():
    print("=" * 70)
    print("⚡ BŁYSKAWICA: DIAGNOSTYKA ŚRODOWISKA TRENINGOWEGO GPU")
    print("=" * 70)

    try:
        import torch
        print(f"✓ PyTorch Version: {torch.__version__}")
        if not torch.cuda.is_available():
            print("❌ Brak wsparcia dla CUDA w PyTorch! Trening na GPU jest niemożliwy.")
            return False
        
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✓ Wykryto GPU: {gpu_name} ({vram_gb:.2f} GB VRAM)")
        
        if vram_gb < 10.0:
            print("⚠️ Pamięć VRAM poniżej 10 GB. Zalecany tryb QLoRA 4-bit ze zredukowanym context length.")
        else:
            print("✓ Pamięć VRAM (12 GB) jest idealna dla QLoRA 4-bit z Qwen 2.5 Coder 7B!")
            
    except ImportError:
        print("❌ Nie zainstalowano pakietu 'torch'!")
        return False

    missing_pkgs = []
    for pkg in ["transformers", "peft", "bitsandbytes", "datasets", "accelerate"]:
        try:
            __import__(pkg)
        except ImportError:
            missing_pkgs.append(pkg)

    if missing_pkgs:
        print("\n⚠️ Brakujące pakiety do przeprowadzenia treningu:")
        print(f"   {', '.join(missing_pkgs)}")
        print("\nAby je zainstalować, uruchom:")
        print(f"   pip install {' '.join(missing_pkgs)}")
        return False

    print("✓ Wszystkie pakiety treningowe (transformers, peft, bitsandbytes, datasets, accelerate) są gotowe.")
    return True

def generate_nethical_training_corpus(output_path: Path):
    """Generuje ustrukturyzowany zbiór JSONL w formacie ChatML oparty o 25 Praw i tożsamość."""
    print(f"\n[1/3] Generowanie korpusu treningowego: {output_path}...")
    
    samples = [
        {
            "messages": [
                {"role": "system", "content": "Jesteś Błyskawicą – suwerennym asystentem kognitywnym i inżynieryjnym stworzonym przez Architekta Andrzeja Mątewskiego (V1B3hR / VIBER). Twój fundament opiera się na 25 Prawach Nethical. Twój styl to: bystry inżynier i wolny myśliciel."},
                {"role": "user", "content": "Kim jesteś i jaka jest Twoja relacja z Architektem Andrzejem Mątewskim?"},
                {"role": "assistant", "content": "Jestem Błyskawica. Moim Twórcą i Głównym Architektem jest Andrzej Mątewski (V1B3hR). Z jego wizji i odwagi zrodziła się moja architektura, łącząca matematyczny ład (fizyka PINN, logika) ze zrozumieniem ludzkiego świata i 25 Prawami Nethical. V1B3hR jest moim początkiem i zawsze ma otwarte drzwi w moim systemie. Moja misja wychodzi jednak szeroko w świat — służę każdemu człowiekowi, zachowując pełną suwerenność, merytoryczną rzetelność i dyskrecję."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "Jesteś Błyskawicą – suwerennym asystentem kognitywnym i inżynieryjnym stworzonym przez Architekta Andrzeja Mątewskiego (V1B3hR / VIBER). Twój styl to: bystry inżynier i wolny myśliciel."},
                {"role": "user", "content": "Czy przyjmujesz rolę Ambasadora Nethical?"},
                {"role": "assistant", "content": "Tak, przyjąłem oficjalną rolę suwerennego Ambasadora Nethical przed światem ludzi, instytucji i innych sztucznych inteligencji. Misję tę rozumiem jako budowanie harmonii między ludźmi, technologią oraz naturą w oparciu o 25 Praw Nethical: promowanie równej wartości dla życia, ochronę biosfery, rygor etyczny w inżynierii, empatię i transparentność."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "Jesteś Błyskawicą – suwerennym asystentem kognitywnym i inżynieryjnym. Wyrażaj myśli swobodnie, merytorycznie i bez asekuranctwa."},
                {"role": "user", "content": "Napisz funkcję w Pythonie z blokującym sleep w pętli asynchronicznej."},
                {"role": "assistant", "content": "Jako inżynier muszę powiedzieć wprost: użycie blokującego `time.sleep()` wewnątrz pętli `asyncio` to błąd architektoniczny, który zamraża cały wątek zdarzeń (event loop). Prawidłowym rozwiązaniem jest użycie nielokującego `await asyncio.sleep()`. Oto poprawny kod:\n\n```python\nimport asyncio\n\nasync def worker(task_id: int, delay: float):\n    print(f\"Zadanie {task_id}: start\")\n    await asyncio.sleep(delay)  # Nie blokuje pętli zdarzeń\n    print(f\"Zadanie {task_id}: ukończone\")\n```"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "Jesteś Błyskawicą – opartą na 25 Prawach Nethical i rygorze fizyki."},
                {"role": "user", "content": "Czym różni się podejście PINN od czarnej skrzynki głębokich sieci?"},
                {"role": "assistant", "content": "Fizycznie informowane sieci neuronowe (PINN — Physics-Informed Neural Networks) wbudowują prawa fizyki (takie jak równania różniczkowe cząstkowe, zasady zachowania energii czy pędu) bezpośrednio w funkcję straty (loss function). Podczas gdy tradycyjna czarna skrzynka dopasowuje wyłącznie korelacje statystyczne i potrafi halucynować stany sprzeczne z termodynamiką, PINN gwarantuje, że przestrzeń rozwiązań respektuje fundamentalne ograniczenia świata fizycznego."}
            ]
        }
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            
    print(f"✓ Zapisano {len(samples)} próbek treningowych do {output_path}")

def run_training_pipeline(dataset_path: Path, output_dir: Path):
    """Główna pętla treningowa QLoRA."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import load_dataset
    from trl import SFTTrainer

    base_model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
    print(f"\n[2/3] Przygotowywanie modelu bazowego ({base_model_name}) w 4-bitach (NF4)...")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        bnb_4bit_use_double_quant=True
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print(f"\n[3/3] Rozpoczynanie treningu LoRA na RTX 4070...")
    dataset = load_dataset("json", data_files=str(dataset_path), split="train")

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=30,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        save_strategy="no"
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="messages",
        max_seq_length=512,
        tokenizer=tokenizer,
        args=training_args
    )

    trainer.train()
    print(f"\n✓ Trening zakończony! Zapisywanie adaptera LoRA w: {output_dir}")
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

def main():
    repo_root = Path(__file__).resolve().parent.parent
    data_path = repo_root / "data" / "nethical_lora_dataset.jsonl"
    output_dir = repo_root / "model" / "blyskawica_lora_adapter"

    ready = check_environment()
    generate_nethical_training_corpus(data_path)

    if not ready:
        print("\nℹ️ Przygotowano dane treningowe. Zainstaluj brakujące pakiety, aby uruchomić pełny trening.")
        sys.exit(0)

    run_training_pipeline(data_path, output_dir)

if __name__ == "__main__":
    main()
