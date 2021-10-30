import sys


def get_subdomains(domain):
    stdout = sys.stdout
    try:
        # We don't want any output to stdout, redirect to stderr
        sys.stdout = sys.stderr

        import sublist3r

        return sublist3r.main(
            domain,
            80,
            None,
            ports=None,
            silent=False,
            verbose=False,
            enable_bruteforce=False,
            engines=None,
        )
    finally:
        sys.stdout = stdout
