# Installing a Newer Version of Bash on macOS&reg;*

To use the `build.sh` and `run.sh` on MacOS you must ensure your `bash` is running on the latest version (macOS&reg;* comes with `bash` dating back to 2006). Use a package manager like [`brew`](https://brew.sh) to install it:

```
brew install bash                       # Installs latest version of bash.
/usr/local/bin/bash ./docker/build.sh   # Builds Docker container with newly installed bash.
```

---
\* Other names and brands may be claimed as the property of others.
