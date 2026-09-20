"""Compile ordered map tiles to disjoint metre-space volumes.

Later records replace earlier ones, including blank door/window cuts. This is
the static geometry stage, not a complete map physics implementation: ramps,
authored objects and structural ownership are explicitly retained for adapters.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import json
import hashlib
from pathlib import Path


@dataclass(frozen=True)
class Volume:
    lo: tuple[int, int, int]
    hi: tuple[int, int, int]  # Exclusive, in source tile-cell space.
    material: str
    source_line: int

    def contains(self, point):
        return all(a <= x < b for a, x, b in zip(self.lo, point, self.hi))

    def subtract(self, cut: Volume) -> list[Volume]:
        lo = tuple(max(a, b) for a, b in zip(self.lo, cut.lo))
        hi = tuple(min(a, b) for a, b in zip(self.hi, cut.hi))
        if any(a >= b for a, b in zip(lo, hi)):
            return [self]
        # Peel at most six disjoint slabs; never voxelize large maps.
        result = []
        remaining_lo, remaining_hi = list(self.lo), list(self.hi)
        for axis in range(3):
            if remaining_lo[axis] < lo[axis]:
                end = remaining_hi.copy()
                end[axis] = lo[axis]
                result.append(replace(self, lo=tuple(remaining_lo), hi=tuple(end)))
                remaining_lo[axis] = lo[axis]
            if remaining_hi[axis] > hi[axis]:
                start = remaining_lo.copy()
                start[axis] = hi[axis]
                result.append(replace(self, lo=tuple(start), hi=tuple(remaining_hi)))
                remaining_hi[axis] = hi[axis]
        return result

    def physical(self):
        # x/y integer coordinates denote cell centres. Integer z denotes the
        # top surface under a standing player's feet, not the body's centre.
        offset = (0.5, 0.5, 1.0)
        lo = [x - d for x, d in zip(self.lo, offset)]
        hi = [x - d for x, d in zip(self.hi, offset)]
        return dict(min=lo, max=hi, material=self.material,
                    kind='fluid' if self.material.startswith('water') else 'solid',
                    source_line=self.source_line)


def parse_tiles(text: str) -> list[Volume]:
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        fields = line.strip().split(':')
        if fields[0] != 'tile':
            continue
        if len(fields) != 8:
            raise ValueError(f'Invalid tile at line {number}: expected 8 fields')
        values = list(map(int, fields[1:7]))
        lo = tuple(values[::2])
        hi = tuple(v + 1 for v in values[1::2])
        if any(a >= b for a, b in zip(lo, hi)):
            raise ValueError(f'Reversed tile at line {number}')
        result.append(Volume(lo, hi, fields[7], number))
    return result


def compile_tiles(tiles: list[Volume]) -> list[Volume]:
    volumes = []
    for tile in tiles:
        volumes = [piece for old in volumes for piece in old.subtract(tile)]
        if tile.material not in ('blank', ''):
            volumes.append(tile)
    return volumes


def compile_map(path: Path) -> dict:
    text = path.read_text(encoding='utf-8-sig')
    volumes = compile_tiles(parse_tiles(text))
    adapters = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.split(':', 1)[0] in ('ramp', 'object', 'objectpart', 'fixture', 'openspace'):
            adapters.append(dict(source_line=number, record=line))
    return dict(schema=1, units='metres', source=path.name,
                source_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                geometry_stage='ordered-static-volumes',
                volumes=[v.physical() for v in volumes], adapter_records=adapters)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('map', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = compile_map(args.map)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',', ':')), encoding='utf-8')
    print(f'{args.map}: {len(result["volumes"])} disjoint volumes')


if __name__ == '__main__':
    main()
