# SSDX Helper

This repo contains SSDX Helper. Its goal is to make the life of Salesforce Developers and Administrators easier. It's an CLI extension of SFDX, created in Python, to more quickly execute SFDX commands used more often.

|     Main Menu      |   Org Commands    |
| :----------------: | :---------------: |
| ![](/img/main.png) | ![](/img/org.png) |

[Hyper](https://hyper.is) is a recommended terminal, as seen above

## Installation

### macOS / Linux

```bash
# prerequisites
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)" # Homebrew is recommended for installing git and python quickly
brew install git
brew install python@3.9
pip3 install virtualenv

# ssdx installation
cd [path_to_dx_project]
bash <(curl -s https://raw.githubusercontent.com/navikt/ssdx/master/scripts/install.sh)
```

## Windows

#### Prerequisites

* [git](https://git-scm.com/download/win)
* [python3](https://www.python.org/ftp/python/3.8.0/python-3.8.0.exe)
  * **Important!** Install with 'ADD PYTHON 3.8 TO PATH' checked
  * Checkbox appears on first windows screen when installing
  * If checkbox is not checked, uninstall Python and re-install
* [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
  * Right-click on get-pip.py and save the file somewhere on your computer
  * Run ```python get-pip.py``` from your terminal of choice
  * Make sure to cd into the directory you saved get-pip.py (or drag the file into the terminal to get the full path)

#### SSDX Installation

1. Right-click on
[install.cmd](https://raw.githubusercontent.com/navikt/ssdx/master/scripts/install.cmd) and click "Save Link As" (or equivalent)
2. Save to root of SFDX project folder as "install.cmd"
3. Double click install.cmd

### .gitignore

```text
**/.ssdx/
run.command
run.cmd
install.cmd
**/dummy-data/*.out/*
```

## Configuration

Add the following config template to ```./config/ssdx-config.json```:

``` json
{
  "locations": {
		"dummy-data": "[folder_location]",
		"users": "[folder_location]",
		"manifest": "[folder_location]",
		"unpackagable": "[folder_location]",
		"package-key": "[file_location]"
  },
  "permsets_to_assign": [],
  "managed_packages": []
}
```

Example [ssdx-config.json](https://github.com/navikt/crm-arbeidsgiver-base/blob/master/config/ssdx-config.json).

### Locations (optional)

* ```dummy-data```: folder location for dummy-data ([example](https://github.com/navikt/crm-arbeidsgiver-base/tree/master/dummy-data), [documentation](https://github.com/navikt/crm-arbeidsgiver-base/tree/master/dummy-data))

* ```user```: folder location for config files to generate users ([example](https://github.com/navikt/crm-arbeidsgiver-base/tree/master/config/users), [documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_users_def_file.htm))

* ```manifest```: folder location for config files to retrieve metadata using manifests ([example](https://github.com/navikt/crm-arbeidsgiver-base/tree/master/config/manifest), [documentation](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/manifest_samples.htm))

* ```unpackagable```: metadata needed for scratch orgs, but cannot be in packages ([example](https://github.com/navikt/crm-arbeidsgiver-base/tree/master/config/unpackagable), [documentation](https://developer.salesforce.com/docs/metadata-coverage))

* ```package-key```: file location where to save package key (key needed when creating and installing packages) ([documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_dev2gp_config_installkey.htm))

### Permsets to assign (optional)

When creating a new scratch org using SSDX, permission sets can automatically be assigned to the current users. NOTE! These permissions will also be taken into account when running tests. Only add the API names for the permsets, do not include a path.


## Commands

### Organization Commands

The following organization funcionality exists:

* Create Scratch Org
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

### User Commands

* Create User
	* Will automatically create a new user in an org and print the password

### Other Commands

* Create Package Key
	* If any dependant package requires a password, add the password here to quickly install it (remember to gitignore the file)
	* The file is saved where you configure it to (see config-section)

## Demo

### Creating Scratch Org

The most useful command, which automates many tasks, such as:

![Screenshot](/img/createScratchOrg.gif)

### Status of Scratch Org

You can also get status information of your current scratch org. This is useful to see how many days are left in your scratch org.

![Screenshot](/img/status.png)
