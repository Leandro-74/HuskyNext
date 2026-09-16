import colorsys

DEFAULT_CALIBRATION = {
    "channel_order": "RGB",
    "gamma": 1.0,
    "brightness": 1.0,
    "saturation": 1.0,
    "min_value": 0.0,
    "max_value": 1.0,
}

def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

def _clamp255(value: float) -> int:
    return max(0, min(255, int(round(value))))

def apply_calibration(r: int, g: int, b: int, calibration: dict | None = None) -> tuple[int, int, int]:
    cfg = DEFAULT_CALIBRATION.copy()

    if calibration:
        cfg.update(calibration)

    mapping = {
        "R": r,
        "G": g,
        "B": b,
    }

    order = str(cfg.get("channel_order", "RGB")).upper()

    if len(order) == 3 and set(order) == set("RGB"):
        out_r = mapping[order[0]]
        out_g = mapping[order[1]]
        out_b = mapping[order[2]]
    else:
        out_r, out_g, out_b = r, g, b

    nr = out_r / 255
    ng = out_g / 255
    nb = out_b / 255

    h, s, v = colorsys.rgb_to_hsv(nr, ng, nb)

    s = _clamp01(s * float(cfg.get("saturation", 1.0)))
    v = _clamp01(v * float(cfg.get("brightness", 1.0)))

    min_value = _clamp01(float(cfg.get("min_value", 0.0)))
    max_value = _clamp01(float(cfg.get("max_value", 1.0)))

    if min_value > max_value:
        min_value, max_value = max_value, min_value

    v = max(min_value, min(max_value, v))

    fr, fg, fb = colorsys.hsv_to_rgb(h, s, v)

    gamma = float(cfg.get("gamma", 1.0))

    if gamma > 0 and gamma != 1.0:
        fr = fr ** gamma
        fg = fg ** gamma
        fb = fb ** gamma

    return (
        _clamp255(fr * 255),
        _clamp255(fg * 255),
        _clamp255(fb * 255),
    )