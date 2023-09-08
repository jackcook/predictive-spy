# Predictive Spy 🕵️

Code accompanying my blogpost, “A look at Apple’s new Transformer-powered predictive text model.”
With this repository, you can snoop on activity from the new predictive text model in macOS Sonoma.

**Note:** At some point this summer, Apple removed the ability to spy on model predictions at some point, but I’m not sure which beta they did this in.
I can confirm it works in macOS Sonoma beta 1, but not in beta 7.

![Demo snooping on predictive text model predictions](/assets/output.gif)

## Introduction

This repository has two scripts:

- **get_tokens.py**: Generates a vocabulary file from the predictive text model
- **spy.py**: Spies on predictive text model activity

Both scripts only work on macOS Sonoma (14), neither will work on macOS Ventura (13) or earlier.
If you’re just interested in getting the vocabulary file, you don’t need to follow any of the setup instructions.

## Spying Setup

**Note:** I tested these instructions most recently on a virtual machine in Parallels, but these instructions should also work on a real machine.
If you need to install a VM, I found a link to a macOS Sonoma beta 1 IPSW [here](https://ipswbeta.dev/macos/14.x/).

### Disable SIP

Follow [this guide](https://developer.apple.com/documentation/security/disabling_and_enabling_system_integrity_protection) to disable system integrity protection.
You’ll need to boot into recovery mode, run a command, and then reboot.
If you’re doing this on a real machine, don’t forget to re-enable SIP once you’re done :-)

### Install Command Line Tools

Usually, you should be able to install command line tools with the following command:

```bash
xcode-select --install
```

However, I had trouble doing this in my VM, so I downloaded the most recent Command Line Tools package from the Apple Developer website.

### Install fq

To install [`fq`](https://github.com/wader/fq), you can follow the instructions in their README, or use these commands:

```bash
# Install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add brew to path
(echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> /Users/jackcook/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install fq
brew install wader/tap/fq
```

### Install dependencies

```bash
pip3 install -r requirements.txt
```

## Usage

Once everything is set up, you should be able to run it with sudo:

```bash
sudo python3 app.py
```

You may see the following error:

```
Failed to spawn: unable to find a process with name 'AppleSpell'
```

This is because AppleSpell needs to be running when you start the command.
In order to ensure this is the case, open the Notes app (or any other app with a text field) and start typing, then try starting the script again.

## License

`predictive-spy` is available under the MIT license. See the [LICENSE](LICENSE.md) file for more details.
