from unittest import mock

from api_cheerlights import Cheerlight, cheerlights_confirm, api_request


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_new_color_defaults_to_red_on_invalid_color_name(mocked_neopixel):
    cheerlight = Cheerlight(0, 1)
    cheerlight.new_color('beige')
    assert cheerlight.target == (255, 0, 0)


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_new_color_sets_target_for_all_cheerlights(mocked_neopixel):
    cheerlights = [Cheerlight(i, 1) for i in range(3)]
    Cheerlight.new_color('blue')
    for cheerlight in cheerlights:
        assert cheerlight.target == (0, 0, 255)


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_in_sync_returns_correct_value(mocked_neopixel):
    cheerlight = Cheerlight(5, 1)
    cheerlight.color = (0, 0, 0)
    cheerlight.target = (1, 111, 222)
    assert not cheerlight.in_sync()

    cheerlight.color = (1, 111, 222)
    assert cheerlight.in_sync()


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_write_calls_the_required_neopixel_methods(mocked_neopixel):
    cheerlight = Cheerlight(9, 4)
    mocked_neopixel.reset_mock()

    cheerlight.write((4, 5, 6))
    expected_calls = [mock.call().fill((4, 5, 6)),
                      mock.call().write()]
    assert mocked_neopixel.mock_calls == expected_calls
    assert cheerlight.color == (4, 5, 6)


@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_off_sets_the_cheerlight_to_off(mocked_neopixel):
    cheerlight = Cheerlight(8, 3)
    mocked_neopixel.reset_mock()
    cheerlight.color = (130, 140, 150)

    cheerlight.off()
    expected_calls = [mock.call().fill((0, 0, 0)),
                      mock.call().write()]
    assert mocked_neopixel.mock_calls == expected_calls
    assert cheerlight.color == (0, 0, 0)


@mock.patch('api_cheerlights.time')
@mock.patch('api_cheerlights.neopixel.NeoPixel')
def test_transition_moves_the_rgb_values_towards_the_target(mocked_neopixel,
                                                            mocked_time):
    cheerlight = Cheerlight(2, 2)
    cheerlight.color = (100, 2, 123)
    cheerlight.target = (255, 2, 0)

    cheerlight.transition()
    assert cheerlight.color == (101, 2, 122)


@mock.patch('api_cheerlights.time')
@mock.patch('api_cheerlights.Cheerlight')
def test_cheerlights_confirm_flashes_all_cheerlights(mocked_cheerlight,
                                                     mocked_time):
    mocked_cheerlight.colors = {'green': (0, 255, 0), 'red': (255, 0, 0)}
    cheerlights = [mocked_cheerlight for _ in range(2)]

    cheerlights_confirm(cheerlights, False)
    expected_calls = [mock.call.write((255, 0, 0)),
                      mock.call.write((255, 0, 0)),
                      mock.call.off(),
                      mock.call.off(),
                      mock.call.write((255, 0, 0)),
                      mock.call.write((255, 0, 0)),
                      mock.call.off(),
                      mock.call.off(),
                      mock.call.write((255, 0, 0)),
                      mock.call.write((255, 0, 0)),
                      mock.call.off(),
                      mock.call.off()]
    assert mocked_cheerlight.mock_calls == expected_calls

    mocked_cheerlight.reset_mock()
    cheerlights_confirm(cheerlights, True)
    expected_calls = [mock.call.write((0, 255, 0)),
                      mock.call.write((0, 255, 0)),
                      mock.call.off(),
                      mock.call.off(),
                      mock.call.write((0, 255, 0)),
                      mock.call.write((0, 255, 0)),
                      mock.call.off(),
                      mock.call.off(),
                      mock.call.write((0, 255, 0)),
                      mock.call.write((0, 255, 0)),
                      mock.call.off(),
                      mock.call.off()]
    assert mocked_cheerlight.mock_calls == expected_calls


@mock.patch('api_cheerlights.urequests.get')
def test_api_requests_returns_correct_element_from_json(mocked_requests):
    test_json = {"created_at": "2018-11-17T23:43:34Z",
                 "entry_id": 490378,
                 "field1": "red",
                 "field2": "#FDF5E6"
                 }
    mocked_requests().json.return_value = test_json

    assert api_request('some_url.com/cheerlights') == 'red'
