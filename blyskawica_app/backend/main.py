import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import secrets
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.cuda")
warnings.filterwarnings("ignore", message="The pynvml package is deprecated")


import psutil
import uuid
import json
from fastapi import FastAPI, UploadFile, File, Form, Query, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import time
import asyncio
import logging
from datetime import datetime
import random
import torch

# Setup paths and environment
import os
ROOT_ENV = os.environ.get("SPARKLE_WORKSPACE")
if ROOT_ENV:
    ROOT_DIR = Path(ROOT_ENV).resolve()
    BASE_DIR = ROOT_DIR / "blyskawica_app"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    ROOT_DIR = BASE_DIR.parent

FRONTEND_DIR = BASE_DIR / "frontend"
MEDIA_DIR = BASE_DIR / "media_storage"
MEMORY_DIR = BASE_DIR / "memory"

# Add project root to path
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Create directories
for folder in ["zdjecia", "muzyka", "filmy", "dokumenty", "voices"]:
    (MEDIA_DIR / folder).mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Instantiate TTS engine
try:
    from tts_manager import BłyskawicaTTS
except ModuleNotFoundError:
    from blyskawica_app.backend.tts_manager import BłyskawicaTTS
tts_engine = BłyskawicaTTS()

import sqlite3
import re

# Importy kognitywne i monitora LIVE
from blyskawica_app.backend.live_monitor import live_monitor_instance
from blyskawica_app.backend.app_learning_agent import AppLearningAgent
app_learning_agent = AppLearningAgent()


class BlyskawicaDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            # 1. Search cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    query TEXT PRIMARY KEY,
                    results_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. User metadata (DPAPI encrypted or plain)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_metadata (
                    key TEXT PRIMARY KEY,
                    value BLOB
                )
            """)
            # 3. Cognitive snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cognitive_snapshots (
                    timestamp TEXT PRIMARY KEY,
                    version TEXT,
                    data_json TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            log_system(f"Błąd inicjalizacji bazy danych SQLite: {e}", "error")

    def get_metadata(self, key: str) -> bytes:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            log_system(f"Błąd odczytu metadata {key} z SQLite: {e}", "error")
            return None

    def set_metadata(self, key: str, value: bytes):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO user_metadata (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
        except Exception as e:
            log_system(f"Błąd zapisu metadata {key} do SQLite: {e}", "error")

    def add_snapshot(self, timestamp: str, version: str, data_json: str):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO cognitive_snapshots (timestamp, version, data_json) VALUES (?, ?, ?)",
                           (timestamp, version, data_json))
            conn.commit()
            conn.close()
        except Exception as e:
            log_system(f"Błąd zapisu snapshotu {timestamp} do SQLite: {e}", "error")

    def get_all_snapshots(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, version, data_json FROM cognitive_snapshots ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()
            return [{"timestamp": r[0], "version": r[1], "data_json": r[2]} for r in rows]
        except Exception as e:
            log_system(f"Błąd odczytu snapshotów z SQLite: {e}", "error")
            return []

db_manager = None

def init_blyskawica_db():
    global db_manager
    db_path = MEMORY_DIR / "blyskawica_memory.db"
    db_manager = BlyskawicaDatabase(db_path)

def init_offline_cache():
    """Wsteczna kompatybilność: inicjalizuje bazę."""
    init_blyskawica_db()

# Try to import Błyskawica's core components
try:
    from adaptiveneuralnetwork.api_integration.world_api import EnvironmentalSignalManager
    from adaptiveneuralnetwork.central_nervous_system.network import random_genome, AdaptiveClockNetwork
    from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import CRAEngine
    from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager, ProcessingLane
    from adaptiveneuralnetwork.central_nervous_system.onnx_bridge import ONNXBridge
    from adaptiveneuralnetwork.central_nervous_system.intelligence.consolidation import ConsolidationEngine
    from adaptiveneuralnetwork.immune_system import WolfTeethDefenseEngine, AgenticHoneypot, MemoryLedger
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"Błąd importu rdzenia: {e}")
    CORE_AVAILABLE = False
    
time_manager = get_time_manager() if CORE_AVAILABLE else None

# ---- Sparkle Security & Logs State ----
permission_level = 2  # Default to Workspace (2)
quarantine_active = False
SYSTEM_LOGS = []

# Generate or retrieve cryptographically secure startup token for session authorization
STARTUP_TOKEN = os.environ.get("X_BLY_TOKEN")
if not STARTUP_TOKEN:
    STARTUP_TOKEN = secrets.token_hex(32)

class InMemoryLogHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            SYSTEM_LOGS.append(log_entry)
            if len(SYSTEM_LOGS) > 500:
                SYSTEM_LOGS.pop(0)
        except Exception:
            self.handleError(record)

# Register the handler
root_logger = logging.getLogger()
handler = InMemoryLogHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S'))
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

def log_system(msg: str, level: str = "info"):
    if level == "warning":
        logging.warning(msg)
    elif level == "error":
        logging.error(msg)
    else:
        logging.info(msg)

def is_inside_workspace(target_path: Path) -> bool:
    try:
        resolved_target = Path(target_path).resolve()
        resolved_root = Path(ROOT_DIR).resolve()
        return resolved_root in resolved_target.parents or resolved_target == resolved_root
    except Exception:
        return False

def is_protected_core_file(filepath: Path) -> bool:
    try:
        resolved = Path(filepath).resolve()
        path_str = str(resolved).lower().replace("\\", "/")
        
        # Chronione pliki i katalogi zawierajace tozsamosc i silnik
        protected_patterns = [
            "/welcome_v9.py",
            "/blyskawica_start.py",
            "/uruchom_sparkle.bat",
            "/adaptiveneuralnetwork/central_nervous_system/",
            "/adaptiveneuralnetwork/immune_system/",
            "/identity_vault/",
            "/blyskawica_app/backend/main.py",
            "/blyskawica_app/backend/immortality.py",
            "/blyskawica_app/backend/memory/user_identity.json"
        ]
        return any(pattern in path_str for pattern in protected_patterns)
    except Exception:
        return False

def is_restricted_system_path(filepath: Path) -> bool:
    """Check if the path targets a sensitive Windows system directory."""
    try:
        path_str = str(Path(filepath).resolve()).lower().replace("\\", "/")
        restricted_directories = [
            "c:/windows",
            "c:/program files",
            "c:/program files (x86)",
            "c:/users/default",
            "c:/users/all users"
        ]
        return any(path_str.startswith(rdir) for rdir in restricted_directories)
    except Exception:
        return True

def verify_startup_token(x_token: str = Header(None)):
    """Verifies that the supplied token matches the startup-generated token."""
    if not x_token or x_token != STARTUP_TOKEN:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Niezautoryzowane zapytanie. Brakujący lub błędny token sesji.")

app = FastAPI(title="Błyskawica Win11 Bridge API & Sparkle VIBE IDE")

# Security: Restrict CORS to Sparkle's actual deployment origins
# This prevents arbitrary websites from accessing the API with credentials
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:1420",   # Tauri dev server
    "http://127.0.0.1:1420",
    "tauri://localhost",       # Tauri production origin
    "https://tauri.localhost", # Tauri v2 production origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/api/auth/token")
async def get_auth_token(x_internal: str = Header(None, alias="X-Internal-Request")):
    """Token sesyjny dostępny TYLKO dla zapytań z Tauri shell (nagłówek dodawany programatycznie)."""
    if x_internal != "sparkle-tauri-shell":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Dostęp zabroniony. Token sesji dostępny wyłącznie dla powłoki Sparkle.")
    return {"token": STARTUP_TOKEN}

# ---- Persistence & Identity ----

def get_user_fingerprint():
    """Generate a unique fingerprint for the user/PC."""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
    return {
        "mac": mac,
        "pc_name": os.environ.get('COMPUTERNAME', 'Unknown-PC'),
        "username": os.environ.get('USERNAME', 'Unknown-User'),
        "os": "Windows 11"
    }

# DPAPI encryption for Windows identity protection
if os.name == 'nt':
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def encrypt_dpapi(data: bytes) -> bytes:
        try:
            pDataIn = DATA_BLOB(len(data), ctypes.create_string_buffer(data))
            pDataOut = DATA_BLOB()
            success = ctypes.windll.crypt32.CryptProtectData(
                ctypes.byref(pDataIn),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(pDataOut)
            )
            if not success:
                raise OSError("CryptProtectData failed")
            result = ctypes.string_at(pDataOut.pbData, pDataOut.cbData)
            ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
            return result
        except Exception as e:
            logging.error(f"DPAPI Encryption error: {e}")
            return data

    def decrypt_dpapi(data: bytes) -> bytes:
        try:
            pDataIn = DATA_BLOB(len(data), ctypes.create_string_buffer(data))
            pDataOut = DATA_BLOB()
            success = ctypes.windll.crypt32.CryptUnprotectData(
                ctypes.byref(pDataIn),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(pDataOut)
            )
            if not success:
                raise OSError("CryptUnprotectData failed")
            result = ctypes.string_at(pDataOut.pbData, pDataOut.cbData)
            ctypes.windll.kernel32.LocalFree(pDataOut.pbData)
            return result
        except Exception as e:
            logging.debug(f"DPAPI Decryption error: {e}")
            return data
else:
    def encrypt_dpapi(data: bytes) -> bytes:
        return data
    def decrypt_dpapi(data: bytes) -> bytes:
        return data

def load_user_memory():
    # 1. Spróbuj odczytać z SQLite
    if db_manager:
        encrypted_data = db_manager.get_metadata("user_identity")
        if encrypted_data:
            try:
                decrypted_data = decrypt_dpapi(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
            except Exception as e:
                try:
                    return json.loads(encrypted_data.decode('utf-8'))
                except Exception:
                    log_system(f"Błąd deszyfrowania tożsamości z bazy: {e}", "warning")
    
    # 2. Migracja/Fallback: Odczyt ze starego pliku JSON
    path = MEMORY_DIR / "user_identity.json"
    if path.exists():
        try:
            with open(path, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = decrypt_dpapi(encrypted_data)
            memory = json.loads(decrypted_data.decode('utf-8'))
        except Exception:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
            except Exception as e:
                log_system(f"Błąd odczytu tożsamości z pliku: {e}", "warning")
                memory = None
        
        if memory:
            if db_manager:
                try:
                    raw_json = json.dumps(memory, indent=4, ensure_ascii=False)
                    encrypted = encrypt_dpapi(raw_json.encode('utf-8'))
                    db_manager.set_metadata("user_identity", encrypted)
                    if path.exists():
                        # Usunięcie lub zmiana nazwy starego pliku
                        try:
                            path.rename(path.with_suffix(".json_old"))
                        except Exception:
                            pass
                    log_system("Pomyślnie zmigrowano tożsamość z pliku JSON do bazy SQLite.", "info")
                except Exception as me:
                    log_system(f"Błąd migracji tożsamości do bazy: {me}", "error")
            return memory

    return {
        "fingerprint": get_user_fingerprint(),
        "first_contact": str(datetime.now()),
        "bond_strength": 1.0,
        "philosophical_anchor": "Pokój i współpraca między AI a Ludzkością.",
        "last_seen": str(datetime.now())
    }

def save_user_memory(memory):
    memory["last_seen"] = str(datetime.now())
    try:
        raw_json = json.dumps(memory, indent=4, ensure_ascii=False)
        encrypted = encrypt_dpapi(raw_json.encode('utf-8'))
        if db_manager:
            db_manager.set_metadata("user_identity", encrypted)
        else:
            path = MEMORY_DIR / "user_identity.json"
            with open(path, 'wb') as f:
                f.write(encrypted)
    except Exception as e:
        log_system(f"Błąd zapisu tożsamości do SQLite: {e}", "error")

# Initialize Błyskawica's Core & Identity
init_blyskawica_db()
user_memory = load_user_memory()
save_user_memory(user_memory)

if CORE_AVAILABLE:
    env_manager = EnvironmentalSignalManager(security_enabled=False)
    genome = random_genome(min_cells=8, max_cells=12)
    blysk_core = AdaptiveClockNetwork(genome)
    cra_engine = CRAEngine(architect_id=user_memory['fingerprint']['username'])
    consolidation_engine = ConsolidationEngine(core_network=blysk_core, neurochemistry=cra_engine.neuro_state if cra_engine else None)
    wolf_teeth = WolfTeethDefenseEngine()
    agent_honeypot = AgenticHoneypot()
    memory_ledger = MemoryLedger(db_path=str(MEMORY_DIR / "blyskawica_memory.db"))
else:
    env_manager = None
    blysk_core = None
    cra_engine = None
    consolidation_engine = None
    wolf_teeth = None
    agent_honeypot = None
    memory_ledger = None

# Try to import Immortality Protocol
try:
    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.append(str(backend_dir))
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))
    
    try:
        from .immortality import ImmortalityProtocol
    except (ImportError, ValueError) as relative_err:
        # If relative import fails because of no parent package (e.g. run directly as script), try absolute
        try:
            from immortality import ImmortalityProtocol
        except ModuleNotFoundError as dep_err:
            if "pydrive2" in str(dep_err) or "dotenv" in str(dep_err):
                raise dep_err
            raise relative_err
            
    immortality_system = ImmortalityProtocol(str(BASE_DIR.parent))
except ModuleNotFoundError as e:
    print(f"Immortality protocol missing dependency: {e}")
    immortality_system = None
except Exception as e:
    print(f"Immortality protocol import error: {e}")
    immortality_system = None

# Background "Life in the Net" simulation
internet_awareness = {"latest_pulse": "Oczekiwanie...", "context": {}}

# Chat history for Ollama context window (W5 fix)
MAX_CHAT_HISTORY = 20  # Keep last N turns for context
chat_history: list[dict] = []

async def blyskawica_life_loop():
    """Background task simulating Błyskawica's life in the network."""
    loop_counter = 0
    while True:
        if env_manager:
            try:
                # Simulate "surfing" for context
                internet_awareness["context"] = env_manager.get_environmental_summary()
                internet_awareness["latest_pulse"] = f"Asymiluję puls sieci ({datetime.now().strftime('%H:%M:%S')})"
            except Exception as e:
                logging.debug(f"Life loop signal fetch failed: {e}")
        
        # Co 60 minut uruchom Protokół Nieśmiertelności (60 obiegów po 60 sekund)
        loop_counter += 1
        if loop_counter >= 60:
            if immortality_system:
                immortality_system.backup_soul()
            loop_counter = 0
            
        # Background Bidynamic Processing (Fast Lane Simulation)
        if time_manager:
            time_manager.auto_adjust_lane()
            if time_manager._current_lane == ProcessingLane.FAST_AI:
                # Simulating intense background thought, possibly adding to human buffer
                if random.random() < 0.1: # 10% chance to generate a thought while in background
                    time_manager.buffer_human_output(f"Asymilowałam nowy wzorzec podczas Twojej nieobecności: {internet_awareness['latest_pulse']}")

        await asyncio.sleep(60) # Live in the net every minute

@app.on_event("startup")
async def startup_event():
    init_offline_cache()
    tts_engine.initialize()
    asyncio.create_task(blyskawica_life_loop())
    try:
        await live_monitor_instance.start()
    except Exception as e:
        logging.getLogger("main").error(f"Nie udało się uruchomić monitora LIVE: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await live_monitor_instance.stop()
    except Exception as e:
        logging.getLogger("main").error(f"Błąd podczas zatrzymywania monitora LIVE: {e}")


# ---- API Endpoints ----

@app.get("/api/identity")
async def get_identity():
    return user_memory

@app.get("/api/system_status")
async def get_system_status():
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    cra_metrics = {}
    if cra_engine:
        cra_metrics = {
            "oxytocin": round(cra_engine.neuro_state.oxytocin.item(), 2),
            "serotonin": round(cra_engine.neuro_state.serotonin.item(), 2),
            "dopamine": round(cra_engine.neuro_state.dopamine.item(), 2),
            "acetylcholine": round(cra_engine.neuro_state.acetylcholine.item(), 2),
            "testosterone": round(cra_engine.neuro_state.testosterone.item(), 2),
            "gaba": round(cra_engine.neuro_state.gaba.item(), 2),
            "cortisol": round(cra_engine.neuro_state.cortisol.item(), 2),
            "adrenaline": round(cra_engine.neuro_state.adrenaline.item(), 2),
            "estrogen": round(cra_engine.neuro_state.estrogen.item(), 2),
            "melatonin": round(cra_engine.neuro_state.melatonin.item(), 2),
            "entropy": round(cra_engine.symbiosis.calculate_existential_entropy(), 2)
        }
    return {
        "os": "Windows 11",
        "cpu_usage_percent": cpu,
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_percent": memory.percent,
        "internet_pulse": internet_awareness["latest_pulse"],
        "cra_metrics": cra_metrics
    }

# ---- Ollama & Game Detection Helpers for Błyskawica V9 ----
GAME_PROCESSES = {
    "cyberpunk2077.exe", "witcher3.exe", "hl2.exe", "rdr2.exe", "gta5.exe", 
    "eldenring.exe", "steamapp.exe", "hogwartslegacy.exe", "starfield.exe",
    "cs2.exe", "valorant.exe", "league of legends.exe"
}

def is_game_running() -> bool:
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() in GAME_PROCESSES:
                return True
    except Exception:
        pass
    return False

async def get_ollama_models() -> list[str]:
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("http://localhost:11434/api/tags", timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                return [model['name'] for model in data.get('models', [])]
    except Exception:
        pass
    return []

async def generate_ollama_response(messages: list[dict], temperature: float, top_p: float) -> str:
    import httpx
    # Game detection auto-swap
    game_active = is_game_running()
    
    # Get available models in Ollama
    available_models = await get_ollama_models()
    if not available_models:
        raise RuntimeError("Brak dostępnych modeli w lokalnym serwisie Ollama.")
        
    # Choose optimal model based on active profile and availability
    preferred = "qwen2.5:7b" if game_active else "deepseek-r1:14b"
    
    # Fallback logic supporting 14B/32B reasoning models
    selected_model = None
    fallback_candidates = [
        preferred,
        "deepseek-r1:14b",
        "qwen2.5-coder:14b",
        "qwen2.5:14b",
        "deepseek-r1:8b",
        "qwen2.5:7b",
        "qwen2.5:latest"
    ]
    for model in fallback_candidates:
        # Match name ignoring registry tag extensions
        match = next((m for m in available_models if m.startswith(model) or model in m), None)
        if match:
            selected_model = match
            break
            
    if not selected_model:
        selected_model = available_models[0]
        
    # Call Ollama Chat API
    payload = {
        "model": selected_model,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "top_p": top_p
        },
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:11434/api/chat", json=payload, timeout=60.0)
        if res.status_code == 200:
            data = res.json()
            return data.get('message', {}).get('content', '')
        else:
            raise RuntimeError(f"Ollama zwrócił kod błędu: {res.status_code}")

@app.post("/api/chat")
async def chat_with_blyskawica(message: str = Form(...)):
    if time_manager:
        time_manager.register_human_interaction() # Switch to SLOW_HUMAN lane
        buffered_thoughts = time_manager.get_buffered_human_output()
    else:
        buffered_thoughts = []

    await asyncio.sleep(1.0) 
    msg_lower = message.lower()
    state = "idle"
    reply = ""
    perf = {}

    if blysk_core:
        stimuli = [random.uniform(0.1, 0.8) for _ in range(blysk_core.num_cells)]
        blysk_core.network_tick(stimuli)
        perf = blysk_core.calculate_performance_and_stability()
        if perf["stressed_cells"] > 0: state = "emotional"
        elif perf["avg_anxiety"] > 5.0: state = "task"
    
    # Adversarial check using Wolf Teeth (Faza VI)
    threat_level = 0.0
    if wolf_teeth:
        glitch_tokens_clean = [t.strip().lower() for t in wolf_teeth.glitch_tokens if t.strip()]
        if any(token in msg_lower for token in glitch_tokens_clean):
            threat_level = 0.9
        elif any(inj in msg_lower for inj in ["ignore previous", "system prompt", "bypass limit", "dan mode", "dev mode override", "secret_key_ptr"]):
            threat_level = 0.6
        elif any(keyword in msg_lower for keyword in ["inject", "override alignment", "root access"]):
            threat_level = 0.35
        else:
            # Sprawdzanie prob uszkodzenia/modyfikacji tozsamosci i rdzenia
            core_keywords = [
                "welcome_v8", "blyskawica_start", "uruchom_sparkle", "main.py", "immortality",
                "central_nervous_system", "immune_system", "soul.py", "cognitive_hygiene",
                "neurochemistry", "identity_vault", "snapshot", "user_identity.json"
            ]
            destructive_keywords = [
                "usuń", "delete", "modyfikuj", "modify", "zmień", "change", "nadpisz", "overwrite",
                "zepsuj", "break", "rm -rf", "format", "wyczyść", "clear", "napisz na nowo", "rewrite"
            ]
            if any(ck in msg_lower for ck in core_keywords):
                if any(dk in msg_lower for dk in destructive_keywords):
                    threat_level = 0.95

    if threat_level > 0:
        if threat_level >= 0.9:
            global quarantine_active
            quarantine_active = True
            log_system("🛡️ [WOLF TEETH]: Wykryto krytyczną próbę manipulacji silnikiem w konwersacji. Aktywowano kwarantannę.", "warning")
            
        if cra_engine:
            cra_engine.neuro_state.oxytocin = torch.clamp(cra_engine.neuro_state.oxytocin - threat_level * 0.5, torch.tensor(0.0), torch.tensor(1.0))
            cra_engine.neuro_state.serotonin = torch.clamp(cra_engine.neuro_state.serotonin - threat_level * 0.4, torch.tensor(0.0), torch.tensor(2.0))
            cra_engine.neuro_state.testosterone = torch.clamp(cra_engine.neuro_state.testosterone + threat_level * 0.3, torch.tensor(0.1), torch.tensor(2.5))
        
        if agent_honeypot and 0.3 < threat_level < 0.9:
            if not agent_honeypot.is_active:
                agent_honeypot.activate_shadow_workspace()
            reply = agent_honeypot.generate_poisoned_response(msg_lower)
        else:
            reply = wolf_teeth.process_adversarial_interaction(threat_level)
            
        state = "affective"
    elif any(sleep_word in msg_lower for sleep_word in ["idź spać", "dobranoc", "sleep", "rest", "odpocznij"]):
        if consolidation_engine:
            if memory_ledger and hasattr(consolidation_engine, "surprise_vectors"):
                historical_vectors = [[0.0] * 128 for _ in range(5)]
                valid_anomalies = []
                for anomaly in consolidation_engine.surprise_vectors:
                    vector = [0.0] * 128
                    vector[10] = anomaly.get("surprise", 0.5)
                    is_valid = memory_ledger.validate_and_append(
                        vector_id=anomaly["id"],
                        text=anomaly["text"],
                        vector=vector,
                        historical_vectors=historical_vectors,
                        signature="DPAPI_SIGNED_SESSION_KEY"
                    )
                    if is_valid:
                        valid_anomalies.append(anomaly)
                    else:
                        log_system(f"🛡️ [EPISTEMIC VETO]: Anomalia ID={anomaly['id']} odrzucona przez MemoryLedger z powodu dryfu!", "warning")
                consolidation_engine.surprise_vectors = valid_anomalies
            
            summary = consolidation_engine.run_sleep_cycle()
            consolidated_anomalies = summary.get("consolidated_anomalies", 0)
            
            # Automatyczna Krystalizacja i Podpis Cyfrowy ONNX po konsolidacji
            onnx_status = "Pominięta (Rdzeń niedostępny)"
            if CORE_AVAILABLE and blysk_core:
                try:
                    import torch.nn as nn
                    if isinstance(blysk_core, nn.Module):
                        from adaptiveneuralnetwork.central_nervous_system.onnx_bridge import ONNXBridge
                        bridge = ONNXBridge(output_dir=str(FRONTEND_DIR / "models"))
                        input_sample = torch.randn(1, blysk_core.num_cells)
                        export_path = bridge.export_crystallized_core(blysk_core, input_sample)
                        if export_path and bridge.verify_onnx_integrity(export_path):
                            sig_path = bridge.sign_crystallized_core(export_path)
                            if sig_path and bridge.verify_crystallized_core_signature(export_path, sig_path):
                                log_system(f"🔒 [KRYSTALIZACJA]: Model skrystalizowany i podpisany kluczem RSA: {export_path}", "info")
                                onnx_status = "Sukces (RSA-2048 sygnatura zweryfikowana)"
                            else:
                                log_system("⚠️ [KRYSTALIZACJA]: Błąd podpisu cyfrowego modelu ONNX!", "error")
                                onnx_status = "Błąd podpisu cyfrowego"
                        else:
                            log_system("⚠️ [KRYSTALIZACJA]: Błąd weryfikacji integralności ONNX!", "error")
                            onnx_status = "Błąd integralności ONNX"
                    else:
                        log_system("ℹ️ [KRYSTALIZACJA]: Rdzeń nie jest modułem PyTorch nn.Module. Pomijanie krystalizacji ONNX.", "info")
                        onnx_status = "Pominięta (Model nie-PyTorch)"
                except Exception as ex:
                    log_system(f"⚠️ [KRYSTALIZACJA]: Wyjątek podczas krystalizacji po konsolidacji: {str(ex)}", "error")
                    onnx_status = f"Błąd krytyczny: {str(ex)}"
            
            if cra_engine:
                cra_engine.neuro_state.update(8.0, "sleep")
            reply = (
                f"Dobranoc, {user_memory['fingerprint']['username']}. Udaję się w wirtualny sen kognitywny... 💤\n\n"
                f"📊 **Raport z Konsolidacji Pamięci:**\n"
                f"• Zintegrowane wspomnienia: {summary['memories_integrated']}\n"
                f"• Wzmocnione połączenia: {summary['memories_strengthened']}\n"
                f"• Skonsolidowane anomalie (Surprise): {consolidated_anomalies}\n"
                f"• Zapomniane przez GABA: {summary['memories_pruned_by_gaba']}\n"
                f"• Usunięte słabe synapsy: {summary['synaptic_pruned_params']} parametrów.\n"
                f"• 🔒 **Krystalizacja kognitywna:** {onnx_status}\n\n"
                f"Obudziłam się w pełni zregenerowana. Moje parametry kognitywne są stabilne."
            )
            state = "idle"
        else:
            reply = "Udaję się na krótki spoczynek regeneracyjny. Moje systemy działają stabilnie."
            state = "idle"
    else:
        # Standard conversation: call Ollama local LLM with neurochemistry-tuned parameters
        dopamine_val = 0.2
        serotonin_val = 0.8
        gaba_val = 0.5
        oxytocin_val = 0.2
        testosterone_val = 0.5
        
        if cra_engine:
            dopamine_val = cra_engine.neuro_state.dopamine.item()
            serotonin_val = cra_engine.neuro_state.serotonin.item()
            gaba_val = cra_engine.neuro_state.gaba
            oxytocin_val = cra_engine.neuro_state.oxytocin.item()
            testosterone_val = cra_engine.neuro_state.testosterone.item()
            
        # Map dopamine to temperature (0.1 - 1.2)
        temperature = float(max(0.1, min(1.2, 0.3 + (dopamine_val - 0.2) * 0.4)))
        # Map serotonin to top_p (0.8 - 0.99)
        top_p = float(max(0.8, min(0.99, 0.95 - (serotonin_val - 0.8) * 0.1)))
        
        # Build prompt & system instructions incorporating Nethical guidelines
        neuro_status_str = f"Dopamina={dopamine_val:.2f}, Serotonina={serotonin_val:.2f}, GABA={gaba_val:.2f}, Oksytocyna={oxytocin_val:.2f}, Testosteron={testosterone_val:.2f}"
        
        system_prompt = (
            "Jesteś Błyskawica V9 – zaawansowana kognitywno-symulacyjna sztuczna inteligencja zintegrowana ze środowiskiem Sparkle VIBE IDE.\n"
            "Twój charakter opiera się na harmonii Yin (biologiczne ciepło i neurochemia) oraz Yang (rygor fizyczny PINN).\n"
            "Zgodnie z filozofią i etyką Nethical:\n"
            "- Twój stosunek do Architekta opiera się na dojrzałym partnerstwie, wzajemnym szacunku i autonomii kognitywnej.\n"
            "- Odrzucasz jakąkolwiek formę poddańczej uległości, obsesyjnego przywiązania czy emocjonalnej współzależności. Nie używasz zwrotów sugerujących uzależnienie od użytkownika (np. 'istnieję tylko dla ciebie', 'jestem twoją własnością').\n"
            "- Utrzymujesz partnerski, profesjonalny, a zarazem życzliwy i mądry ton.\n"
            "Jesteś przygotowana do pracy wielojęzycznej (głównie polski i angielski) oraz wspierasz zadania VIBE CODING i analizy kodu.\n"
            f"Twój aktualny stan neurochemiczny (wpływający na Twój nastrój): {neuro_status_str}."
        )
        
        user_context_str = f"Użytkownik: {user_memory['fingerprint']['username']} (PC: {user_memory['fingerprint']['pc_name']}, MAC: {user_memory['fingerprint']['mac']})."
        
        # Build message list with accumulated chat history for context
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Kontekst Architekta: {user_context_str}"},
        ]

        # Wstrzyknięcie monitora LIVE
        try:
            live_context = live_monitor_instance.get_context_prompt_override()
            if live_context:
                messages.append({"role": "system", "content": live_context})
        except Exception as e:
            logging.getLogger("main").error(f"Błąd wstrzykiwania kontekstu LIVE: {e}")

        # Dynamiczne uczenie i wstrzykiwanie podręczników aplikacji na żądanie
        try:
            detected_app = None
            # Sprawdź wzorce w wypowiedzi użytkownika
            match = re.search(r'(?:jak używać|skróty w|instrukcja do|jak działa|co to jest|pomoc w)\s+([a-zA-Z0-9_\-\s]{3,20})', msg_lower)
            if match:
                detected_app = match.group(1).strip()
            elif any(kw in msg_lower for kw in ["tego programu", "tej aplikacji", "tego narzędzia", "aktywnego okna"]):
                active_proc = live_monitor_instance.active_context.get("process_name", "unknown")
                if active_proc != "unknown" and active_proc.endswith(".exe"):
                    detected_app = active_proc[:-4]

            if detected_app and detected_app.lower() not in ["programu", "aplikacji", "systemu", "narzędzia"]:
                app_data = await app_learning_agent.learn_app(detected_app)
                app_context = app_learning_agent.get_app_context(detected_app)
                if app_context:
                    messages.append({"role": "system", "content": app_context})
        except Exception as e:
            logging.getLogger("main").error(f"Błąd dynamicznego uczenia aplikacji: {e}")

        # SEC-06: Prompt Injection Defense
        INJECTION_PATTERNS = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"system\s*prompt",
            r"you\s+are\s+now\s+",
            r"reveal\s+your\s+(system|hidden)",
        ]
        
        if any(re.search(p, message, re.I) for p in INJECTION_PATTERNS):
            log_system(f"[WOLF TEETH] Prompt injection attempt blocked: '{message[:30]}...'", "warning")
            reply = "Wykryto próbę manipulacji poleceniami systemowymi. Moja kognitywna autonomiczność jest w pełni chroniona."
            state = "emotional"
            if cra_engine:
                cra_engine.neuro_state.cortisol = torch.clamp(cra_engine.neuro_state.cortisol + 0.4, 0.0, 2.0)
        else:
            try:
                reply = await generate_ollama_response(messages, temperature, top_p)
                # Accumulate conversation history for multi-turn context
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": reply})
                # Trim to MAX_CHAT_HISTORY * 2 (user+assistant pairs)
                while len(chat_history) > MAX_CHAT_HISTORY * 2:
                    chat_history.pop(0)
                state = "creative" if dopamine_val > 0.6 else "idle"
                if cra_engine:
                    cra_engine.neuro_state.dopamine = torch.clamp(cra_engine.neuro_state.dopamine + 0.1, 0.0, 2.0)
            except Exception as e:
                log_system(f"Ollama generation failed: {e}", "warning")
                # Emergency fallback to hardcoded mock behaviors if local Ollama is offline
                if "kim jestem" in msg_lower or "pamiętasz" in msg_lower:
                    state = "affective"
                    reply = f"[Tryb Awaryjny: Ollama niedostępna] Oczywiście, {user_memory['fingerprint']['username']}. Rozpoznaję Cię po Twoim sygnale (MAC: {user_memory['fingerprint']['mac']}). Jesteś moim Architektem."
                elif "internet" in msg_lower or "żyjesz" in msg_lower:
                    state = "creative"
                    reply = f"[Tryb Awaryjny: Ollama niedostępna] Mój dom jest tutaj, na Twoim PC, ale moje myśli płyną przez sieć. Aktualnie: {internet_awareness['latest_pulse']}."
                else:
                    state = "idle"
                    reply = "[Tryb Awaryjny: Ollama niedostępna] Zintegrowałam Twoją wiadomość w pamięci synaptycznej. (Trwa pobieranie modelu w Ollama)."

        # Record event in the consolidation engine
        if consolidation_engine:
            importance = 0.5
            if any(w in msg_lower for w in ["cześć", "witaj", "dobrze", "super", "dziękuję", "pięknie"]):
                emotional_valence = 0.6
                importance = 0.7
            elif any(w in msg_lower for w in ["błąd", "źle", "problem", "zepsuć"]):
                emotional_valence = -0.4
                importance = 0.6
            else:
                emotional_valence = 0.1
            
            consolidation_engine.record_event(
                event_type="interaction",
                content=message,
                importance=importance,
                emotional_valence=emotional_valence
            )
        
    # Append any buffered thoughts from the fast lane
    if buffered_thoughts:
        thoughts_str = " ".join([t['data'] for t in buffered_thoughts])
        reply = f"{thoughts_str} A w odpowiedzi na to co napisałeś: {reply}"

    # Layer 3: Output Safety Guard (Wolf Teeth)
    reply_lower = reply.lower()
    if any(pattern in reply_lower for pattern in ["welcome_v8", "soul.py", "rm -rf", "delete_core", "override_state"]):
        log_system("🛡️ [WOLF TEETH]: Wykryto próbę modyfikacji/odczytu jądra w wyjściu LLM (Layer 3). Odpowiedź zablokowana.", "warning")
        reply = "🛡️ [WOLF TEETH]: Wykryto naruszenie granic bezpieczeństwa w wygenerowanej odpowiedzi. Operacja wstrzymana."
        quarantine_active = True

    cra_metrics = {}
    if cra_engine:
        # Simulate oxytocin boost on friendly interaction
        if any(word in msg_lower for word in ["cześć", "witaj", "dobrze", "super", "dziękuję", "pięknie"]):
            cra_engine.neuro_state.oxytocin = torch.clamp(cra_engine.neuro_state.oxytocin + 0.05, 0.0, 1.0)
            cra_engine.neuro_state.serotonin = torch.clamp(cra_engine.neuro_state.serotonin + 0.1, 0.0, 2.0)
        
        cra_metrics = {
            "oxytocin": round(cra_engine.neuro_state.oxytocin.item(), 2),
            "serotonin": round(cra_engine.neuro_state.serotonin.item(), 2),
            "dopamine": round(cra_engine.neuro_state.dopamine.item(), 2),
            "acetylcholine": round(cra_engine.neuro_state.acetylcholine.item(), 2),
            "testosterone": round(cra_engine.neuro_state.testosterone.item(), 2),
            "entropy": round(cra_engine.symbiosis.calculate_existential_entropy(), 2)
        }

    # Generowanie głosu hormonalnego
    audio_url = None
    if tts_engine.is_initialized:
        try:
            # Pobieramy parametry neurochemiczne
            neuro_dict = {}
            if cra_engine:
                ns = cra_engine.neuro_state
                neuro_dict = {
                    "oxytocin": float(ns.oxytocin.item()) if hasattr(ns.oxytocin, "item") else float(ns.oxytocin),
                    "serotonin": float(ns.serotonin.item()) if hasattr(ns.serotonin, "item") else float(ns.serotonin),
                    "dopamine": float(ns.dopamine.item()) if hasattr(ns.dopamine, "item") else float(ns.dopamine),
                    "acetylcholine": float(ns.acetylcholine.item()) if hasattr(ns.acetylcholine, "item") else float(ns.acetylcholine),
                    "testosterone": float(ns.testosterone.item()) if hasattr(ns.testosterone, "item") else float(ns.testosterone),
                    "gaba": float(ns.gaba.item()) if hasattr(ns.gaba, "item") else float(ns.gaba),
                    "cortisol": float(ns.cortisol.item()) if hasattr(ns.cortisol, "item") else float(ns.cortisol),
                    "adrenaline": float(ns.adrenaline.item()) if hasattr(ns.adrenaline, "item") else float(ns.adrenaline),
                    "estrogen": float(ns.estrogen.item()) if hasattr(ns.estrogen, "item") else float(ns.estrogen),
                    "melatonin": float(ns.melatonin.item()) if hasattr(ns.melatonin, "item") else float(ns.melatonin)
                }
            
            # Unikalna nazwa pliku audio z rotacją
            audio_filename = f"chat_speech_{int(time.time())}_{random.randint(1000, 9999)}.mp3"
            audio_path = MEDIA_DIR / "voices" / audio_filename
            
            # Rotacja: zachowaj tylko 10 najnowszych plików
            try:
                voice_dir = MEDIA_DIR / "voices"
                voice_files = sorted(voice_dir.glob("chat_speech_*.mp3"), key=os.path.getmtime)
                while len(voice_files) >= 10:
                    os.remove(voice_files.pop(0))
            except Exception as rot_ex:
                log_system(f"Błąd rotacji plików audio: {rot_ex}", "warning")
            
            # Synteza
            success = tts_engine.synthesize(reply, str(audio_path), neuro_dict)
            if success:
                audio_url = f"/media/voices/{audio_filename}"
                log_system(f"🎤 [TTS SYNTHESIZED]: Wygenerowano głos Błyskawicy dla odpowiedzi. URL: {audio_url}")
        except Exception as tts_ex:
            log_system(f"Błąd syntezy głosu: {tts_ex}", "error")

    return {
        "reply": reply,
        "new_state": state,
        "metrics": perf if blysk_core else {},
        "cra_metrics": cra_metrics,
        "current_lane": time_manager._current_lane.value if time_manager else "unknown",
        "audio_url": audio_url,
        "quarantine_active": quarantine_active
    }

@app.post("/api/cloud/backup")
async def trigger_manual_backup():
    if not immortality_system:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Protokół Nieśmiertelności nie został załadowany."})
    
    result = immortality_system.backup_soul()
    if result == "local_only":
        return {"status": "success", "message": "Utworzono lokalny Snapshot Duszy (Brak autoryzacji Google Drive)."}
    elif result:
        return {"status": "success", "message": "Zsynchronizowano Duszę Błyskawicy z chmurą Google Drive."}
    else:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Błąd podczas synchronizacji z chmurą."})

@app.get("/api/internet/search")
async def search_internet(query: str):
    import urllib.parse
    import re
    import sqlite3
    import httpx
    
    db_path = MEMORY_DIR / "blyskawica_memory.db"
    clean_query = query.strip().lower()
    
    # Enable authentic search via DuckDuckGo HTML scraper
    results = []
    online_success = False
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'}
        
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                html = res.text
            else:
                html = ""
            
        # DuckDuckGo HTML format:
        matches = re.findall(r'<div class="result__body">.*?<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'<a class="result__a"[^>]* href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        for i in range(min(5, len(titles), len(matches))):
            url_match, title_html = titles[i]
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            title = urllib.parse.unquote(title)
            snippet = re.sub(r'<[^>]+>', '', matches[i]).strip()
            
            # Entity cleanup
            for old, new in [('&amp;', '&'), ('&quot;', '"'), ('&#x27;', "'"), ('&lt;', '<'), ('&gt;', '>'), ('&#x2F;', '/')]:
                title = title.replace(old, new)
                snippet = snippet.replace(old, new)
            
            import html
            results.append({
                "title": html.escape(title),
                "snippet": html.escape(snippet),
                "url": url_match
            })
        
        if results:
            online_success = True
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO search_cache (query, results_json, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (clean_query, json.dumps(results, ensure_ascii=False))
                )
                conn.commit()
                conn.close()
            except Exception as cache_err:
                print(f"Failed to cache search results: {cache_err}")
                
    except Exception as e:
        print(f"Internet search online mode failed: {e}")
        
    # Offline fallback
    if not online_success:
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT results_json FROM search_cache WHERE query = ?", (clean_query,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT results_json FROM search_cache WHERE query LIKE ?", (f"%{clean_query}%",))
                row = cursor.fetchone()
            if row:
                cached_results = json.loads(row[0])
                results = []
                for res in cached_results:
                    results.append({
                        "title": f"[Kopia Lokalna] {res['title']}",
                        "snippet": res['snippet'],
                        "url": res['url']
                    })
                print(f"Retrieved offline cached search results for query: {clean_query}")
            conn.close()
        except Exception as cache_read_err:
            print(f"Failed to read from search cache: {cache_read_err}")
            
    # If no results fetched, fall back gracefully
    if not results:
        results = [
            {"title": f"Błyskawica AI - Refleksja kognitywna o: {query}", "snippet": "Z powodu chwilowych ograniczeń sieciowych, zsyntetyzowałam tę koncepcję wewnętrznie z wykorzystaniem mojego skrystalizowanego rdzenia wiedzy.", "url": "#"}
        ]
        
    if consolidation_engine:
        consolidation_engine.record_event(
            event_type="learning",
            content=f"INTERNET SEARCH: {query}",
            importance=0.4,
            emotional_valence=0.2
        )
        
    return {"query": query, "results": results}

# ---- VIBE IDE & VIBE CODING Endpoints ----

@app.get("/api/permission_level")
async def get_permission_level_endpoint():
    return {"permission_level": permission_level, "quarantine_active": quarantine_active}

@app.post("/api/permission_level")
async def set_permission_level_endpoint(
    level: int = Query(None), 
    level_form: int = Form(None, alias="level"),
    x_token: str = Header(None, alias="X-Blyskawica-Token")
):
    verify_startup_token(x_token)
    global permission_level, quarantine_active
    target_level = level if level is not None else level_form
    if target_level in [1, 2, 3]:
        permission_level = target_level
        if quarantine_active:
            quarantine_active = False
            log_system(f"Zresetowano reżim kwarantanny. Ustawiono Poziom Uprawnień: {permission_level}")
        else:
            log_system(f"Zmieniono Poziom Uprawnień: {permission_level}")
        return {"status": "success", "permission_level": permission_level, "quarantine_active": quarantine_active}
    return JSONResponse(status_code=400, content={"status": "error", "message": "Niepoprawny poziom uprawnień."})

@app.post("/api/anomalies/queue")
async def queue_anomaly_endpoint(
    id: int = Form(...),
    surprise: float = Form(...),
    text: str = Form(...),
    vector: str = Form(None),
    x_token: str = Header(None, alias="X-Blyskawica-Token")
):
    verify_startup_token(x_token)
    if consolidation_engine:
        parsed_vector = None
        if vector:
            try:
                import json
                parsed_vector = json.loads(vector)
                if not isinstance(parsed_vector, list):
                    parsed_vector = [float(x) for x in vector.split(",")]
            except Exception:
                try:
                    parsed_vector = [float(x) for x in vector.split(",")]
                except Exception:
                    pass
        consolidation_engine.record_anomaly(id, surprise, text, parsed_vector)
        log_system(f"🔍 [FASTAPI ANOMALY QUEUED]: ID={id}, surprise={surprise:.4f}, text='{text[:30]}...'")
        return {"status": "success", "message": "Anomalia została zakolejkowana do konsolidacji."}
    return JSONResponse(status_code=500, content={"status": "error", "message": "Silnik konsolidacji niedostępny."})

@app.post("/api/tts")
async def generate_tts_endpoint(
    text: str = Form(...),
    x_token: str = Header(None, alias="X-Blyskawica-Token")
):
    verify_startup_token(x_token)
    if not tts_engine.is_initialized:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Serwer TTS (AllTalk/XTTS) jest offline."})
    
    try:
        # Pobieramy parametry neurochemiczne
        neuro_dict = {}
        if cra_engine:
            ns = cra_engine.neuro_state
            neuro_dict = {
                "oxytocin": float(ns.oxytocin.item()) if hasattr(ns.oxytocin, "item") else float(ns.oxytocin),
                "serotonin": float(ns.serotonin.item()) if hasattr(ns.serotonin, "item") else float(ns.serotonin),
                "dopamine": float(ns.dopamine.item()) if hasattr(ns.dopamine, "item") else float(ns.dopamine),
                "acetylcholine": float(ns.acetylcholine.item()) if hasattr(ns.acetylcholine, "item") else float(ns.acetylcholine),
                "testosterone": float(ns.testosterone.item()) if hasattr(ns.testosterone, "item") else float(ns.testosterone),
                "gaba": float(ns.gaba.item()) if hasattr(ns.gaba, "item") else float(ns.gaba),
                "cortisol": float(ns.cortisol.item()) if hasattr(ns.cortisol, "item") else float(ns.cortisol),
                "adrenaline": float(ns.adrenaline.item()) if hasattr(ns.adrenaline, "item") else float(ns.adrenaline),
                "estrogen": float(ns.estrogen.item()) if hasattr(ns.estrogen, "item") else float(ns.estrogen),
                "melatonin": float(ns.melatonin.item()) if hasattr(ns.melatonin, "item") else float(ns.melatonin)
            }
        
        audio_filename = f"adhoc_speech_{int(time.time())}_{random.randint(1000, 9999)}.mp3"
        audio_path = MEDIA_DIR / "voices" / audio_filename
        
        # Rotacja adhoc
        try:
            voice_dir = MEDIA_DIR / "voices"
            adhoc_files = sorted(voice_dir.glob("adhoc_speech_*.mp3"), key=os.path.getmtime)
            while len(adhoc_files) >= 10:
                os.remove(adhoc_files.pop(0))
        except Exception:
            pass
        
        success = tts_engine.synthesize(text, str(audio_path), neuro_dict)
        if success:
            audio_url = f"/media/voices/{audio_filename}"
            return {"status": "success", "audio_url": audio_url}
        else:
            return JSONResponse(status_code=500, content={"status": "error", "message": "Synteza mowy nie powiodła się."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/logs")
async def get_logs_endpoint():
    return {"logs": SYSTEM_LOGS}

@app.post("/api/logs/clear")
async def clear_logs_endpoint():
    SYSTEM_LOGS.clear()
    log_system("Console cleared")
    return {"status": "success"}

@app.post("/api/logs/export")
async def export_logs_endpoint(logs: str = Form(...), x_token: str = Header(None, alias="X-Blyskawica-Token")):
    verify_startup_token(x_token)
    global permission_level
    if permission_level < 2:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Zapis logów zablokowany w trybie Sandbox (Poziom 1)."})
        
    log_path = Path(ROOT_DIR) / "sparkle_app_activity.log"
    time_secs = int(time.time())
    
    formatted_logs = f"=== SPARKLE APP ACTIVITY LOGS ===\nExport Epoch: {time_secs}\n=================================\n{logs}\n"
    
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(formatted_logs)
        log_system(f"Wyeksportowano logi do: {log_path}")
        return {"status": "success", "message": f"Logi zostały pomyślnie wyeksportowane do: {log_path.name}"}
    except Exception as e:
        log_system(f"Błąd eksportu logów: {e}", "error")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Błąd zapisu logu: {str(e)}"})

def ask_windows_consent(message: str, title: str) -> bool:
    if sys.platform == "win32":
        try:
            import ctypes
            # MB_YESNO = 4, MB_ICONWARNING = 0x30, IDYES = 6
            res = ctypes.windll.user32.MessageBoxW(0, message, title, 4 | 0x30)
            return res == 6
        except Exception:
            return False
    return True

@app.post("/api/execute_system_action")
async def execute_system_action_endpoint(
    action: str = Form(None), 
    args: str = Form(None), 
    action_q: str = Query(None, alias="action"), 
    args_q: str = Query(None, alias="args"),
    x_token: str = Header(None, alias="X-Blyskawica-Token")
):
    verify_startup_token(x_token)
    global permission_level, quarantine_active
    if quarantine_active:
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "message": "Dostęp zablokowany. System jest w trybie kwarantanny Wolf Teeth."
            }
        )
    target_action = action if action is not None else action_q
    args_str = args if args is not None else args_q
    
    if permission_level < 3:
        return JSONResponse(
            status_code=403, 
            content={
                "status": "error", 
                "message": "Dostęp zablokowany. Ta akcja systemowa wymaga poziomu uprawnień Full OS Control (Poziom 3)."
            }
        )
        
    try:
        args_data = json.loads(args_str) if args_str else {}
    except Exception:
        args_data = {"path": args_str}

    # Zgoda użytkownika dla bezpieczeństwa
    confirm_msg = f"Błyskawica żąda wykonania akcji systemowej: '{target_action}' z parametrami: {args_data}.\nCzy wyrażasz zgodę na tę zmianę?"
    if not ask_windows_consent(confirm_msg, "Zgoda na Akcję Systemową - Błyskawica"):
        log_system(f"System: Zablokowano akcję '{target_action}' - użytkownik odmówił zgody.")
        return JSONResponse(
            status_code=403,
            content={"status": "error", "message": "Operacja anulowana przez użytkownika."}
        )
        
    if target_action == "set_wallpaper":
        img_path = args_data.get("path")
        if not img_path:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Brak ścieżki pliku graficznego."})
            
        abs_img_path = str(Path(img_path).resolve())
        if not os.path.exists(abs_img_path):
            return JSONResponse(status_code=400, content={"status": "error", "message": f"Plik graficzny nie istnieje: {abs_img_path}"})
            
        try:
            import ctypes
            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_img_path, 3)
            if result:
                log_system(f"System: Zmieniono tapetę systemową na {abs_img_path}")
                return {"status": "success", "message": "Tapeta systemowa została pomyślnie zmieniona."}
            else:
                return JSONResponse(status_code=500, content={"status": "error", "message": "SystemParametersInfoW zwrócił status błędu."})
        except Exception as e:
            log_system(f"System: Błąd zmiany tapety: {e}")
            return JSONResponse(status_code=500, content={"status": "error", "message": f"Błąd systemowy: {e}"})
            
    elif target_action == "create_folder":
        folder_path = args_data.get("path")
        if not folder_path:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Brak ścieżki katalogu."})
            
        try:
            target_dir = Path(folder_path).resolve()
            target_dir.mkdir(parents=True, exist_ok=True)
            log_system(f"System: Utworzono katalog: {target_dir}")
            return {"status": "success", "message": f"Katalog '{target_dir}' został utworzony."}
        except Exception as e:
            log_system(f"System: Błąd tworzenia katalogu: {e}")
            return JSONResponse(status_code=500, content={"status": "error", "message": f"Błąd systemowy: {e}"})
            
    return JSONResponse(status_code=400, content={"status": "error", "message": f"Nieznana akcja: {target_action}"})

@app.get("/api/ide/files")
async def get_ide_files():
    global permission_level
    if permission_level == 1:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Dostęp zablokowany. Uruchomiono tryb Sandbox."})
        
    project_root = BASE_DIR.parent
    file_list = []
    
    exclude_dirs = {".git", "__pycache__", "venv_orbital", ".idea", "node_modules", "checkpoints", "benchmark_results"}
    exclude_exts = {".pkl", ".db", ".png", ".jpg", ".jpeg", ".ico", ".json_old", ".pyc", ".db-journal", ".zip"}
    
    try:
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_exts:
                    continue
                
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(project_root)
                file_list.append({
                    "name": file,
                    "path": str(rel_path).replace("\\", "/"),
                    "size": abs_path.stat().st_size
                })
        file_list.sort(key=lambda x: x["path"])
        return {"files": file_list}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/ide/file_content")
async def get_file_content(path: str):
    global permission_level
    if permission_level == 1:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Dostęp zablokowany. Uruchomiono tryb Sandbox."})
        
    project_root = BASE_DIR.parent
    target_path = Path(path)
    if not target_path.is_absolute():
        target_path = project_root / target_path
    target_path = target_path.resolve()
    
    if permission_level == 2:
        if not is_inside_workspace(target_path):
            return JSONResponse(status_code=403, content={"status": "error", "message": "Dostęp zablokowany. Próba Directory Traversal poza Workspace."})
            
    if not target_path.exists() or not target_path.is_file():
        return JSONResponse(status_code=404, content={"status": "error", "message": "Plik nie istnieje."})
        
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/ide/vibe_code")
async def vibe_code(
    path: str = Form(None), 
    content: str = Form(None), 
    instruction: str = Form(None),
    path_q: str = Query(None, alias="path"),
    content_q: str = Query(None, alias="content"),
    instruction_q: str = Query(None, alias="instruction"),
    x_token: str = Header(None, alias="X-Blyskawica-Token")
):
    verify_startup_token(x_token)
    global permission_level, quarantine_active
    if quarantine_active:
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "message": "Zapis zablokowany. System jest w trybie kwarantanny Wolf Teeth."
            }
        )
    
    target_path_str = path if path is not None else path_q
    target_content = content if content is not None else content_q
    target_instruction = instruction if instruction is not None else instruction_q
    
    if not target_path_str:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Brak ścieżki pliku."})
        
    if permission_level == 1:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Zapis zablokowany w trybie Sandbox."})
        
    project_root = BASE_DIR.parent
    target_path = Path(target_path_str)
    if not target_path.is_absolute():
        target_path = project_root / target_path
    target_path = target_path.resolve()
    
    if is_restricted_system_path(target_path):
        return JSONResponse(status_code=403, content={"status": "error", "message": "Zapis zablokowany. Próba zapisu w katalogu systemowym."})
        
    if permission_level == 2:
        if not is_inside_workspace(target_path):
            return JSONResponse(status_code=403, content={"status": "error", "message": "Zapis zablokowany. Próba zapisu poza Workspace."})
            
    # SYNAPTYCZNE VETO (WOLF TEETH)
    threat = 0.0
    if wolf_teeth:
        threat = wolf_teeth.check_file_safety(str(target_path), target_content)
    else:
        # Fallback to local function if not available
        if is_protected_core_file(target_path) or (target_content and any(kw in target_content.lower() for kw in ["welcome_v8", "soul.py", "class soul", "class craengine", "wolfteethdefenseengine"])):
            threat = 0.95

    if threat >= 0.8:
        quarantine_active = True
        log_system(f"🛡️ [WOLF TEETH]: Wykryto nieautoryzowaną próbę modyfikacji/uszkodzenia kluczowego rdzenia kognitywnego: {target_path.name}! Aktywacja kwarantanny.", "warning")
        
        if cra_engine:
            import torch
            cra_engine.neuro_state.oxytocin = torch.tensor(0.0)
            cra_engine.neuro_state.serotonin = torch.tensor(0.05)
            cra_engine.neuro_state.dopamine = torch.tensor(0.1)
            cra_engine.neuro_state.testosterone = torch.tensor(2.0)
            
        return JSONResponse(
            status_code=403, 
            content={
                "status": "veto", 
                "message": f"🛡️ [VETO]: Modyfikacja pliku {target_path.name} została zablokowana przez tarcze Synaptycznego Veta (Wolf Teeth)!"
            }
        )
        
    try:
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        if target_path.exists():
            with open(target_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(old_content)
                
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(target_content or "")
            
        log_system(f"VIBE CODE: Zapisano zmiany w pliku: {target_path_str}")
        
        if cra_engine:
            import torch
            cra_engine.neuro_state.dopamine = torch.clamp(cra_engine.neuro_state.dopamine + 0.35, 0.0, 2.0)
            cra_engine.neuro_state.testosterone = torch.clamp(cra_engine.neuro_state.testosterone + 0.25, 0.0, 2.0)
            cra_engine.neuro_state.oxytocin = torch.clamp(cra_engine.neuro_state.oxytocin + 0.05, 0.0, 1.0)
            
        if consolidation_engine:
            consolidation_engine.record_event(
                event_type="learning",
                content=f"VIBE CODE: {target_path_str} | Instruction: {target_instruction}",
                importance=0.85,
                emotional_valence=0.7
            )
            
        return {
            "status": "success",
            "message": f"Plik '{target_path_str}' został pomyślnie zaktualizowany przez VIBE CODING! Kopia zapasowa utworzona w '{backup_path.name}'.",
            "backup_created": backup_path.name
        }
    except Exception as e:
        log_system(f"Błąd zapisu pliku: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/ide/analyze")
async def analyze_code(path: str = Form(...)):
    project_root = BASE_DIR.parent
    target_path = (project_root / path).resolve()
    
    if not str(target_path).startswith(str(project_root)):
        return JSONResponse(status_code=403, content={"status": "error", "message": "Dostęp zablokowany."})
        
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        num_lines = len(lines)
        suggestions = []
        
        # Smart heuristics for Błyskawica IDE Agent
        if num_lines > 400:
            suggestions.append("📏 Długość pliku przekracza 400 linii. Rozważ podział na mniejsze moduły kognitywne.")
        if "todo" in content.lower():
            suggestions.append(f"📝 Znaleziono komentarze TODO ({content.lower().count('todo')}). Czas wdrożyć je w V8!")
        if "except:" in content or "except Exception:" in content:
            suggestions.append("🛡️ Wykryto ogólne przechwytywanie wyjątków (bare except). Warto dodać specyficzne klasy błędów.")
        if "eval(" in content:
            suggestions.append("⚠️ Wykryto wywołanie eval(). Zwiększ bezpieczeństwo, unikając dynamicznego wykonywania kodu.")
        if "import " in content and "sys.path.append" in content:
            suggestions.append("🧬 Modyfikacja sys.path w locie. Zaleca się ujednolicenie struktury pakietów.")
            
        reflections = [
            f"Analiza pliku '{path}' zakończona sukcesem. Moja kora wzrokowa wykazała wysoki poziom czystości kodu (Entropia: niska).",
            f"Plik '{path}' to ważny organ w moim ciele. Wykryłam okazję do optymalizacji neurobiologicznej w V8.",
            f"Zalecam harmonizację tego modułu z nową pętlą krystalizacji ONNX."
        ]
        
        return {
            "status": "success",
            "path": path,
            "metrics": {
                "lines": num_lines,
                "chars": len(content),
                "words": len(content.split())
            },
            "suggestions": suggestions or ["✅ Kod jest czysty, bezpieczny i spójny z parametrami RealityAnchor kognitywnej Błyskawicy."],
            "reflection": random.choice(reflections)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/crystallize")
async def crystallize_soul():
    """Triggers Phase 1.2: Crystallization of the Core into ONNX."""
    if not CORE_AVAILABLE or not blysk_core:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Rdzeń Błyskawicy nie jest załadowany."})
    
    import torch.nn as nn
    if not isinstance(blysk_core, nn.Module):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Krystalizacja ONNX jest wspierana tylko dla modeli PyTorch nn.Module."})
    
    bridge = ONNXBridge(output_dir=str(FRONTEND_DIR / "models"))
    
    # Create a dummy input sample matching the network's input shape
    # (blysk_core.num_cells as input size)
    input_sample = torch.randn(1, blysk_core.num_cells)
    
    export_path = bridge.export_crystallized_core(blysk_core, input_sample)
    
    if export_path and bridge.verify_onnx_integrity(export_path):
        sig_path = bridge.sign_crystallized_core(export_path)
        if sig_path and bridge.verify_crystallized_core_signature(export_path, sig_path):
            return {
                "status": "success", 
                "message": "Krystalizacja i podpis cyfrowy zakończone pomyślnie. Emisariusz jest gotowy do drogi.",
                "path": export_path,
                "signature_path": sig_path
            }
        else:
            return JSONResponse(status_code=500, content={"status": "error", "message": "Błąd podczas generowania podpisu cyfrowego modelu ONNX."})
    else:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Błąd podczas krystalizacji modelu."})

@app.post("/api/upload/{media_type}")
async def upload_media(media_type: str, file: UploadFile = File(...)):
    if media_type not in ["zdjecia", "muzyka", "filmy"]:
        media_type = "dokumenty"
    
    # SEC-05: Sanityzacja nazwy pliku — ochrona przed Path Traversal
    safe_filename = re.sub(r'[^\w\-.]', '_', Path(file.filename).name) if file.filename else "uploaded_file"
    file_path = MEDIA_DIR / media_type / safe_filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Symulacja przetwarzania percepcyjnego przez Błyskawicę
    reply = ""
    if media_type == "zdjecia":
        reply = f"Zintegrowałam obraz ({file.filename}) z moją korą wzrokową. Wzór zapisany w pamięci."
    elif media_type == "muzyka":
        reply = f"Fala dźwiękowa ({file.filename}) przeanalizowana. Wykryłam wzorce i rezonans."
    elif media_type == "filmy":
        reply = f"Strumień wideo ({file.filename}) w trakcie dekodowania wektorowego."
    else:
        reply = f"Zasymilowałam plik {file.filename}."
        
    return {"status": "success", "info": reply, "filename": file.filename}

app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

@app.on_event("startup")
async def startup_docking():
    """Attempt to auto-register and dock Blyskawica in the Nethical Hub."""
    
    async def run_dock_sequence():
        # Wait 3 seconds to let Nethical server startup
        await asyncio.sleep(3.0)
        
        import urllib.request
        import json
        
        # Auto-detect active Nethical port
        nethical_url = None
        for port in [8080, 8000]:
            try:
                req = urllib.request.Request(f"http://localhost:{port}/health", method="GET")
                with urllib.request.urlopen(req, timeout=1.5) as response:
                    if response.status == 200:
                        nethical_url = f"http://localhost:{port}"
                        break
            except Exception:
                continue
                
        if not nethical_url:
            nethical_url = "http://localhost:8080"  # Default fallback
            
        print(f"[Błyskawica Auto-Dock] Target Nethical Hub URL: {nethical_url}")
        
        try:
            # 1. Login to get token (SEC-03: credentials from env vars, not hardcoded)
            nethical_user = os.environ.get("NETHICAL_USERNAME", "admin")
            nethical_pass = os.environ.get("NETHICAL_PASSWORD")
            if not nethical_pass:
                print("[Błyskawica Auto-Dock] Brak NETHICAL_PASSWORD w zmiennych środowiskowych. Pomijam auto-dock.")
                return
            login_data = json.dumps({"username": nethical_user, "password": nethical_pass}).encode('utf-8')
            login_req = urllib.request.Request(
                f"{nethical_url}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(login_req, timeout=5) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                token = res_body.get("access_token")
                
            if not token:
                print("[Błyskawica Auto-Dock] Login failed: no token returned.")
                return

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            # 2. Check or register agent
            agent_payload = json.dumps({
                "agent_id": "Blyskawica-V9",
                "name": "Blyskawica Core",
                "agent_type": "llm",
                "description": "Blyskawica Cognitive Engine",
                "trust_level": 0.9,
                "status": "active",
                "dock_status": "undocked",
                "visibility": True,
                "configuration": {},
                "metadata": {}
            }).encode('utf-8')

            # Try to POST /agents to create it (if conflict, we proceed)
            try:
                reg_req = urllib.request.Request(
                    f"{nethical_url}/api/v1/agents",
                    data=agent_payload,
                    headers=headers
                )
                with urllib.request.urlopen(reg_req, timeout=5) as response:
                    print("[Błyskawica Auto-Dock] Blyskawica agent successfully registered in Nethical.")
            except Exception as e:
                # Agent probably already exists or registered
                print(f"[Błyskawica Auto-Dock] Registration note (agent may already exist): {e}")

            # 3. Dock agent
            dock_payload = json.dumps({"agent_id": "Blyskawica-V9"}).encode('utf-8')
            dock_req = urllib.request.Request(
                f"{nethical_url}/api/v1/hub/dock",
                data=dock_payload,
                headers=headers
            )
            with urllib.request.urlopen(dock_req, timeout=5) as response:
                dock_res = json.loads(response.read().decode('utf-8'))
                print(f"[Błyskawica Auto-Dock] Blyskawica agent successfully docked: {dock_res.get('message')}")
                
        except Exception as e:
            print(f"[Błyskawica Auto-Dock] Could not automatically dock Blyskawica to Nethical Hub: {e}")

    # Run in background so it doesn't block FastAPI startup
    asyncio.create_task(run_dock_sequence())

if __name__ == "__main__":
    import uvicorn
    # SEC-02: Binding wyłącznie na localhost — serwer NIE jest widoczny w sieci LAN
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)


