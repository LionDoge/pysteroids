from ursina import *

_apsect_ratio_inv = 1.0 / window.aspect_ratio

def wrap_around_position(pos, pad):
    x = pos.x * _apsect_ratio_inv
    y = pos.y

    pad_x = pad * _apsect_ratio_inv

    if x < -0.5 - pad_x:
        pos.x = (0.5 * window.aspect_ratio) + pad_x
    elif x > 0.5 + pad_x:
        pos.x = (-0.5 * window.aspect_ratio) - pad_x

    if y < -0.5 - pad:
        pos.y = 0.5 + pad
    elif y > 0.5 + pad:
        pos.y = -0.5 - pad
    return pos

def is_out_of_bounds(pos, pad):
    x = pos.x * _apsect_ratio_inv
    y = pos.y

    pad_x = pad * _apsect_ratio_inv

    if x < -0.5 - pad_x or x > 0.5 + pad_x or y < -0.5 - pad or y > 0.5 + pad:
        return True
    return False