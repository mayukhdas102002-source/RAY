"""Local brand-voice TTS for OpenMontage: Voicebox and VoiceStudio providers.

Install: copy this file to  OpenMontage/tools/audio/local_voice_tts.py
The registry auto-discovers it; tts_selector can then pick `voicebox` / `voicestudio`
(pass preferred_provider="voicebox" to force it). Log the addition in the project's
decision_log as category "capability_extension".

Env (OpenMontage/.env):
  VOICEBOX_URL=http://127.0.0.1:17493      VOICEBOX_PROFILE=<profile name or id>
  VOICESTUDIO_URL=http://127.0.0.1:3900    VOICESTUDIO_PROFILE=<profile name or id>
  VOICESTUDIO_ENGINE=voxcpm2               (commercial-safe; OmniVoice weights are CC-BY-NC)

Both run on the user's machine; cost is $0. Output is WAV (24 kHz mono from most engines).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from abc import abstractmethod
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


def _http(method: str, url: str, body: bytes | None = None, headers: dict | None = None, timeout: float = 900):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, {}, e.read() or b""
    except Exception as e:  # noqa: BLE001
        return 0, {}, str(e).encode()


def _alive(url: str) -> bool:
    code, _, _ = _http("GET", url.rstrip("/") + "/health", timeout=2)
    return 0 < code < 500


def _profile_id(base: str, ref: str) -> str | None:
    code, _, data = _http("GET", base + "/profiles", timeout=20)
    if code != 200:
        return None
    for p in json.loads(data):
        if p.get("id") == ref or str(p.get("name", "")).lower() == ref.lower():
            return p.get("id")
    return None


class _LocalVoiceBase(BaseTool):
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL
    agent_skills = ["text-to-speech"]
    capabilities = ["text_to_speech", "voice_cloning", "offline_generation"]
    supports = {"voice_cloning": True, "multilingual": True, "offline": True, "native_audio": True}
    best_for = ["consistent cloned brand voice", "zero-cost local narration", "privacy-sensitive scripts"]
    not_good_for = ["machines without the desktop app running"]
    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "output_path": {"type": "string"},
            "profile": {"type": "string", "description": "Profile name or id (defaults to env)"},
            "engine": {"type": "string"},
            "seed": {"type": "integer"},
            "language": {"type": "string"},
            "instruct": {"type": "string"},
        },
    }
    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=4096, vram_mb=0, disk_mb=50, network_required=False)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=[])
    idempotency_key_fields = ["text", "profile", "engine", "seed"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = ["Listen to the sample line before batching"]

    url_env = ""
    default_url = ""
    profile_env = ""

    def _base(self) -> str:
        return (os.environ.get(self.url_env) or self.default_url).rstrip("/")

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if _alive(self._base()) else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(success=False, error=f"{self.provider} is not running at {self._base()}. " + self.install_instructions)
        ref = inputs.get("profile") or os.environ.get(self.profile_env, "")
        pid = _profile_id(self._base(), ref) if ref else None
        if not pid:
            return ToolResult(success=False, error=f"{self.provider}: profile '{ref}' not found. Set {self.profile_env} or pass profile.")
        out = Path(inputs.get("output_path") or f"{self.provider}_{int(time.time())}.wav")
        out.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        err = self._generate(pid, inputs, out)
        if err:
            return ToolResult(success=False, error=err)
        return ToolResult(success=True, data={"provider": self.provider, "profile_id": pid, "output": str(out), "format": "wav"},
                          artifacts=[str(out)], seed=inputs.get("seed"), model=inputs.get("engine") or self.provider,
                          duration_seconds=round(time.time() - start, 2), cost_usd=0.0)

    @abstractmethod
    def _generate(self, pid: str, inputs: dict[str, Any], out: Path) -> str | None:
        """Write WAV to `out`; return an error string or None."""


class VoiceboxTTS(_LocalVoiceBase):
    name = "voicebox_tts"
    provider = "voicebox"
    url_env, default_url, profile_env = "VOICEBOX_URL", "http://127.0.0.1:17493", "VOICEBOX_PROFILE"
    dependencies = []
    install_instructions = "Install and open Voicebox (https://voicebox.sh); clone the brand voice; API on 127.0.0.1:17493."

    def _generate(self, pid: str, inputs: dict[str, Any], out: Path) -> str | None:
        body = {"profile_id": pid, "text": inputs["text"], "language": inputs.get("language", "en"), "normalize": True}
        for k in ("seed", "engine", "instruct"):
            if inputs.get(k) is not None:
                body[k] = inputs[k]
        code, _, data = _http("POST", self._base() + "/generate/stream", json.dumps(body).encode(), {"Content-Type": "application/json"})
        if code == 200 and data[:4] == b"RIFF":
            out.write_bytes(data)
            return None
        return f"Voicebox /generate/stream -> {code}: {data[:300]!r} (generate once in the app to download the model)"


class VoiceStudioTTS(_LocalVoiceBase):
    name = "voicestudio_tts"
    provider = "voicestudio"
    url_env, default_url, profile_env = "VOICESTUDIO_URL", "http://127.0.0.1:3900", "VOICESTUDIO_PROFILE"
    dependencies = []
    install_instructions = "Install VoiceStudio (https://voicestudio.sh), accept model licences, clone the brand voice; API on 127.0.0.1:3900."

    def _generate(self, pid: str, inputs: dict[str, Any], out: Path) -> str | None:
        engine = inputs.get("engine") or os.environ.get("VOICESTUDIO_ENGINE", "voxcpm2")
        fields = {"text": inputs["text"], "profile_id": pid, "engine": engine, "effect_preset": "raw", "wav_bits": "24"}
        if inputs.get("seed") is not None:
            fields["seed"] = str(inputs["seed"])
        if inputs.get("language"):
            fields["language"] = inputs["language"]
        b = "----om" + uuid.uuid4().hex
        body = b"".join(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode() for k, v in fields.items())
        body += f"--{b}--\r\n".encode()
        code, _, data = _http("POST", self._base() + "/generate", body, {"Content-Type": f"multipart/form-data; boundary={b}"})
        if code == 200:
            out.write_bytes(data)
            return None
        if code == 403:
            return "VoiceStudio refused: accept the model licence in Model Catalogue (or choose a commercial-safe engine)."
        return f"VoiceStudio /generate -> {code}: {data[:300]!r}"
