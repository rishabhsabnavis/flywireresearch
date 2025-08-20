# FlyWire Connectome Analysis Python Project

This project provides authenticated access to the Drosophila connectome via the FlyWire project's CAVEclient Python API. It demonstrates how to connect, authenticate, and run example neuron queries using a FlyWire datastack.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Overview

Leverage the Princeton FlyWire project's official CAVEclient API to programmatically access and analyze the fruit fly brain connectome. Ideal for neuroscience researchers and students.

---

## Features

- Secure authentication with FlyWire API token
- Query neuron root info by root_id
- Discover available datastacks dynamically
- Easily extensible for additional connectomic analysis

---

## Installation

1. **Install Anaconda (recommended)**
   - [anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)

2. **Create a conda environment and activate it:**
conda create -n flywire-env python=3.10
conda activate flywire-env

text

3. **Install required packages:**
pip install caveclient

text
(Optional: `pip install fafbseg` for advanced segmentation queries.)

---

## Setup

1. **Obtain your FlyWire API token:**
- Log in at [flywire.ai](https://flywire.ai)
- Go to your user profile/account and copy your API token.

2. **Set your token for authentication via environment variable—either:**
- **Before running Python:**  
  Windows (Anaconda Prompt):
  ```
  set CAVE_TOKEN=your_token_here
  python main.py
  ```
  macOS/Linux:
  ```
  export CAVE_TOKEN=your_token_here
  python main.py
  ```
- **Or place this at the very top of your `main.py`:**
  ```
  import os
  os.environ['CAVE_TOKEN'] = 'your_token_here'
  ```

---

## Usage

Discover available datastacks and query neuron info:

import os
os.environ['CAVE_TOKEN'] = 'your_token_here'

from caveclient import CAVEclient

First, list datastacks:
client = CAVEclient(server_address="https://global.daf-apis.com")
print(client.info.get_datastack_names()) # Use the correct datastack returned

Then connect using the correct datastack, for example:
client = CAVEclient("production_flywire") # Change as needed

root_id = "720575940626979621" # Example
root_info = client.chunkedgraph.get_root_id(root_id)
print("Root Info:", root_info)

text

---

## Troubleshooting

- **AuthException:**  
  Ensure your `CAVE_TOKEN` is set *before* importing or initializing `CAVEclient`. Double-check token correctness and that it has not expired.
- **GlobalClientError:**  
  You must initialize with a valid datastack name, not just a server address.
- **HTTPError: invalid_table_id:**  
  Use `client.info.get_datastack_names()` to discover the active datastack names.
- **SSL/Connection errors:**  
  Always work inside an Anaconda environment, not system Python.

---

## Technologies

- Python 3.8–3.12  
- Anaconda  
- [CAVEclient](https://pypi.org/project/caveclient/)

---

## Contributing

Pull requests are welcome! Please fork this repository and open a PR with your improvements.

---

## Contact

Rishabh Sabnavis  
[github.com/rishabhsabnavis]  
For more on FlyWire: [https://flywire.ai](https://flywire.ai)