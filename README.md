# gungnir

> *Odin's spear. Always hits its target.*

Shared transport client for the [WDGoWars](https://wdgwars.pl) (wdgwars.pl)
ecosystem of feeders. Speaks the HMAC-signed `/api/upload/` envelope, handles
cooldown persistence, retries 429s, and detects the silent-drop failure mode
where the server returns `HTTP 200 ok:true` with zero on every counter.

## Used by

- **[Muninn](https://github.com/HiroAlleyCat/adsb-to-wdgwars)** — ADS-B feeder
- **[Heimdall](https://github.com/HiroAlleyCat/meshcore-to-wdgwars)** — Meshcore feeder
- **[wigle-to-wdgwars](https://github.com/HiroAlleyCat/wigle-to-wdgwars)** — WiFi/BLE feeder

## Quick start

```python
import gungnir

client = gungnir.Client(tool="my-feeder", version="1.0.0")
key = client.load_key(cli_key=None)  # falls through CLI → env → file

records = [{"icao": "A8A5DD", "lat": 42.0, "lon": -81.0, ...}]
client.send(key, aircraft=records)
```

## API surface

```python
class Client:
    def __init__(self, tool: str, version: str, *,
                 api_url: str = DEFAULT_API_URL,
                 me_url: str = ME_API_URL): ...

    def load_key(self, cli_key: str | None = None) -> str: ...
    def save_key(self, key: str) -> None: ...
    def whoami(self, key: str) -> int: ...
    def send(self, key: str, *,
             aircraft: list[dict] | None = None,
             networks: list[dict] | None = None,
             meshcore_nodes: list[dict] | None = None,
             batch_size: int = 500,
             dry_run: bool = False) -> int: ...
```

## Why "gungnir"?

Norse mythology — Odin's spear, said to always hit its mark when thrown.
Fits a delivery client whose job is reliable, signed delivery to wdgwars.pl.
Continues the lab-wide Norse naming convention (Muninn, Heimdall, Huginn,
Forseti, Bifröst).

## License

MIT
