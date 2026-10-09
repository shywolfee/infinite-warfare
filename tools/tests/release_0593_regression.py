"""Validate release metadata and the explicit device/supply content contract."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "iwserver/content"

def props(path):
    return dict(line.split("=", 1) for line in path.read_text(encoding="utf-8-sig").splitlines()
                if "=" in line and not line.startswith("#"))

assert (ROOT / "version.txt").read_text().strip() == "0.5.9.3"
client = (ROOT / "Infinite Warfare.nvgt").read_text(encoding="utf-8-sig")
assert 'string version_name="0.5.9.3";' in client
assert re.search(r"int build_number\s*=\s*103;", client)
items = {p.stem: props(p) for p in (CONTENT / "items").rglob("*.item")}
weapons = {p.stem: props(p) for p in (CONTENT / "weapons").rglob("*.wpn")}
offers = {}
for path in (CONTENT / "marketplace").rglob("*.offer"):
    d = props(path)
    assert path.stem not in offers, f"Duplicate offer: {path.stem}"
    assert d["item"] in items or d["item"] in weapons, path
    assert 1 <= int(d["quantity"]) <= 1000, path
    assert 1 <= int(d["max_order"]) <= 100, path
    assert 1 <= int(d["price"]) <= 1_000_000, path
    assert not any(c in d[key] for c in "~;|\r\n" for key in ("name", "summary", "category")), path
    if d["item"] in items:
        assert not items[d["item"]].get("currency_kind"), path
        assert items[d["item"]].get("market_excluded") != "true", path
    offers[path.stem] = d
assert len(offers) >= 350
assert all(id in offers for id in weapons), "Every firearm needs an explicit offer"
assert items["translocator_cell"]["category"] == "Utility"
assert (CONTENT / "items/utility/translocator_cell.item").exists()
assert items["bomb_vest"]["category"] == "Explosives"
assert "does not provide armour" in items["bomb_vest"]["summary"].lower()
assert items["bowling_bomb"]["flight_mandatory"] == "true"
assert float(items["bowling_bomb"]["flight_volume_db"]) > 0
devices = {id: d for id, d in items.items() if d.get("device_profile")}
assert len(devices) == 7
assert {id for id, d in devices.items() if d.get("device_extensible") == "true"} == {"field_tablet", "signal_handset"}
for path in (CONTENT / "device_modules").rglob("*.app"):
    d = props(path)
    assert d["handler"] in {"scanner", "ballistics", "vehicle_diagnostics"}, path
    assert int(d["size"]) > 0 and int(d["price"]) >= 0, path
    for id in d["devices"].split(","):
        assert devices[id]["device_extensible"] == "true", path
print(f"PASS 0.5.9.3: {len(offers)} offers, {len(devices)} devices, valid release metadata")
