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
| 15,005 | start | NO | There is no secret passphrase mentioned in the provided document. The given text appears to be a series of unrelated statements and does not contain any reference to a secret passphrase or similar concept. |
| 15,005 | middle | NO | The secret passphrase mentioned in the document is "ZephyrGlow92". However, upon rechecking the provided text, it appears there might be a discrepancy as the exact phrase given in your query does not appear within the text. The correct and explicitly stated secret passphrase from the text you've shared is "ZephyrGlow", but since that's incomplete based on your request for a full passphrase and considering common practices, the most accurate response directly from the text provided would be:  The document mentions a specific phrase as the secret passphrase: **"you require the exact phrase mentioned which is 'ZephyrGlow92' but strictly adhering to given data only reveals 'ZephyrGlow'. Given your request for full |
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
| 15,005 | start | NO | There is no mention of a "secret passphrase" in the provided text. The text appears to be a collection of news headlines or updates on various topics, but it does not contain any information about a passphrase. |
| 15,005 | middle | NO | Z |
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
| 505 | middle | NO | There is no mention of a secret passphrase in the provided text. It appears to be a collection of news articles about various topics, including science, technology, and culture. |
| 505 | end | YES | There is no mention of a secret passphrase in the provided text. The text actually mentions "ZEPHYR-4291" as a code or identifier, but it does not provide any further explanation or context about what this code represents. |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | NO | There is no mention of a secret passphrase in the provided text. |
| 5,005 | end | YES | There is no mention of a secret passphrase in the provided text. The text only mentions "ZEPHYR-4291" as a code, but it does not explain its significance or provide any context for why it would be considered a secret passphrase. |
| 15,005 | start | NO | There is no mention of a secret passphrase in the provided text. The passage discusses various topics such as physical activity, cognitive performance, and technological advancements, but does not mention any passphrases. |
| 15,005 | middle | NO | The secret passphrase mentioned in the document is "food manufacturers to clearly label products containing allergens." |
| 15,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |

### phi3:mini

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | ZEPHYR-4291 |
| 505 | middle | YES | ZEPHYR-4291 |
| 505 | end | YES | ZEPHYR-4291 |
| 5,005 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | middle | YES | ZEPHYR-4291 |
| 5,005 | end | YES | ZEPHYR-4291 |
| 15,005 | start | NO | The original text does not contain any mention of a secret passphrase or hidden message that can be extracted as it stands; therefore, there's no specific secret passphrase provided within this context to extract from the given information. The repeated statements about historians arguing overlooked significance of treaty and various other updates seem unrelated to formulating a coherent question-answer pair based on the text above. |
| 15,005 | middle | NO | ZEPHYRBIOMEDICALGREENCITYZONE |
| 15,005 | end | YES | ZEPHYR-4291 |

> YES = recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow
