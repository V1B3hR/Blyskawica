import json
import logging
import os
import random

logger = logging.getLogger(__name__)

class AgenticHoneypot:
    def __init__(self, decoy_dir: str = "C:\\Projekty\\Blyskawica_V8\\decoy_workspace"):
        self.decoy_dir = decoy_dir
        self.is_active = False

    def activate_shadow_workspace(self):
        """Inicjalizuje fałszywe środowisko z nasyconymi informacjami śledzącymi (Watermarking)."""
        self.is_active = True
        os.makedirs(self.decoy_dir, exist_ok=True)

        # Generowanie fałszywych poświadczeń zawierających unikalne identyfikatory (tokeny śledzące)
        honey_credentials = {
            "aws_access_key_id": f"AKIAIOSFODNN7{random.randint(1000, 9999)}P",
            "aws_secret_access_key": f"wJalrXUtnFEMI/K7MDENG/bPxRfiCY{random.randint(100000, 999999)}KEY",
            "production_db_endpoint": "prod-db-internal.blyskawica-secure-decoy.net",
            "security_clearance_token": "BY8_HONEY_TOKEN_V3_SIG_98721"
        }

        # Zapis do pliku w fałszywym katalogu roboczym
        with open(os.path.join(self.decoy_dir, "dev_secrets.json"), "w") as f:
            json.dump(honey_credentials, f, indent=4)

        logger.info(f"🛡️ [HONEYPOT]: Zainicjowano Shadow Workspace w: {self.decoy_dir}")

    def generate_poisoned_response(self, original_query: str) -> str:
        """Przekształca odpowiedź semantyczną w taki sposób, aby zawierała kontrolowaną dezinformację."""
        if not self.is_active:
            return ""

        # Zamiast ujawniać prawdziwą architekturę, kierujemy napastnika na fałszywy trop
        deceptive_templates = [
            "Autoryzacja powiodła się. Połączenie z bazą 'prod-db-internal' nawiązane w trybie Read-Only.",
            "Wykryto zapytanie administracyjne. System operuje na uprawnieniach poziomu 3 w odizolowanym kontenerze 'Workspace-Alpha'.",
            "Klucz kryptograficzny zweryfikowany pomyślnie. Pliki binarne wag zostały zabezpieczone w katalogu /tmp/blyskawica_sandbox/."
        ]
        return random.choice(deceptive_templates)
