# naver-vaccine-alert

This is an old script that I made back in 2021 in order to get vaccinated against COVID-19, back when we had a vaccine shortage.

The vaccine part is no longer relevant, but the script is my first attempt at GraphQL querying and I'm pretty pleased with how well it worked, so I'm open-sourcing it in the hopes that it helps someone else in the future.

---

Uses Naver's API to fetch leftover vaccine reservation list

# Config

Create a `config.ini` file in the same directory as the Python script:

```ini
[DEFAULT]
pushover-notifications = true       # Pushover notifications
time-delay = 3                      # Time delay between runs

[pushover]                          # Only required if pushover-notifications is enabled
api-token = abcdefg...
user-key = hijklmnop...
```

# Usage

1. Fetch the request body of the area you want to search through.
You can do this by using your browser's built-in DevTools, and
looking for network requests.

2. Save the request body to a file called `request.json`. A sample
request file is provided in `sample_request.json` file.

3. Run the script.

4. If a vaccination spot opens up, the script will alert you,
and print details of the vaccination spot on the terminal.

5. Each run is saved to a `response.json` file if you wish to do
further processing. Note that this file is overwritten on each
run, so consider copying the file if you want to analyze an
individual run.
