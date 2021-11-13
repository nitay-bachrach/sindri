# Sindri

## Installtion
1. Install [amass](https://github.com/OWASP/Amass). If you use Kali Linux, Parrot OS or Blackarch, you probably have it already. If you use Arch (BTW), you can find it in the [AUR](https://aur.archlinux.org/packages/amass/). You can also install it using snap.

2. Alternatively, you can also install [sublist3r](https://github.com/aboul3la/Sublist3r). If you use Kali Linux, Parrot OS or Blackarch, you probably have it already. If you use Arch, you can find it in the [AUR](https://aur.archlinux.org/packages/sublist3r-git/).

3. Use pip to install sindri. Navigate to the repo and then execute the following command:
````shell
python -m pip install -e ./
````
If you installed `sublist3r` in a virtual environment and wish to use it, make sure to install sindri in the same environment

## Usage
The basic usage is very simple:
```shell
sindri example.com
```

You can provide flags such as `-n` to choose name servers, `-j` to tell sindri to print the output as JSON, and `--so` if you want to save the scanned subdomains in a file (so you won't have to scan the site twice).