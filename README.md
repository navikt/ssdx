# SSDX Helper

This repo contains SSDX Helper. Its goal is to make the life of Salesforce Developers and Administrators easier. It's an CLI extension of SFDX, created in Python, to more quickly execute SFDX commands used more often.

|     Main Menu      |   Org Commands    |
| :----------------: | :---------------: |
| ![](/img/main.png) | ![](/img/org.png) |

[Hyper](https://hyper.is) is a recommended terminal, as seen above

## Installation

### macOS / Linux prerequisites

```bash
# install Homebrew (recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install git
brew install python3
pip3 install virtualenv
```

### macOS / Linux install command

```bash
cd [path_to_dx_project]
bash <(curl -s https://raw.githubusercontent.com/navikt/ssdx/master/scripts/install.sh)
```

### Windows prerequisites

* [git](https://git-scm.com/download/win)
* [python3](https://www.python.org/ftp/python/3.8.0/python-3.8.0.exe)
  * **Important!** Install with 'ADD PYTHON 3.8 TO PATH' checked
* [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
  * ```python get-pip.py```

### Windows install file

1. Download 
[install.cmd](https://raw.githubusercontent.com/navikt/ssdx/master/scripts/install.cmd) (Ctrl+S into your DX project root, without .txt)
2. Double click file

### .gitignore

```text
**/.ssdx/
run.command
run.cmd
install.cmd
**/dummy-data/*.out/*
```

## Commands

### Organization Commands

The following organization funcionality exists:

* Crete Scratch Org
* Open Scratch Org
* Status of Scratch Org
* Change Scratch Org
* Delete Scratch Org
* Change default org
* Login to org

### Source Commands

The following source (metadata) funcionality exists:

* Pulling metadata from a Salesforce Scratch Org
* Pushing metadata from a Salesforce Scratch Org
* Pulling metadata from a Manifest

## Demo

### Creating Scratch Org

The most useful command, which automates many tasks, such as:

![Screenshot](/img/createScratchOrg.gif)

### Status of Scratch Org

You can also get status information of your current scratch org. This is useful to see how many days are left in your scratch org.

![Screenshot](/img/status.png)
