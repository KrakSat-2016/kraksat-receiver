# kraksat-receiver

## Requirements

* Python 3.5
* Qt 5.4
* PyQt

## Building

Before first run or after making changes in files inside `app/ui/` directory,
`make` needs to be executed to build UI files. Make sure you have GNU Make
installed as well as `pyuic5` and `pyrcc5` PyQt utilities in order to do that.

## Running

```
./main.py
```

## Unit Testing

Running unit tests:

```
python -m unittest
```

## 3rd Party Assets

kraksat-receiver uses [Google Material Icons](https://design.google.com/icons/)
licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
placed in the `app/ui/res/` directory.
