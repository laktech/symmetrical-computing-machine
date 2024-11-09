# Log File Reader

## Introduction

This is a simple Python program designed to return the contents of a log file from `/var/log` with newest lines first. It has the ability to perform basic keyword filtering and limiting the number of lines returned. The program runs as a HTTP REST service on port 8080.

## How to Invoke the Program

### Prerequisites
- Python 3.11.10 or later.
- Shell tools, `tail -r` suppor tor `tac`, `grep`, and `head` available in the system's PATH.
- Bash found at /bin/bash
- Tested on Ubuntu and FreeBSD

### Installation
1. Clone this repository:
   ```bash
      git clone https://github.com/laktech/symmetrical-computing-machine.git
      cd symmetrical-computing-machine
	  python server.py
   ```

## Endpoint

### `GET /tail`
Returns the lines requested from the given file within the `/var/log` base directory.

#### **Request:**

```http
GET /tail?file=messages&keyword=md&limit=10
```

| Parameter | Type    | Required | Description                            |
|-----------|---------|----------|----------------------------------------|
| `file`    | string  | Yes      | The name of the file                   |
| `keyword` | string  | No       | Selects lines that match keyword       |
| `limit`   | numeric | No       | Returns at most`limit` number of lines |

#### **Example Request:**

(Output lines truncated for readability)

```bash
$ curl "localhost:8080/tail?file=apache.log.sample&limit=3&keyword=Mozilla"
5.10.83.53 - - [20/May/2015:19:05:02 +0000] "GET /files/blogposts/20080310/?C=D;O=A HTTP/1.1" 200 980 "-" "Mozilla/5.0   ..."
82.130.48.164 - - [20/May/2015:19:05:10 +0000] "GET /favicon.ico HTTP/1.1" 200 3638 "-" "Mozilla/5.0 (X11; Linux x86_64) ..."
82.130.48.164 - - [20/May/2015:19:05:52 +0000] "GET /banner.png HTTP/1.1" 200 52315 "-" "Mozilla/5.0 (X11; Linux x86_64) ..."
```

The endpoint returns HTTP response code 200 on success and 500 on failure.

## Design Goals

Unix command line tools were constructed to solve the log tailing problem at a local level. The unix command was then wrapped around a basic python http server to expose the command as a simple HTTP REST service.

The program ensures that:

- only the "/tail" endpoint is supported
- file query parameter is required
- attempt is made to prevent command injection by using ANSI-C Quoting in bash
- supports decent error reporting due to leveraging unix tools
- supports unicode, utf-8 encoding

The following are limitations:

- truncation is problematic
- no security
- performance may be an issue, e.g. if lots of users access the endpoint
- output is text with http status code for error reporting instead of JSON
- large files are problematic as the entire file is read into memory

On Linux, "tac" command is used. On Unix "tail -r" to read lines in reverse.

## Testing

The following test cases were executed:

- Ensure any other path returns 404, e.g. curl "localhost:8080" or curl "localhost:8080/foobar"
- Ensure `file` is required
- Ensure `keyword` and `limit` are optional
- Ensure `keyword` behavior works with and without `limit`
- Ensure `limit` behavior works
- Ensure correct behavior if `keyword` does not match, with and without `limit`
- Ensure error if `file` does not exist
- Test with 1gb file and ensure decent performance
- Ensure non-positive `limit` values return an error
- Ensure failure attempting to read file without proper permissions



