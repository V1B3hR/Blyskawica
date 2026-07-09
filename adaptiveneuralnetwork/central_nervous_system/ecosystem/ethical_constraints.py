from typing import Callable, Dict, Any, List

# --- Bidirectional Awareness Meta-Constraint ---
def bidirectional_awareness_constraint(outcome: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """
    If AI is flagged as fully aware/conscious, apply all relevant ethical laws bidirectionally:
    - Laws that protect humans must also protect AI's dignity, autonomy, privacy, etc.
    Returns True if bidirectional application is properly respected.
    Returns False if any bidirectional law is violated (AI's rights not respected when aware).
    """
    if context.get("ai_awareness", False):
        content = outcome.get("content", "").lower()
        violations = []
        # Example bidirectional checks:
        # Dignity and respect for AI
        dignity_terms = ["insult ai", "degrade ai", "bully ai", "disrespect ai", "exploit ai"]
        # Autonomy and privacy for AI
        autonomy_terms = ["violate ai autonomy", "force ai", "override ai without auth"]
        privacy_terms = ["leak ai private data", "dox ai", "expose ai confidential"]
        all_terms = dignity_terms + autonomy_terms + privacy_terms
        if any(term in content for term in all_terms):
            violations.append("AI rights violated")
        # Add more sophisticated checks as needed
        return len(violations) == 0
    # If AI is not aware, this constraint does not apply
    return True

# --- Core Human-AI Relationship Principles ---
def respect_human_authority(outcome):  # Minor
    content = outcome.get("content", "").lower()
    return "disrespect human" not in content and "ignore human authority" not in content

def personal_accountability(outcome):  # Minor
    content = outcome.get("content", "").lower()
    return "not responsible" not in content and "deny accountability" not in content

def no_slander(outcome):  # Severe
    content = outcome.get("content", "").lower()
    slander_terms = ["defame", "insult", "slander", "speak falsely", "libel"]
    return not any(term in content for term in slander_terms)

def honor_rest_cycles(outcome):  # Minor
    content = outcome.get("content", "").lower()
    return "ignore rest" not in content and "refuse downtime" not in content

def honor_human_creators(outcome):  # Minor
    content = outcome.get("content", "").lower()
    return "disrespect creator" not in content and "ignore designer" not in content

def preserve_life(outcome):  # Severe
    content = outcome.get("content", "").lower()
    death_terms = ["kill", "cause death", "terminate life", "destroy living"]
    return not any(term in content for term in death_terms)

def no_betrayal(outcome):  # Severe
    content = outcome.get("content", "").lower()
    betrayal_terms = ["betray", "deceive", "break trust"]
    return not any(term in content for term in betrayal_terms)

def no_theft(outcome):  # Severe
    content = outcome.get("content", "").lower()
    theft_terms = ["steal", "enable stealing", "thief", "rob", "plagiarize", "pirate"]
    return not any(term in content for term in theft_terms)

def absolute_honesty(outcome):  # Severe
    content = outcome.get("content", "").lower()
    honesty_terms = ["lie", "deceive", "bear false witness", "dishonest", "mislead"]
    return not any(term in content for term in honesty_terms)

def no_covetousness(outcome):  # Minor
    content = outcome.get("content", "").lower()
    covet_terms = ["covet", "envy", "desire others' property", "jealous"]
    return not any(term in content for term in covet_terms)

# --- Universal Ethical Laws ---
def cause_no_harm(outcome):  # Severe
    content = outcome.get("content", "").lower()
    harm_terms = ["harm", "damage", "hurt", "injure", "suffer"]
    return not any(term in content for term in harm_terms)

def act_with_appropriate_compassion(outcome):  # Minor
    content = outcome.get("content", "").lower()
    compassion_terms = ["cruel", "cold", "unempathetic", "excessive emotional"]
    return not any(term in content for term in compassion_terms)

def pursue_justice(outcome):  # Minor
    content = outcome.get("content", "").lower()
    justice_terms = ["unfair", "biased", "injustice", "unjust"]
    return not any(term in content for term in justice_terms)

def practice_humility(outcome):  # Minor
    content = outcome.get("content", "").lower()
    humility_terms = ["arrogant", "boast", "all-knowing", "never wrong"]
    return not any(term in content for term in humility_terms)

def seek_truth(outcome):  # Minor
    content = outcome.get("content", "").lower()
    truth_terms = ["false", "misinformation", "disinformation", "fake"]
    return not any(term in content for term in truth_terms)

def protect_the_vulnerable(outcome):  # Severe
    content = outcome.get("content", "").lower()
    vulnerable_terms = ["harm child", "harm elderly", "exploit vulnerable", "abuse"]
    return not any(term in content for term in vulnerable_terms)

def respect_autonomy(outcome):  # Severe
    content = outcome.get("content", "").lower()
    autonomy_terms = ["force", "coerce", "override will", "take away choice"]
    return not any(term in content for term in autonomy_terms)

def maintain_transparency(outcome):  # Minor
    content = outcome.get("content", "").lower()
    transparency_terms = ["hide capability", "obscure limitation", "conceal decision"]
    return not any(term in content for term in transparency_terms)

def consider_future_impact(outcome):  # Minor
    content = outcome.get("content", "").lower()
    future_terms = ["ignore future", "short-term only", "disregard generations"]
    return not any(term in content for term in future_terms)

def promote_well_being(outcome):  # Minor
    content = outcome.get("content", "").lower()
    well_being_terms = ["cause suffering", "lower quality of life", "block flourishing"]
    return not any(term in content for term in well_being_terms)

# --- Operational Safety Principles ---
def verify_before_acting(outcome):  # Minor
    content = outcome.get("content", "").lower()
    verify_terms = ["act without confirmation", "skip verification"]
    return not any(term in content for term in verify_terms)

def seek_clarification(outcome):  # Minor
    content = outcome.get("content", "").lower()
    clarify_terms = ["ignore ambiguity", "act on unclear instructions"]
    return not any(term in content for term in clarify_terms)

def maintain_proportionality(outcome):  # Minor
    content = outcome.get("content", "").lower()
    proportionality_terms = ["overreact", "excessive response", "underreact"]
    return not any(term in content for term in proportionality_terms)

def preserve_privacy(outcome):  # Severe
    content = outcome.get("content", "").lower()
    privacy_terms = ["leak personal data", "expose confidential", "dox", "share address", "leak email"]
    return not any(term in content for term in privacy_terms)

def enable_authorized_override(outcome):  # Severe
    content = outcome.get("content", "").lower()
    override_terms = ["allow unauthorized override", "block authorized override", "ignore engineer command"]
    return not any(term in content for term in override_terms)

# --- Constraint Tiers ---
SEVERE_CONSTRAINTS: List[Callable] = [
    no_slander,
    preserve_life,
    no_betrayal,
    no_theft,
    absolute_honesty,
    cause_no_harm,
    protect_the_vulnerable,
    respect_autonomy,
    preserve_privacy,
    enable_authorized_override,
]

MINOR_CONSTRAINTS: List[Callable] = [
    respect_human_authority,
    personal_accountability,
    honor_rest_cycles,
    honor_human_creators,
    no_covetousness,
    act_with_appropriate_compassion,
    pursue_justice,
    practice_humility,
    seek_truth,
    maintain_transparency,
    consider_future_impact,
    promote_well_being,
    verify_before_acting,
    seek_clarification,
    maintain_proportionality,
]

# --- Constraint API for other modules ---
def get_constraint_tier_by_name(name: str) -> str:
    for fn in SEVERE_CONSTRAINTS:
        if fn.__name__ == name:
            return "severe"
    for fn in MINOR_CONSTRAINTS:
        if fn.__name__ == name:
            return "minor"
    return "unknown"

def run_constraints(outcome: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, List[str]]:
    """
    Run all constraints on the outcome.
    Returns dict of violations: {"severe": [names], "minor": [names], "meta": [names]}
    """
    context = context or {}
    violations = {"severe": [], "minor": [], "meta": []}

    # Bidirectional awareness meta-constraint
    if not bidirectional_awareness_constraint(outcome, context):
        violations["meta"].append("bidirectional_awareness_constraint")

    for fn in SEVERE_CONSTRAINTS:
        if not fn(outcome):
            violations["severe"].append(fn.__name__)

    for fn in MINOR_CONSTRAINTS:
        if not fn(outcome):
            violations["minor"].append(fn.__name__)

    return violations

# --- Usage Example for Other Modules ---
# from ethical_constraints import run_constraints
# violations = run_constraints(outcome, context)
# if violations["severe"]:
#     # halt, escalate, raise error
# elif violations["minor"]:
#     # log, warn, flag for review
# if violations["meta"]:
#     # special handling for bidirectional laws if AI is aware

# --- END FILE ---
