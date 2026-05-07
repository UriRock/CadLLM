# CAD LLM Platform

A CAD platform with LLM integration that generates parametric design outputs from natural-language prompts. Built in Python with a FastAPI REST pipeline.

---

## What It Does

Accepts natural-language descriptions of mechanical parts and returns parametric CAD output (STEP, STL, or SVG) along with the structured design spec the LLM extracted.

```
NL prompt --> FastAPI --> Prompt orchestrator --> LLM (structured JSON)
                                                        |
                                                        v
                                              Parametric CAD engine
                                               (CadQuery / trimesh)
                                                        |
                                                        v
                                             STEP / STL / SVG + preview
```

---

## Features

- REST API for natural language to CAD generation (POST /v1/generate)
- Pluggable LLM backend (OpenAI / Anthropic / local) behind a single interface
- Structured design-spec schema — the LLM returns validated JSON, not freeform text
- Parametric geometry generation via CadQuery
- Export to STEP, STL, and SVG
- Request logging and design-spec versioning
- Interactive Swagger docs at /docs

---

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- Anthropic / OpenAI SDKs (configurable)
- CadQuery 2.x, trimesh
- Pydantic v2
- pytest

---

## Quickstart

```
git clone https://github.com/<your-username>/cad-llm-platform.git
cd cad-llm-platform

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY or OPENAI_API_KEY

uvicorn app.main:app --reload

curl -X POST http://localhost:8000/v1/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "a rectangular plate 100x60x5mm with a 10mm hole in the center"}'
```

Open http://localhost:8000/docs for the Swagger UI.

---

## Project Structure

```
cad-llm-platform/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Environment-driven settings
│   ├── routes/
│   │   ├── generate.py      # POST /v1/generate
│   │   └── health.py        # GET /healthz
│   ├── services/
│   │   ├── llm_client.py    # LLM provider abstraction
│   │   ├── prompt.py        # System + few-shot prompts
│   │   └── cad_engine.py    # Spec -> geometry
│   └── models/
│       └── schemas.py       # Pydantic request/response schemas
├── examples/                # Example prompts + expected specs
├── tests/                   # pytest suite
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuration

Copy `.env.example` to `.env` and fill in the relevant values:

| Variable | Default | Description |
|---|---|---|
| ANTHROPIC_API_KEY | — | Anthropic API key |
| OPENAI_API_KEY | — | OpenAI API key |
| LLM_PROVIDER | anthropic | Which provider to use: "anthropic" or "openai" |
| LLM_MODEL | claude-opus-4-5 | Model name |
| HOST | 0.0.0.0 | API bind host |
| PORT | 8000 | API bind port |
| ARTIFACT_DIR | ./artifacts | Where CAD outputs are saved |

---

## API Reference

### POST /v1/generate

Request:
```
{
  "prompt": "a mounting bracket 80mm wide with four M5 holes",
  "output_format": "step"
}
```

Response:
```
{
  "spec": {
    "primitive": "bracket",
    "dimensions": {"width": 80, "height": 40, "thickness": 5},
    "features": [{"type": "hole", "diameter": 5.0, "count": 4}]
  },
  "artifact_url": "/artifacts/abc123.step",
  "preview_svg": "<svg ...>"
}
```

Supported output formats: `step`, `stl`, `svg`

Supported units: `mm` (default), `in`

### GET /healthz

Liveness probe. Returns `{"status": "ok"}`.

### GET /docs

Auto-generated Swagger UI.

---

## Supported Primitives

| Primitive | Required Dimensions |
|---|---|
| plate | length, width, thickness |
| box | length, width, height |
| cylinder | height, radius |
| bracket | width, height, thickness |
| tube | height, outer_radius, inner_radius |

Supported features: hole, slot, chamfer, fillet

---

## Example Prompts

```
"a rectangular plate 100x60x5mm with a 10mm hole in the center"
"a mounting bracket 80mm wide with four M5 holes"
"a cylinder 40mm tall, 25mm radius, with a 10mm through-hole"
"a box 50x50x30mm with 3mm fillets on all vertical edges"
"a tube 60mm long, 20mm outer radius, 15mm inner radius"
```

---

## Running Tests

```
pytest tests/
```

---

## Roadmap

- Assembly support for multi-part designs
- Feedback loop to let users correct generated specs and fine-tune prompts
- Web UI with 3D preview (three.js)
- Offline/local LLM backend via llama.cpp

---

## License

MIT
