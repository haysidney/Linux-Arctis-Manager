from linux_arctis_manager.status_parser_fn import int_int_mapping, int_str_mapping, on_off, percentage, two_sided_chatmix


def test_percentage():
    fn = percentage
    assert getattr(fn, '_status_type') == 'percentage'

    assert fn(0, 100, 0) == 0
    assert fn(-56, 0, -56) == 0

    assert fn(0, 100, 75) == 75
    assert fn(-200, 0, -50) == 75

    assert fn(0, 100, 100) == 100
    assert fn(-123, 123, 123) == 100

    # inverted range (perc_max < perc_min)
    assert fn(255, 191, 255) == 0
    assert fn(255, 191, 191) == 100
    assert fn(255, 191, 223) == 50
    # out-of-range values clamp
    assert fn(255, 191, 0) == 100
    assert fn(0, 100, 150) == 100

def test_on_off():
    fn = on_off
    assert getattr(fn, '_status_type') == 'on_off'

    assert fn(0x01, 0x01, 0) == 'on'
    assert fn(0, 1, 0) == 'off'
    assert fn(1, 1, 3) == 'on'
    assert fn(3, 2, 3) == 'off'

def test_int_str_mapping():
    fn = int_str_mapping
    mapping = {0x00: "off", 0x01: "-12db", 0x02: "on"}

    assert getattr(fn, '_status_type') == 'int_str_mapping'

    assert fn(mapping, 0x00) == "off"
    assert fn(mapping, 0x01) == "-12db"
    assert fn(mapping, 0x02) == "on"
    assert fn(mapping, 0x03) is None

def test_two_sided_chatmix():
    fn = two_sided_chatmix
    assert getattr(fn, '_status_type') == 'two_sided_chatmix'

    # value=0 means opposite side active → this channel at 100%
    assert fn(192, 255, 0) == 100
    # active range: 192=0%, 255=100%
    assert fn(192, 255, 192) == 0
    assert fn(192, 255, 255) == 100
    # midpoint
    assert fn(192, 255, 223) == 49
    # out of range clamps
    assert fn(192, 255, 100) == 0

def test_int_int_mapping():
    fn = int_int_mapping
    mapping = {0: 10, 1: 20, 2: 30}

    assert getattr(fn, '_status_type') == 'int_int_mapping'

    assert fn(mapping, 0) == 10
    assert fn(mapping, 1) == 20
    assert fn(mapping, 2) == 30
    assert fn(mapping, 3) is None
