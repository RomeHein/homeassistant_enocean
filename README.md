# homeassistant_enocean

Enocean integration for homeassistant

This custom integration regroup PRs made on the homeassistant repo.
If you can't wait for the feature to be merged, you can go with this integration.

Here is the current status of the additional features it contains:

- Door detector profile `D5-00-01` as a binary sensor. From homeassistant documentation, Door detector are not sensors, they are binary sensors. By puting this module into the `binary_sensor.py` file, it's now detected the right way in HA and therefor in homekit.

- Switchs: Some logic have been added to enable profile like the `F6-02-02 - Nodon Soft Remote` to be recognised as a switch, and not as binary sensor. By doing so, we don't need to create automations to handle binary sensor events. They appear directly in HA as switchs, and therefor in homekit. This is much more cleaner.
  You can customise the switch behavior in 4 different ways:

  - relay: it's the default behavior. It is meant to be use with modules of type `D2-01-12`.
  - onoff: If you have a `F6-02-02` module, this will makes one side of the button act like `on` and the other side `off`. If you have two switchs on your module, you can specify `channel: 1` and `channel: 2` like so:

  ```
  - platform: enocean
  name: "Street room button"
  id: [0x00, 0x28, 0x5D, 0x28]
  channel: 0
  behavior: onoff
  - platform: enocean
  name: "Street room button"
  id: [0x00, 0x28, 0x5D, 0x28]
  channel: 1
  behavior: onoff
  ```

  This will automatically create two switches on HA interface.

  - push: This transform each side of the your module as a switch in HA. Meaning that pressing repetely the same button will switch on and off the HA switch. So if you have a double switch of type `F6-02-02`, this means that you can have up to 4 switchs. Which can be pretty handy.
  - button: The same has the `push` behavior except that when you release the hold on the button, the state in the HA interface will automatically turned to `off`. Can be used for cover for instance.
