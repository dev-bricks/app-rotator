from app_rotator.tray import create_icon


def test_packaged_tray_icon_is_transparent_and_square():
    icon = create_icon()

    assert icon.mode == "RGBA"
    assert icon.size == (512, 512)
    assert icon.getbbox() is not None
    assert icon.getpixel((0, 0))[3] == 0
