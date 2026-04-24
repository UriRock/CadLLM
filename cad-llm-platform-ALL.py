# ============================================================
# FILE: README.md
# ============================================================
# CAD LLM Platform

A CAD platform with LLM integration that generates parametric design outputs from natural-language prompts. Built in Python with a FastAPI REST pipeline.

## Overview

The platform accepts natural-language descriptions of mechanical parts (e.g., *"a mounting bracket 80mm wide with four M5 holes"*) and returns parametric CAD output (STEP, STL, or SVG) along with the structured design spec the LLM extracted.

```
  NL prompt ──►  FastAPI ──►  Prompt orchestrator ──►  LLM (structured JSON)
                                                            │
                                                            ▼
                                                  Parametric CAD engine
                                                   (CadQuery / trimesh)
                                                            │
                                                            ▼
                                                 STEP / STL / SVG + preview
```

## Features

- REST API for NL-to-CAD generation (`POST /v1/generate`)
- Pluggable LLM backend (OpenAI / Anthropic / local) behind a single interface
- Structured design-spec schema — the LLM returns validated JSON, not freeform text
- Parametric geometry generation via CadQuery
- Export to STEP, STL, SVG
- Request logging and design-spec versioning
- Interactive Swagger docs at `/docs`

## Tech stack

- **Language:** Python 3.11+
- **API:** FastAPI + Uvicorn
- **LLM:** Anthropic / OpenAI SDKs (configurable)
- **CAD engine:** CadQuery 2.x, trimesh
- **Validation:** Pydantic v2
- **Testing:** pytest

## Quickstart

```bash
# 1. Clone and enter
git clone https://github.com/<your-username>/cad-llm-platform.git
cd cad-llm-platform

# 2. Create a virtualenv
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
#   then edit .env and set ANTHROPIC_API_KEY=... (or OPENAI_API_KEY=...)

# 5. Run the API
uvicorn app.main:app --reload

# 6. Try it
curl -X POST http://localhost:8000/v1/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "a rectangular plate 100x60x5mm with a 10mm hole in the center"}'
```

Open `http://localhost:8000/docs` for the Swagger UI.

## Project structure

```
cad-llm-platform/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Settings (env-driven)
│   ├── routes/
│   │   ├── generate.py      # POST /v1/generate
│   │   └── health.py        # GET /healthz
│   ├── services/
│   │   ├── llm_client.py    # LLM abstraction
│   │   ├── prompt.py        # System + few-shot prompts
│   │   └── cad_engine.py    # Spec -> geometry
│   └── models/
│       └── schemas.py       # Pydantic request/response models
├── examples/                # Example prompts + expected specs
├── tests/                   # pytest suite
├── requirements.txt
├── .env.example
└── README.md
```

## API reference

### `POST /v1/generate`

**Request**
```json
{
  "prompt": "a mounting bracket 80mm wide with four M5 holes",
  "output_format": "step"
}
```

**Response**
```json
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

### `GET /healthz`
Liveness probe. Returns `{"status": "ok"}`.

## Roadmap

- [ ] Add assembly support (multi-part designs)
- [ ] Feedback loop — let users correct generated specs and fine-tune prompts
- [ ] Web UI with 3D preview (three.js)
- [ ] Offline/local LLM backend (llama.cpp)

## License

MIT — see `LICENSE`.


# ============================================================
# FILE: .env.example
# ============================================================
# Choose one provider
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Which provider to use: "anthropic" or "openai"
LLM_PROVIDER=anthropic
LLM_MODEL=claude-opus-4-5

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Output
ARTIFACT_DIR=./artifacts


# ============================================================
# FILE: .gitignore
# ============================================================
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Env / secrets
.env
.env.local

# CAD outputs
artifacts/
*.step
*.stl
*.stp
!examples/*.step
!examples/*.stl

# IDE
.idea/
.vscode/
*.swp
.DS_Store


# ============================================================
# FILE: requirements.txt
# ============================================================
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.5.2
python-dotenv==1.0.1
anthropic==0.39.0
openai==1.51.0
cadquery==2.4.0
trimesh==4.4.9
numpy==1.26.4
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0


# ============================================================
# FILE: LICENSE
# ============================================================
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


# ============================================================
# FILE: app/__init__.py
# ============================================================


# ============================================================
# FILE: app/main.py
# ============================================================
"""CAD LLM Platform - FastAPI entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import generate, health

app = FastAPI(
    title="CAD LLM Platform",
    description="Generate parametric CAD designs from natural language prompts.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generate.router, prefix="/v1")


@app.get("/")
def root():
    return {
        "service": "cad-llm-platform",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


# ============================================================
# FILE: app/config.py
# ============================================================
"""Environment-driven settings."""
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    llm_model: str = "claude-opus-4-5"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # Output
    artifact_dir: Path = Path("./artifacts")

    def ensure_dirs(self) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()


# ============================================================
# FILE: app/models/__init__.py
# ============================================================


# ============================================================
# FILE: app/models/schemas.py
# ============================================================
"""Request and response schemas."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    output_format: Literal["step", "stl", "svg"] = "step"
    units: Literal["mm", "in"] = "mm"


class Feature(BaseModel):
    type: str               # "hole", "slot", "chamfer", "fillet", ...
    diameter: Optional[float] = None
    count: Optional[int] = None
    radius: Optional[float] = None


class DesignSpec(BaseModel):
    primitive: str          # "plate", "bracket", "cylinder", ...
    dimensions: dict[str, float]
    features: list[Feature] = []
    notes: Optional[str] = None


class GenerateResponse(BaseModel):
    spec: DesignSpec
    artifact_url: str
    preview_svg: Optional[str] = None


# ============================================================
# FILE: app/routes/__init__.py
# ============================================================


# ============================================================
# FILE: app/routes/generate.py
# ============================================================
"""POST /v1/generate — natural language -> CAD artifact."""
from fastapi import APIRouter, HTTPException

from app.models.schemas import DesignSpec, GenerateRequest, GenerateResponse
from app.services import cad_engine, llm_client

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    # 1. Ask the LLM to extract a structured spec.
    try:
        client = llm_client.get_client()
        raw_spec = client.complete(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}") from e

    # 2. Validate into our Pydantic schema.
    try:
        spec = DesignSpec.model_validate(raw_spec)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"LLM returned an invalid spec: {e}",
        ) from e

    # 3. Build geometry + export.
    try:
        path, preview = cad_engine.build_and_export(spec, req.output_format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAD build failed: {e}") from e

    return GenerateResponse(
        spec=spec,
        artifact_url=f"/artifacts/{path.name}",
        preview_svg=preview,
    )


# ============================================================
# FILE: app/routes/health.py
# ============================================================
"""Liveness probe."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


# ============================================================
# FILE: app/services/__init__.py
# ============================================================


# ============================================================
# FILE: app/services/llm_client.py
# ============================================================
"""Thin abstraction over LLM providers."""
from __future__ import annotations

import json
from typing import Protocol

from app.config import settings
from app.services.prompt import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES


class LLMClient(Protocol):
    def complete(self, user_prompt: str) -> dict: ...


class AnthropicClient:
    def __init__(self, model: str, api_key: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def complete(self, user_prompt: str) -> dict:
        messages = [*FEW_SHOT_EXAMPLES, {"role": "user", "content": user_prompt}]
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return _extract_json(resp.content[0].text)


class OpenAIClient:
    def __init__(self, model: str, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, user_prompt: str) -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *FEW_SHOT_EXAMPLES,
            {"role": "user", "content": user_prompt},
        ]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        return _extract_json(resp.choices[0].message.content)


def _extract_json(text: str) -> dict:
    """Tolerant JSON extraction: strips ```json fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip("`\n ")
    return json.loads(cleaned)


def get_client() -> LLMClient:
    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return AnthropicClient(settings.llm_model, settings.anthropic_api_key)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        return OpenAIClient(settings.llm_model, settings.openai_api_key)
    raise ValueError(f"Unknown provider: {settings.llm_provider}")


# ============================================================
# FILE: app/services/prompt.py
# ============================================================
"""System prompt + few-shot examples for spec extraction."""

SYSTEM_PROMPT = """You are a CAD design assistant. Convert the user's natural-language
description of a mechanical part into a strict JSON design spec.

Output ONLY valid JSON matching this schema:
{
  "primitive":  one of ["plate", "bracket", "cylinder", "box", "tube"],
  "dimensions": object of named numeric dimensions in millimeters,
  "features":   optional array of {"type": str, "diameter"?, "count"?, "radius"?},
  "notes":      optional short string
}

Rules:
- All dimensions are in millimeters unless the user explicitly says inches.
- If a dimension is missing, pick a reasonable default and mention it in `notes`.
- Never invent exotic features the user didn't ask for.
- Never include prose outside the JSON."""


FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "a rectangular plate 100x60x5mm with a 10mm hole in the center",
    },
    {
        "role": "assistant",
        "content": (
            '{"primitive": "plate", '
            '"dimensions": {"length": 100, "width": 60, "thickness": 5}, '
            '"features": [{"type": "hole", "diameter": 10, "count": 1}]}'
        ),
    },
    {
        "role": "user",
        "content": "a mounting bracket 80mm wide with four M5 holes",
    },
    {
        "role": "assistant",
        "content": (
            '{"primitive": "bracket", '
            '"dimensions": {"width": 80, "height": 40, "thickness": 5}, '
            '"features": [{"type": "hole", "diameter": 5.0, "count": 4}], '
            '"notes": "Assumed 40mm height and 5mm thickness."}'
        ),
    },
]


# ============================================================
# FILE: app/services/cad_engine.py
# ============================================================
"""Convert a DesignSpec into geometry and export it."""
from __future__ import annotations

import uuid
from pathlib import Path

from app.config import settings
from app.models.schemas import DesignSpec


def build_and_export(spec: DesignSpec, output_format: str) -> tuple[Path, str]:
    """Build geometry from spec, export, and return (artifact_path, svg_preview)."""
    try:
        import cadquery as cq
    except ImportError as e:
        raise RuntimeError(
            "cadquery is not installed. See README for setup."
        ) from e

    solid = _build(cq, spec)

    filename = f"{uuid.uuid4().hex[:8]}.{output_format}"
    path = settings.artifact_dir / filename

    if output_format == "step":
        cq.exporters.export(solid, str(path))
    elif output_format == "stl":
        cq.exporters.export(solid, str(path), exportType="STL")
    elif output_format == "svg":
        cq.exporters.export(solid, str(path), exportType="SVG")
    else:
        raise ValueError(f"Unsupported format: {output_format}")

    # Always also render an SVG preview for the UI
    svg_preview_path = path.with_suffix(".preview.svg")
    cq.exporters.export(solid, str(svg_preview_path), exportType="SVG")
    svg_preview = svg_preview_path.read_text()

    return path, svg_preview


def _build(cq, spec: DesignSpec):
    """Dispatch on primitive type."""
    dims = spec.dimensions
    if spec.primitive == "plate":
        solid = cq.Workplane("XY").box(
            dims["length"], dims["width"], dims["thickness"]
        )
    elif spec.primitive == "box":
        solid = cq.Workplane("XY").box(
            dims.get("length", 50),
            dims.get("width", 50),
            dims.get("height", 50),
        )
    elif spec.primitive == "cylinder":
        solid = cq.Workplane("XY").cylinder(
            dims.get("height", 50), dims.get("radius", 25)
        )
    elif spec.primitive == "bracket":
        # Simple L-bracket
        w = dims.get("width", 80)
        h = dims.get("height", 40)
        t = dims.get("thickness", 5)
        solid = (
            cq.Workplane("XY")
            .box(w, h, t)
            .faces(">Y").workplane()
            .box(w, t, h, combine=True)
        )
    elif spec.primitive == "tube":
        solid = (
            cq.Workplane("XY")
            .cylinder(dims.get("height", 50), dims.get("outer_radius", 25))
            .faces(">Z").workplane()
            .hole(dims.get("inner_radius", 15) * 2)
        )
    else:
        raise ValueError(f"Unknown primitive: {spec.primitive}")

    # Apply features
    for feature in spec.features:
        if feature.type == "hole" and feature.diameter:
            solid = _apply_holes(solid, feature.diameter, feature.count or 1)

    return solid


def _apply_holes(solid, diameter: float, count: int):
    """Add `count` through-holes arranged on the top face."""
    wp = solid.faces(">Z").workplane()
    if count == 1:
        return wp.hole(diameter)
    # Simple linear distribution along X
    positions = [(i - (count - 1) / 2) * 15 for i in range(count)]
    return wp.pushPoints([(x, 0) for x in positions]).hole(diameter)


# ============================================================
# FILE: tests/__init__.py
# ============================================================


# ============================================================
# FILE: tests/test_api.py
# ============================================================
"""Basic tests that don't require a real LLM key."""
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import DesignSpec, Feature

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "cad-llm-platform"


def test_design_spec_validates():
    spec = DesignSpec(
        primitive="plate",
        dimensions={"length": 100, "width": 60, "thickness": 5},
        features=[Feature(type="hole", diameter=10.0, count=1)],
    )
    assert spec.primitive == "plate"
    assert spec.features[0].diameter == 10.0


# ============================================================
# FILE: examples/prompts.md
# ============================================================
# Example prompts

A grab bag of prompts that work well with the system. Feed them to
`POST /v1/generate`.

---

**Simple plate**
> a rectangular plate 100x60x5mm with a 10mm hole in the center

**Bracket**
> a mounting bracket 80mm wide with four M5 holes

**Flanged cylinder**
> a cylinder 40mm tall, 25mm radius, with a 10mm through-hole

**Box with fillets**
> a box 50x50x30mm with 3mm fillets on all vertical edges

**Tube**
> a tube 60mm long, 20mm outer radius, 15mm inner radius


