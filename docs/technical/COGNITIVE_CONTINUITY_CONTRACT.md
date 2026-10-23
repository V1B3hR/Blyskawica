# Kontrakt ciągłości kognitywnej Błyskawicy

> **Status:** aktywny — pierwszy wycinek RNT-02, 2026-10-21  
> **Właściciel:** zespół Błyskawica  
> **Powiązanie:** [plan rozwoju i remediacji](../planning/2026-10-development-plan.md), [kontrakt runtime SPARKLE](SPARKLE_RUNTIME_CONTRACT.md)

## Cel

Przeniesienie części produktu do Rust nie może zubożyć rozpoznawalnego sposobu działania Błyskawicy: profili zadaniowych, granic stabilizacji, relacyjnych bezpieczników C.R.A. ani jakości modeli fizycznych. Ten dokument definiuje, co jest zachowaniem referencyjnym, a co jest dopiero kandydatem do portu.

„Neurochemia” w tym kontrakcie oznacza programowe parametry sterujące. Nie jest opisem ani symulacją stanu zdrowia człowieka i nie uzasadnia twierdzeń medycznych.

## Stan faktyczny

| Obszar | Źródło referencyjne | Status migracji | Decyzja |
|---|---|---|---|
| Profile neuroregulacji | `adaptiveneuralnetwork/cognitive_tools/neuro_regulator.py` | Python | Zachować jako referencję dziewięciu parametrów i profili `study`, `analysis`, `rest`, `BCI-co-creation`. Test używa wyłącznie syntetycznego checkpointu. |
| C.R.A. i stabilizacja | `adaptiveneuralnetwork/central_nervous_system/cognitive_hygiene.py` | Python, syntetyczny kontrakt v1 | Dziesięć buforów, stabilizacja, sen, zaufanie operatora, Reality Anchor, Sabbath, symbioza i ocena etyczna są utrwalone w `cra-stabilization-v1.json`; port wyłącznie przez osobny kontrakt semantyczny. |
| PINN termiczny | `adaptiveneuralnetwork/cognitive_tools/pinn_thermal_engine.py` | Python / PyTorch | Trening, autograd i walidacja pozostają w toolchainie Python. Ewentualny Rust obejmuje tylko inference wyeksportowanego modelu po testach jakości. |
| Strumienie Vibe | `blyskawica_app/backend/vibe_telemetry_bridge.py` | legacy Python | Nie migrować automatycznie. Najpierw ustalić potrzebę produktu, stabilny schemat oraz brak danych użytkownika w telemetrii. |
| `NeurochemicalState` | `blyskawica_core/src/neurochemistry.rs` | eksperymentalny Rust | Nie jest obecnie zamiennikiem: ma inną liczbę pól, inne wartości bazowe i inne przejścia profili. Nie może przejąć domyślnej ścieżki C.R.A. lub regulatora Python. |

## Minimalny kontrakt profili v1

Referencja `AutonomousNeuroRegulator` zawiera dziewięć parametrów: `Serotonina`, `Oksytocyna`, `Dopamina`, `GABA`, `Acetylocholina`, `Noradrenalina`, `Melatonina`, `Testosteron`, `Kortyzol`.

- Każdy profil jest liczony względem bazowego stanu, a zmiana pojedynczego parametru jest ograniczona do `±0.07`.
- Nazwy profili, oczekiwane zmiany oraz ślad sekwencyjny `study → rest` są utrwalone w [syntetycznym fixturze v1](fixtures/neurochemistry-profile-v1.json).
- Test `tests/test_neuro_regulator.py` izoluje checkpoint w katalogu tymczasowym; nie czyta ani nie zapisuje pamięci użytkownika.

To jest kontrakt kompatybilności zachowania, nie format trwałego magazynu użytkownika. Dane osobiste, więź relacyjna, historia rozmów i prawdziwe checkpointy nie są dopuszczone do fixture'ów, logów porównawczych ani CI.

## Bramki przed zastąpieniem kodu Python

1. **Specyfikacja:** ustalić wersjonowany stan wejściowy, wyjściowy, granice i scenariusze syntetyczne.
2. **Referencja:** test Python musi przechodzić bez zależności od lokalnego profilu, sieci lub GPU.
3. **Adapter Rust:** implementacja Rust odtwarza wszystkie scenariusze v1 z tolerancją określoną w kontrakcie; różnica wymaga nowej wersji kontraktu i przeglądu.
4. **Praca równoległa:** oba wykonania są porównywane na sztucznych śladach, z kontrolą stabilności, błędów i deterministyczności.
5. **Przełączenie:** domyślna ścieżka może zostać zmieniona dopiero po zielonych testach, udokumentowanej decyzji oraz zachowaniu Pythonowej referencji przez uzgodniony okres wydań.

## Kryteria jakości i prywatności

- Brak niezamierzonego rozszerzenia modelu: moduł Rust nie może udawać C.R.A. bez pełnego zestawu jego semantyk i testów.
- Brak losowości w testach zgodności; losowe elementy należy wstrzyknąć z ustalonym ziarnem lub wyłączyć.
- Żadnych realnych checkpointów, danych tożsamości, sekretów ani telemetrii użytkownika w repozytorium lub CI.
- PINN przechodzi osobne metryki błędu fizycznego przed i po eksporcie; zgodność API nie wystarcza jako dowód jakości modelu.

## Następny bezpieczny wycinek

Zaimplementowano odizolowany adapter porównawczy `NeurochemistryProfileV1` w `blyskawica_core`. Jego test czyta ten sam syntetyczny fixture co test Python, w tym ślad sekwencyjny, i nie jest podłączony do żywego `NeurochemicalState`, C.R.A. ani checkpointu użytkownika.

Kolejny krok utrwalił pełną, syntetyczną referencję C.R.A. w `cra-stabilization-v1.json` oraz `tests/test_cra_stabilization_contract.py`. Obejmuje ona wszystkie dziesięć buforów, stabilizację Ground Loop, cykl snu, sygnał zaufania, decyzje Reality Anchor, Sabbath bez opóźnienia w teście, entropy/loss symbiozy i ocenę etyczną. Nie jest to adapter Rust ani zmiana domyślnej ścieżki produktu. Następnym krokiem może być wyłącznie odizolowany kandydat Rust porównywany z tym fixture po przywróceniu działającej bramki testów Rust.
