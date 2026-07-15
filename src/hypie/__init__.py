from __future__ import annotations

from dataclasses import dataclass, field

from hypie.hs_ast.features import Feature
from hypie.commands import Set


@dataclass
class Hs:
    features: tuple[Feature] = field(default_factory=lambda: [])

    def render(self):
        return "\n".join(f.render() for f in self.features)

    def add_features(self, *feats: Hs | Feature):
        features = []

        for f in feats:
            if isinstance(f, Hs):
                features.extend(f.features)
            elif isinstance(f, (Feature, Set)):
                features.append(f)
        self.features = tuple([*self.features, *features])
        return self

    def __str__(self):
        return self.render()

    __html__ = __str__


def hs(*features):
    return Hs(features)
