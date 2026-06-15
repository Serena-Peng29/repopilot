from __future__ import annotations

import json
from pathlib import Path

from repopilot.models import ProviderConfig, ProviderSpec


def load_provider_config(path: Path) -> list[ProviderSpec]:
    data = json.loads(path.read_text(encoding="utf-8"))
    config = ProviderConfig.model_validate(data)
    return config.providers


def provider_specs_from_names(provider_names: list[str]) -> list[ProviderSpec]:
    specs: list[ProviderSpec] = []
    for provider_name in provider_names:
        if provider_name.startswith("shell:"):
            name = provider_name.split(":", 1)[1]
            specs.append(ProviderSpec(name=provider_name, type="shell", provider=name))
        else:
            specs.append(ProviderSpec(name=provider_name, type="builtin", provider=provider_name))
    return specs
