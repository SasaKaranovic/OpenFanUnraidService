# Change log

## 2025-05-31

- Adding support for multiple temperature sensors. Temperature source `TempSource` can now be a list of sensors.
- Adding option to specify how `TempSource` list should be evaluated. Default is `max` which finds temperature sensor with the highest temperature and uses it's value for for applying the fan curve. It is possible to explicitly request `min` as the eval function. Although using `min` is probably a really bad idea, but it's there if you need it.
- If not specified, default fan curve will be `linear`
- If no temperature source (`TempSource`) is specified in fan profile, and error will be raised instead of current silent behaviour.
- If temperature sensor does not exist, temperature of `-1` will be returned (previously it would return `0`). Now it is easy to differentiate between missing sensor/disk (`-1`) and a spun-down disk (`0`). If you use LN2 for cooling and this causes issues for you, let me know.


## 2024-10-09

- Switching to using .yaml instead of .json for fan profiles.

## Initial release

Initial release of OpenFAN Unraid Service
