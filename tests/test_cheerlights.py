from unittest import mock

from api_cheerlights import Cheerlight, cheerlights_confirm, api_request


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_new_color_falls_back_to_default_on_invalid_color_name(mocked_neopixel):
    cheerlight = Cheerlight(0, 1)
    cheerlight.new_color('beige')
    assert cheerlight.target == (255, 0, 0)


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_new_color_sets_target_for_all_cheerlights(mocked_neopixel):
    cheerlights = [Cheerlight(i, 1) for i in range(3)]
    Cheerlight.new_color('blue')
    for cheerlight in cheerlights:
        assert cheerlight.target == (0, 0, 255)


def test_in_sync_returns_correct_value():
    pass


def test_write_calls_the_required_neopixel_methods():
    pass


def test_off_sets_the_cheerlight_to_off():
    pass


def test_transition_moves_the_rgb_values_towards_the_target():
    pass


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_cheerlights_confirm_flashes_all_cheerlights(mocked_neopixel):
    pass
    # cheerlights = []
    # for i in range(2):
    #     cheerlight = Cheerlight(0, 1)
    #     cheerlights.append(cheerlight)
    #     cheerlights_confirm(True)
    #     expected_calls = (
    #     mocked_neopixel




@mock.patch('api_cheerlights.urequests.get')
def test_api_requests_returns_correct_element_from_json(mocked_requests):
    test_json = {"created_at": "2018-11-17T23:43:34Z",
                 "entry_id": 490378,
                 "field1": "red",
                 "field2": "#FDF5E6"
                 }
    mocked_requests().json.return_value = test_json

    assert api_request('some_url.com/cheerlights') == 'red'
