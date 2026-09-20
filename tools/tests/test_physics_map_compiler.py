import importlib.util
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('compile_physics_maps', ROOT / 'tools/compile_physics_maps.py')
compiler = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = compiler
spec.loader.exec_module(compiler)


class OrderedGeometryTests(unittest.TestCase):
    def assert_matches(self, tiles, volumes, points):
        for point in points:
            expected = ''
            for tile in tiles:
                if tile.contains(point):
                    expected = '' if tile.material == 'blank' else tile.material
            found = [v for v in volumes if v.contains(point)]
            self.assertLessEqual(len(found), 1, f'Overlapping volumes at {point}')
            self.assertEqual(found[0].material if found else '', expected, point)

    def test_door_cut_and_floor_restoration(self):
        tiles = compiler.parse_tiles('tile:0:8:0:8:0:6:wallstone\n'
                                     'tile:1:7:1:7:0:5:blank\n'
                                     'tile:4:4:0:1:0:3:blank\n'
                                     'tile:1:7:0:7:0:0:wood1')
        volumes = compiler.compile_tiles(tiles)
        self.assert_matches(tiles, volumes, ((x,y,z) for x in range(9) for y in range(9) for z in range(7)))

    def test_one_coordinate_is_one_metre_and_floor_is_at_zero(self):
        volume = compiler.parse_tiles('tile:0:0:0:0:0:0:stone')[0].physical()
        self.assertEqual(volume['min'], [-.5,-.5,-1])
        self.assertEqual(volume['max'], [.5,.5,0])

    def test_invalid_geometry_rejected(self):
        with self.assertRaises(ValueError):
            compiler.parse_tiles('tile:4:1:0:0:0:0:stone')

    def test_all_authored_maps_against_original_last_write_rules(self):
        paths = sorted((ROOT / 'iwserver/content/maps').glob('*/*.map'))
        self.assertTrue(paths)
        rng = random.Random(511)
        for path in paths:
            with self.subTest(map=path):
                tiles = compiler.parse_tiles(path.read_text(encoding='utf-8-sig'))
                volumes = compiler.compile_tiles(tiles)
                points = []
                # Sample boundaries and interior cells of every source record,
                # especially blank openings that a simple union would seal.
                for tile in tiles:
                    points.extend((tile.lo, tuple(v-1 for v in tile.hi)))
                    points.extend(tuple(rng.randrange(a,b) for a,b in zip(tile.lo,tile.hi)) for _ in range(3))
                self.assert_matches(tiles, volumes, points)
                print(f'{path.parent.name}: {len(tiles)} records, {len(volumes)} volumes, {len(points)} parity points')


if __name__ == '__main__':
    unittest.main()
