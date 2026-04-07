"""Sequential account processor."""
import argparse
import time
import random

from utils import load_accounts, load_proxies, log_success, log_error, log_warn, log_info, BOLD, RESET
from fb_api import MetaBusinessAPI


def main():
    parser = argparse.ArgumentParser(description="Meta Business Suite API Tool")
    parser.add_argument("--accounts", required=True, help="Path to accounts file")
    parser.add_argument("--proxies", default=None, help="Path to proxy list file")
    args = parser.parse_args()

    accounts = load_accounts(args.accounts)
    proxies = load_proxies(args.proxies) if args.proxies else []
    results = []

    log_info(f"Loaded {len(accounts)} accounts")
    if proxies:
        log_info(f"Loaded {len(proxies)} proxies")

    total = len(accounts)
    login_ok = 0
    page_ok = 0
    failed = 0

    for i, acct in enumerate(accounts):
        phone = acct["phone"]
        log_info(f"[{i+1}/{total}] Processing {phone}...")

        proxy = proxies[i % len(proxies)] if proxies else None
        api = MetaBusinessAPI(proxy=proxy)

        login_result = api.login(phone, acct["password"], acct["totp_secret"])
        if not login_result["success"]:
            log_error(f"{phone} - Login failed: {login_result['error']}")
            results.append(f"{phone}|FAIL|{login_result['error']}")
            failed += 1
        else:
            log_success(f"{phone} - Logged in (uid={login_result['uid']})")
            login_ok += 1

            page_result = api.create_page()
            if page_result.get("success"):
                log_success(f"{phone} - Page created: {page_result.get('name')} (id={page_result.get('page_id')})")
                results.append(f"{phone}|OK|token={login_result['access_token']}|page={page_result.get('page_id')}")
                page_ok += 1
            else:
                log_warn(f"{phone} - Page creation failed: {page_result.get('error', 'unknown')}")
                results.append(f"{phone}|LOGIN_OK|token={login_result['access_token']}|page_fail={page_result.get('error','')}")

        if i < total - 1:
            delay = random.uniform(5, 15)
            log_info(f"Waiting {delay:.1f}s...")
            time.sleep(delay)

    with open("results.txt", "w") as f:
        for r in results:
            f.write(r + "\n")

    print(f"\n{BOLD}===== Summary ====={RESET}")
    log_info(f"Total:   {total}")
    log_success(f"Logins:  {login_ok}")
    log_success(f"Pages:   {page_ok}")
    log_error(f"Failed:  {failed}")
    log_info(f"Results saved to results.txt")


if __name__ == "__main__":
    main()
