# SSDX Helper

This repo contains Sopra Steria DX Helper (SSDX Helper). Its goal is to make the life of Salesforce Developers and Administrators easier. It's an CLI extension of SFDX, created in Python, to more quickly execute SFDX commands used more often.

![Screenshot](/img/terminal.png)

## Installation

macOS / Linux:

```bash
cd [path_to_dx_project]
bash <(curl -s https://raw.githubusercontent.com/navikt/ssdx/master/install.sh)
```

Windows:

1. Download 
[install.cmd](https://raw.githubusercontent.com/navikt/ssdx/master/install.cmd)
2. Open from root of DX project


## Organization Commands

The following organization funcionality exists:

- Crete Scratch Org
- Open Scratch Org
- Status of Scratch Org
- Change Scratch Org
- Delete Scratch Org
- Change default org
- Deploy to org
- Login to org

## Source Commands

The following source (metadata) funcionality exists:

- Pulling metadata from a Salesforce Scratch Org
- Pushing metadata from a Salesforce Scratch Org
- Pulling metadata from a Manifest

## Creating Scratch Org

The most useful command, which automates many tasks, such as:

![Screenshot](/img/createScratchOrg.gif)

## Status of Scratch Org

You can also get status information of your current scratch org. This is useful to see how many days are left in your scratch org.

![Screenshot](/img/status.png)
