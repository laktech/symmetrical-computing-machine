# Log File Reader

## Introduction

This is a simple Python program designed to return the contents of a log file from `/var/log` with newest lines first. It has the ability to perform basic keyword filtering and limiting the number of lines returned to the user. The program runs as a HTTP REST service on port 8080.

## How to Invoke the Program

### Prerequisites
- Python 3.7 or later.
- Shell tools, `tail`, `grep`, and `head` available in the system's PATH.
- Bash

### Installation
1. Clone this repository:
   ```bash
      git clone https://github.com/laktech/symmetrical-computing-machine.git
      cd log-file-reader
   ```
		 
