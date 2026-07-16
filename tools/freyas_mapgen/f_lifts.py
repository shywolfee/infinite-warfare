"""The two turbolifts of Freya's Ascent - one at the forward (north) end and one
at the aft (south) end of every deck - each serving the cargo hold and all seven
decks."""
import structures as S
import config as C


def build(m):
    m.section("TURBOLIFTS (forward and aft, serving the cargo hold and all decks)")
    stops = C.LIFT_STOPS
    zs = [z for _, z in stops]

    nx1, nx2, ny1, ny2 = C.LIFT_N
    S.turbolift_tower(m, "the forward turbolift", nx1, nx2, ny1, ny2, stops,
                      exits={z: "S" for z in zs})
    m.poi((nx1 + nx2) // 2, (ny1 + ny2) // 2, C.DECK1, "the forward turbolift")

    sx1, sx2, sy1, sy2 = C.LIFT_S
    S.turbolift_tower(m, "the aft turbolift", sx1, sx2, sy1, sy2, stops,
                      exits={z: "N" for z in zs})
    m.poi((sx1 + sx2) // 2, (sy1 + sy2) // 2, C.DECK1, "the aft turbolift")
