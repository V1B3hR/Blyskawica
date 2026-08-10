"""
Multilingual Spike Harvester for Błyskawica.
Anchors 10 languages into a unified neuromorphic semantic space using OPUS-100.
Languages: EN, PL, DE, FR, ES, ZH, IT, AR, UR, FA.
"""


import torch
from datasets import load_dataset
from transformers import AutoModel, AutoTokenizer


class MultilingualHub:
    """
    Handles fetching and encoding multilingual data for Błyskawica.
    """

    def __init__(self, device="cpu"):
        self.device = device
        # Use a lightweight multilingual model for semantic grounding
        # This acts as the 'Primary Visual/Auditory Cortex' for text
        self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(device)
        self.target_langs = ['pl', 'de', 'fr', 'es', 'zh', 'it', 'ar', 'ur', 'fa']

    def harvest_anchors(self, samples_per_lang=5):
        """Fetches parallel sentences from OPUS-100 and creates semantic spikes."""
        anchors = {}

        print(f"[MULTILINGUAL] Harvesting Anchors for {len(self.target_langs)} languages...")

        for lang in self.target_langs:
            try:
                print(f"- Fetching en-{lang} pairs...")
                # Fetch a small slice of OPUS-100
                dataset = load_dataset("Helsinki-NLP/opus-100", f"en-{lang}", split=f"train[:{samples_per_lang}]")
                pairs = []
                for item in dataset:
                    pairs.append({
                        'en': item['translation']['en'],
                        f'{lang}': item['translation'][lang]
                    })
                anchors[lang] = pairs
            except Exception as e:
                print(f"  ! Error harvesting {lang}: {e}")

        return anchors

    def encode_to_spikes(self, text):
        """TBD: Mapping semantic embeddings to SNN spike trains."""
        inputs = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling for a single semantic vector
            embeddings = outputs.last_hidden_state.mean(dim=1)

        # Normalize to 0-1 for spike rate mapping
        norm_emb = (embeddings - embeddings.min()) / (embeddings.max() - embeddings.min() + 1e-9)
        return norm_emb

if __name__ == "__main__":
    hub = MultilingualHub()
    anchors = hub.harvest_anchors(samples_per_lang=2)

    print("\n[STATUS] Anchoring successful. Example Concept Map:")
    for lang, pairs in anchors.items():
        if pairs:
            p = pairs[0]
            print(f"  [{lang.upper()}] '{p[lang]}' <-> [EN] '{p['en']}'")
            spike_vec = hub.encode_to_spikes(p[lang])
            print(f"    - Neuromorphic Fingerprint (first 5 dims): {spike_vec[0][:5].numpy()}")

    print("\n[RESULT] Błyskawica is reaching out to the polyglot world. 🌍⚡️")
