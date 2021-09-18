# bo5lock
A lightweight password wallet.

## Dependencies

To install the project dependencies with pip, you can use : 

```shell
pip3 install cryptography
pip3 install pyperclip

# we need pyqt6 (5 untested) for gui
pip3 install PyQt6
```

Preferably in a virtual python environment.

## How to use :


```shell
python bo5lock.py  # launch gui
# make sure you have the proper dependencies installed
```

You get to choose a wallet \*.wlt and ticket \*.tik files in which to store your goodies and randomly generated passphrase.
If the files don't exist, they will be created at the first *create* operation running

Store your ticket and wallet in a safe place.
