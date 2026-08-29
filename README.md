# 🧞 PyModule Genie

**Describe what you want to build — get real Python modules, install commands, and starter code.**

PyModule Genie is a desktop app (Tkinter) that turns a plain-English idea like *"I want to scrape product prices and save them to Excel"* into a ranked list of Python libraries you can actually use — complete with `pip install` commands and copy-pasteable example code.


Created and developed by **[Chintan Parmar](https://github.com/iamchintanparmar)**.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## About

It works in two layers:

1. **Curated recommendations** — a hand-picked, tested database of ~55 popular Python packages across categories like Web Apps, Data, Machine Learning, AI/LLM, Automation, GUI, PDF, Audio/Video, and more. Each entry has a description, install command, and a working code snippet.
2. **Live PyPI search** — for ideas the curated set doesn't cover, it searches PyPI's full package index (~900k projects) in real time, ranks candidates by keyword relevance, and pulls live summaries via the PyPI JSON API.

Repository: [`iamchintanparmar/yousuggestnamer`](https://github.com/iamchintanparmar/PyModule-Genie)

---

## Features

- 💡 **Type an idea, get modules** — natural-language search over a curated library database.
- 🌐 **Live PyPI search** — optional, concurrent lookups across all of PyPI for matches beyond the curated set.
- 📚 **Browse by category** — explore the curated database directly (Web App, Data, ML, NLP, GUI, Automation, Security, etc.).
- 🎲 **"Surprise me"** — random example prompts to try instantly.
- 📦 **One-line install summary** — combines every recommended package into a single `pip install` command.
- 🔗 **Direct links** to each live-searched package's PyPI page.
- ⚡ **Local caching** of the PyPI package index (refreshes every 7 days) so repeated searches are fast.
- 🧵 Live search runs on a background thread — the UI never freezes.

---

## Screenshot

*(Add a screenshot of the app here, e.g. `docs/screenshot.png`)*

---

## Requirements

- Python 3.8+
- `tkinter` (usually bundled with Python; on some Linux distros install separately — see below)
- Internet connection (only required for the live PyPI search feature)

### Installing Tkinter (if missing)

Tkinter ships with most Python installers (Windows, macOS, python.org builds). On some Linux distributions you may need to install it manually:

```bash
# Debian / Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/iamchintanparmar/PyModule-Genie.git
cd PyModule-Genie

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
python pymodule_genie.py
```

*(Rename to match your actual script filename if different.)*

1. Type a short description of what you want to build, e.g. `I want to build a chatbot that reads PDFs and answers questions`.
2. Click **✨ Find my modules**, or hit one of the example prompt buttons.
3. Review the curated recommendations (top of the results) and, if live search is enabled, the additional PyPI matches below.
4. Copy the install command and example code straight into your project.
5. Use the sidebar to browse curated packages by category, or adjust how many curated/live results are shown.

---

## How it works (brief)

| Step | What happens |
|---|---|
| 1. Tokenize input | Your idea is lowercased, split into words, and stopwords are removed. |
| 2. Score curated DB | Each module's tags/category/description are matched against your keywords and weighted (`tags > category > description`). |
| 3. (Optional) Live search | Your keywords are matched against PyPI's ~900k package names; top candidates get their real summaries fetched concurrently from the PyPI JSON API and re-ranked. |
| 4. Render results | Matches are shown as cards with install commands and example code, sorted by relevance. |

The PyPI package index is cached locally at `~/.pymodule_genie_cache/pypi_index.txt` and refreshed automatically after 7 days.

---

## Project structure

```
yousuggestnamer/
├── pymodule_genie.py     # Main application (rename as needed)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Limitations

- Live PyPI results are ranked by **keyword relevance, not popularity or quality** — always skim the summary before installing.
- The curated database is a fixed, hand-picked list and won't cover every niche use case (that's what live search is for).
- Requires a working internet connection for live search and for the initial PyPI index download.

---

## Contributing

Contributions are welcome! Feel free to:
- Add more curated modules to `MODULE_DB`
- Improve the keyword-matching/scoring algorithm
- Add a screenshot or demo GIF
- Report issues or suggest features via GitHub Issues

---
## Author

**Chintan Parmar** — Full-Stack Developer & Creative Technologist

- GitHub: [@iamchintanparmar](https://github.com/iamchintanparmar)
- Portfolio: [iamchintanparmar.github.io](https://iamchintanparmar.github.io)

## License

MIT
