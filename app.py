import streamlit as st
import time
import hashlib
import requests
import random
import string

# =========================================================
# ================= PASSWORD STRENGTH ======================
# =========================================================
def get_charset_size(password):
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(not c.isalnum() for c in password):
        charset += 32
    return charset

def estimate_crack_time(password):
    length = len(password)
    charset_size = get_charset_size(password)
    if charset_size == 0:
        return 0
    combinations = charset_size ** length
    guesses_per_sec = 1_000_000_000
    return combinations / guesses_per_sec

def format_time(seconds):
    if seconds < 1:
        return "less than a second"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} hours"
    elif seconds < 31536000:
        return f"{seconds/86400:.2f} days"
    else:
        return f"{seconds/31536000:.2f} years"

def risk_level(seconds):
    if seconds < 60:
        return "🔥 VERY WEAK"
    elif seconds < 3600:
        return "⚠️ WEAK"
    elif seconds < 86400:
        return "🟡 MEDIUM"
    elif seconds < 31536000:
        return "🟢 STRONG"
    else:
        return "🛡️ VERY STRONG"

# =========================================================
# ================= BREACH DETECTION =======================
# =========================================================
def check_password_breach(password):
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"

    try:
        res = requests.get(url)
    except:
        return -1

    if res.status_code != 200:
        return -1

    hashes = (line.split(":") for line in res.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)
    return 0

# =========================================================
# ================= PASSWORD GENERATOR =====================
# =========================================================
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

# =========================================================
# ================= SMART SUGGESTIONS ======================
# =========================================================
def password_suggestions(password):
    suggestions = []

    if len(password) < 8:
        suggestions.append("Increase length to at least 12 characters")
    if not any(c.isupper() for c in password):
        suggestions.append("Add uppercase letters")
    if not any(c.islower() for c in password):
        suggestions.append("Add lowercase letters")
    if not any(c.isdigit() for c in password):
        suggestions.append("Include numbers")
    if not any(not c.isalnum() for c in password):
        suggestions.append("Add special characters (!@#$ etc.)")

    if password.lower() in ["123456", "password", "qwerty"]:
        suggestions.append("Avoid common passwords")

    if suggestions == []:
        suggestions.append("Excellent password! No major weaknesses found")

    return suggestions

# =========================================================
# ================= HACKER ANIMATION =======================
# =========================================================
def hacker_animation():
    steps = [
        ">> Initializing secure engine...",
        ">> Accessing dark web nodes...",
        ">> Establishing encrypted tunnel...",
        ">> Decrypting password hash...",
        ">> Matching breach database...",
        ">> Finalizing scan..."
    ]

    progress = st.progress(0)

    for i, step in enumerate(steps):
        st.write(step)
        time.sleep(0.4)
        progress.progress((i + 1) * 15)

    progress.empty()

# =========================================================
# ======================= UI ===============================
# =========================================================
st.set_page_config(page_title="SecurePass", page_icon="🔐")

st.markdown("""
<style>
.stApp {
    background: black;
    color: #00ff9f;
    font-family: monospace;
}
.terminal {
    background: black;
    border: 1px solid #00ff9f;
    padding: 10px;
    height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 SecurePass - Cybersecurity Tool")

mode = st.radio("Mode", ["UI Mode", "Console Mode"])

st.info("🔒 Password is hashed locally (k-anonymity). Nothing is stored.")

# =========================================================
# ====================== UI MODE ===========================
# =========================================================
if mode == "UI Mode":

    password = st.text_input("Enter Password", type="password")

    if password:
        hacker_animation()

        # Strength
        seconds = estimate_crack_time(password)
        st.subheader("🧠 Strength Analysis")
        st.write(f"Crack Time: {format_time(seconds)}")
        st.write(f"Security Level: {risk_level(seconds)}")
        st.progress(min(len(password) * 5, 100))

        # Breach
        st.subheader("🚨 Breach Detection")
        breach = check_password_breach(password)

        if breach == -1:
            st.error("Server error")
        elif breach == 0:
            st.success("✅ Not found in breaches")
        else:
            st.error(f"⚠️ Found {breach} times in breaches")

        # Suggestions
        st.subheader("🧠 Smart Suggestions")
        for tip in password_suggestions(password):
            st.write(f"• {tip}")

        # Generator
        st.subheader("🔑 Generate Strong Password")
        if st.button("Generate Password"):
            st.success(generate_password())

# =========================================================
# ==================== CONSOLE MODE ========================
# =========================================================
else:

    if "history" not in st.session_state:
        st.session_state.history = ["SecurePass Console", "Type help"]

    st.markdown("<div class='terminal'>", unsafe_allow_html=True)
    for line in st.session_state.history:
        st.text(line)
    st.markdown("</div>", unsafe_allow_html=True)

    cmd = st.text_input(">>")

    def run(cmd):
        parts = cmd.split()

        if cmd == "help":
            return [
                "scan --password <value>",
                "generate",
                "suggest --password <value>",
                "clear"
            ]

        elif cmd.startswith("scan --password"):
            try:
                pwd = parts[2]
                sec = estimate_crack_time(pwd)
                breach = check_password_breach(pwd)

                output = [
                    f">> Crack Time: {format_time(sec)}",
                    f">> Strength: {risk_level(sec)}"
                ]

                if breach == 0:
                    output.append(">> SAFE")
                else:
                    output.append(f">> BREACHED ({breach})")

                return output
            except:
                return ["Invalid command"]

        elif cmd.startswith("generate"):
            return [f">> {generate_password()}"]

        elif cmd.startswith("suggest"):
            try:
                pwd = parts[2]
                return [f">> {tip}" for tip in password_suggestions(pwd)]
            except:
                return ["Usage: suggest --password <value>"]

        elif cmd == "clear":
            st.session_state.history = []
            return []

        return ["Unknown command"]

    if cmd:
        st.session_state.history.append(f">> {cmd}")
        out = run(cmd)

        for line in out:
            time.sleep(0.2)
            st.session_state.history.append(line)

        st.rerun()
