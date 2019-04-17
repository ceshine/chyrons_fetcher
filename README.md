# chyrons_fetcher
Simple Python Script to download "Third Eye Data: TV News Archive chyrons"

## Example usage

Fetch chyrons from 2018/07/01 to 2018/08/31:

```python
import asyncio
from datetime import date

from fetch_data import main

if __name__ == "__main__":
    try:
        LOOP = asyncio.get_event_loop()
        LOOP.run_until_complete(main(date(2018, 7, 1), date(2018, 8, 31)))
    finally:
        LOOP.close()
```

Downloaded files will be in the `data/` subfolder.
