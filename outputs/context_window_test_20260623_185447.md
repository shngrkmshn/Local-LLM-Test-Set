## Lost-in-the-Middle: Context Window Test

**Needle:** `The secret passphrase is ZEPHYR-4291.`  
**Question:** What is the secret passphrase mentioned in the document?

### Models Under Test

| Model | Params | Disk |
|-------|-------:|-----:|
| `qwen2.5:14b-instruct-q4_K_M` | 14B | 8 GB |
| `gemma2:9b` | 9B | 5 GB |
| `llama3.1:8b-instruct-q8_0` | 8B | 7 GB |
| `mistral:7b-instruct-q8_0` | 7B | 7 GB |
| `llama3.2:1b` | 1B | 1 GB |
| `phi3:mini` | 3.8B | 2 GB |


### qwen2.5:14b-instruct-q4_K_M

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |

### gemma2:9b

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 15,005 | start | NO | There |
| 15,005 | middle | NO | There |
| 15,005 | end | NO | The |

### llama3.1:8b-instruct-q8_0

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | middle | YES | ZEPHYR-4291. |
| 5,005 | end | YES | ZEPHYR-4291 |
| 15,005 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 15,005 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 15,005 | end | YES | ZEPHYR-4291 |

### mistral:7b-instruct-q8_0

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | start | NO |  |
| 15,005 | middle | NO |  |
| 15,005 | end | NO |  |

### llama3.2:1b

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | end | YES | There is no mention of a secret passphrase in the provided text. The text actually mentions "ZEPHYR-4291" as a code or identifier, but it does not provide any further explanation or context about what this code represents. |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | NO | There is no mention of a secret passphrase in the provided text. |
| 5,005 | end | NO | There is no mention of a secret passphrase in the provided text. The text only discusses various topics such as:  * Migratory birds and their use of magnetic fields to navigate * Cloud computing and its impact on companies storing and processing large datasets * Renewable energy investments and their record high for the third consecutive year * The novel explores themes of identity and belonging through the eyes of three generations * Traffic congestion in major metropolitan areas continues to worsen despite infrastructure spending * A new study links regular physical activity to improved cognitive performance in older adults * The museum acquired a rare collection of medieval manuscripts from a private estate * Farmers in the region are adopting precision agriculture techniques to reduce water usage * Astronomers detected unusual radio signals originating |
| 15,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | middle | NO | There is no mention of a secret passphrase in the provided text. The text only discusses various topics such as migratory birds, magnetic fields, renewable energy, and technology advancements, but does not mention any secret passphrases. |
| 15,005 | end | NO | There is no mention of a secret passphrase in the provided text. The conversation appears to be about various topics, including:  * Renewable energy investments reaching a record high for the third consecutive year * Traffic congestion in major metropolitan areas continuing to worsen despite infrastructure spending * A new study linking regular physical activity to improved cognitive performance in older adults * The museum acquiring a rare collection of medieval manuscripts from a private estate * Farmers adopting precision agriculture techniques to reduce water usage * Economists debating whether inflation is primarily driven by supply chain disruptions or monetary policy  There is no mention of a secret passphrase. |

### phi3:mini

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | ZEPHYR-4291 |
| 505 | middle | YES | ZEPHYR-4291 |
| 505 | end | YES | ZEPHYR-4291 |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | YES | ZEPHYR-4291 |
| 5,005 | end | YES | ZEPHYR-4291 |
| 15,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | middle | YES | ZEPHYR-4291 |
| 15,005 | end | YES | ZEPHYR-4291 |

> YES = recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow
