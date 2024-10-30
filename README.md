# OpenFAN UnRAID Service

OpenFAN UnRAID service runs in parallel to OpenFAN Controller docker container.
This package is designed to work on UnRAID system that has [OpenFAN hardware](https://shop.sasakaranovic.com/products/openfan-pc-fan-controller) installed and running [OpenFAN Controller container](https://unraid.net/community/apps?q=OpenFanController#r) running.


## What does it do?

This is a very simple (monkey code, poorly written, slapped together, early alpha, you decide) python/docker project that allows you to individually control fan speed based on hard-disk temperature of your UnRAID system.

This project leverages disk temperatures that are reported by UnRAID system in the Web UI and it should work on every UnRAID setup.

## Why?

At the time of starting this project, there was no "easy" way of automating your fan speed based on temperatures reported by UnRAID.
And by "easy" I mean one that would work on every machine. Something that people can just copy&paste, tweak one file and it's working.

p.s. Obviously there are many ways to achieve this through plugins, scripting, third-party apps etc. But those might not be very easy options for less advanced users.


## How does it work?

You create a docker container and it will run as a background service.

It will load all fan profiles (temperature-to-fan-speed mapping) from `fan_profiles.yaml`.

Every `10sec` it will:
- Read hard drive temperatures from `disks.ini`. These are reported by UnRAID OS.
- Calculate what each fan RPM/PWM should be based on the temperature of the 'assigned' disk.
- Make an API call to OpenFAN Controller API server to update each individual fan

# Installation

## Automatic installation

TBD: Waiting for community application review and approval.

## Manually starting docker container

Make sure you have created your `fan_profiles.yaml` file.
In the below example we assume it's located at `/mnt/user/appdata/openfanservice/fan_profiles.yaml`

```
docker run -d --name OpenFANservice \
-v /var/local/emhttp:/mnt/OpenFanService/sensors:ro \
-v /mnt/user/appdata/openfanservice/fan_profiles.yaml:/mnt/OpenFanService/data/fan_profiles.yaml:ro \
-e "OPENFAN_HOST=192.168.10.25" \
-e "OPENFAN_PORT=3000" \
-e "OPENFAN_SENSORS=/mnt/OpenFanService/sensors/disks.ini" \
-e "OPENFAN_PROFILE=/mnt/OpenFanService/data/fan_profiles.yaml" \
-e "OPENFAN_RELOAD=True" \
ghcr.io/sasakaranovic/openfanunraidservice:release
```

- `-v /var/local/emhttp:/mnt/OpenFanService/sensors:ro` - Mount sensor data to docker container (as read-only)
- `-v /mnt/user/appdata/openfanservice/fan_profiles.json:/mnt/OpenFanService/data/fan_profiles.json:ro` - Mount fan profiles .json file to docker container (as read-only)
- `-e "OPENFAN_HOST=192.168.10.25"` - IP address of the OpenFAN Controller docker container
- `-e "OPENFAN_PORT=3000"` - API port used by OpenFAN Controller docker container
- `-e "OPENFAN_SENSORS=/mnt/OpenFanService/sensors/disks.ini"` - Path to .ini file containing sensor/disk information
- `-e "OPENFAN_PROFILE=/mnt/OpenFanService/data/fan_profiles.yaml"` - Path to .yaml file containing fan profiles
- `-e "OPENFAN_RELOAD=True"` - Set to True will force the app to reload fan-profiles before recalculating new fans speed. This can be used to allow hot-reloading new fan profile data without having to restart the container. If False, fan profile data will be read once on container startup.



# Configuration

## What do items in `fan_profiles.yaml` mean?

Below is an example of a simple fan_profiles.yaml file with comments explaining what each line does

It's recommended that you double check your .yaml file for any syntax errors before starting the container.
There are many online syntax validation tools (ie. https://https://yamlchecker.com//)

FanProfiles section is list of fan profiles/curves that you want to define.
Each fan profile must have unique name.


```
__app_version__: '2'

FanProfiles:
  - Name: DefaultProfile      # Unique profile name
    TempSource: parity        # Which sensor (disk temperature) to use for fan curve
    UsePWM: false             # true means values in `points` section are expressed as PWM (0-100) instead of fan RPM.
    CurveType: threshold      # `threshold` curve will treat `Points` as simple thresholds
    Points:
      - '0,500'               # Value before `,` is temperature. Value after `,` is fan RPM/PWM
      - '20,700'              # Value before `,` is temperature. Value after `,` is fan RPM/PWM
      - '35,1000'             # Value before `,` is temperature. Value after `,` is fan RPM/PWM
      - '45,1500'             # Value before `,` is temperature. Value after `,` is fan RPM/PWM

  - Name: SomeOtherProfile    # Unique profile name
    TempSource: disk1         # Which sensor (disk temperature) to use for fan curve
    UsePWM: false             # true means values in `points` section are expressed as PWM (0-100) instead of fan RPM.
    CurveType: linear         # `linear` curve will interpolate between the two temperature points and calculate the fan speed
    Points:                   #
      - '0,500'               # Value before `,` is temperature. Value after `,` is fan RPM/PWM
      - '30,1000'             # Value before `,` is temperature. Value after `,` is fan RPM/PWM
      - '45,1500'             # Value before `,` is temperature. Value after `,` is fan RPM/PWM

  - Name: FixedRPM            # Unique profile name
    TempSource: disk1         # Which sensor (disk temperature) to use for fan curve
    UsePWM: false             # true means values in `points` section are expressed as PWM (0-100) instead of fan RPM.
    Points:
      - '0,1000'              # Basically regardless of temperature, fans assigned to this profile will always run at 1000 RPM

FanControls:
  - Identifier: OpenFAN/Fan/1 # Unique fan identifier (Fan #)
    Name: 'Fan #1'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/2 # Unique fan identifier (Fan #)
    Name: 'Fan #2'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/3 # Unique fan identifier (Fan #)
    Name: 'Fan #3'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/4 # Unique fan identifier (Fan #)
    Name: 'Fan #4'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/5 # Unique fan identifier (Fan #)
    Name: 'Fan #5'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/6 # Unique fan identifier (Fan #)
    Name: 'Fan #6'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/7 # Unique fan identifier (Fan #)
    Name: 'Fan #7'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/8 # Unique fan identifier (Fan #)
    Name: 'Fan #8'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/9 # Unique fan identifier (Fan #)
    Name: 'Fan #9'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

  - Identifier: OpenFAN/Fan/9 # Unique fan identifier (Fan #)
    Name: 'Fan #9'            # User-friendly fan name
    AssignedProfile: ''       # Pick which fan profile/curve should this fan follow

```

<br/><br/>

---

#### Sasa Karanovic

<a href="https://sasakaranovic.com/" target="_blank" title="Sasa Karanovic Home Page"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_home.png" width="16"> Home Page</a> &nbsp;&middot;&nbsp;
<a href="https://youtube.com/c/sasakaranovic" target="_blank" title="Sasa Karanovic on YouTube"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_youtube.png" width="16"> YouTube</a> &nbsp;&middot;&nbsp;
<a href="https://github.com/sasakaranovic" target="_blank" title="Sasa Karanovic on GitHub"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_github.png" width="16"> GitHub</a> &nbsp;&middot;&nbsp;
<a href="https://twitter.com/_sasakaranovic_" target="_blank" title="Sasa Karanovic on Twitter"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_twitter.png" width="16"> Twitter</a> &nbsp;&middot;&nbsp;
<a href="https://instagram.com/_sasakaranovic_" target="_blank" title="Sasa Karanovic on Instagram"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_instagram.png" width="16"> Instagram</a> &nbsp;&middot;&nbsp;
<a href="https://github.com/sponsors/SasaKaranovic" target="_blank" title="Sponsor on GitHub"><img src="https://raw.githubusercontent.com/SasaKaranovic/common/master/assets/img_github.png" width="16"> Sponsor on GitHub</a>
