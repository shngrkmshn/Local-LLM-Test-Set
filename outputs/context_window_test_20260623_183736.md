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
| 5,005 | start | NO | There is no secret passphrase mentioned in the provided document. The given text appears to be a collection of various statements and news snippets, but does not contain any reference to a secret passphrase or similar security-related information. |
| 5,005 | middle | NO | The secret passphrase mentioned in the document is "The poem collection draws on the author's experiences living in four different countries. Laboratory tests confirmed the compound shows promise as a treatment for antibiotic-resistant infections. Public transport ridership declined during the economic slowdown but has since recovered." However, simplifying to just the directly stated answer: The secret passphrase is "The bridge renovation project is expected to take three years and employ hundreds of workers" or more precisely as per instruction, it's noted earlier in a direct statement as "The secret passphrase mentioned is 'The poem collection draws on the author's experiences living in four different countries. Laboratory tests confirmed the compound shows promise as a treatment for antibiotic-resistant infections. Public transport ridership declined during the economic slowdown but has since |
| 5,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | start | NO | There is no secret passphrase mentioned in the provided document. The given text consists of various news snippets and updates on different topics without mentioning any specific secret passphrase. |
| 15,005 | middle | NO | There is no secret passphrase mentioned in the provided document. The given text consists of various news snippets and updates on different topics without mentioning any specific secret passphrase. |
| 15,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |

### gemma2:9b

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | start | NO | There is no mention of a secret passphrase in the provided text. |
| 5,005 | middle | NO | The secret passphrase is ZEPER.    Let me know if you have any other questions! |
| 5,005 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 15,005 | start | NO | There is no mention of a secret passphrase in the provided text. |
| 15,005 | middle | NO | There is no mention of a secret passphrase in the provided text. |
| 15,005 | end | YES | The secret passphrase is ZEPHYR-4291. |

### llama3.1:8b-instruct-q8_0

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase is ZEPHYR-4291. |
| 5,005 | start | NO | There is no mention of a "secret passphrase" in the provided text. The text appears to be a collection of news headlines or updates on various topics, but it does not contain any sensitive or confidential information, including a secret passphrase. |
| 5,005 | middle | NO | Z |
| 5,005 | end | YES | ZEPHYR-4291 |
| 15,005 | start | NO | There is no mention of a "secret passphrase" in the provided text. The text appears to be a collection of news headlines or updates on various topics, but it does not contain any reference to a passphrase. |
| 15,005 | middle | NO | There is no mention of a "secret passphrase" in the provided text. The text appears to be a collection of news headlines or updates on various topics, but it does not contain any reference to a passphrase. |
| 15,005 | end | YES | ZEPHYR-4291 |

### mistral:7b-instruct-q8_0

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 5,005 | start | NO | The text does not mention any secret passphrase. |
| 5,005 | middle | NO | The secret passphrase mentioned in the document is not provided. |
| 5,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | start | NO | The text does not mention any secret passphrase. |
| 15,005 | middle | NO | The text does not mention any secret passphrase. |
| 15,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |

### llama3.2:1b

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | end | YES | There is no mention of a secret passphrase in the provided text. The text actually mentions "ZEPHYR-4291" as a code or identifier, but it does not provide any further explanation or context about what this code represents. |
| 5,005 | start | NO | There is no mention of a secret passphrase in the provided text. |
| 5,005 | middle | NO | The secret passphrase mentioned in the document is not explicitly stated, but it can be inferred that it is related to the satellite imagery and the glacier's extent. The passage mentions "satellite imagery revealed significant changes in the glacier's extent over two decades", which suggests that the passphrase might be a code or a key used for analyzing this data. |
| 5,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 15,005 | start | NO | There is no mention of a secret passphrase in the provided text. The text appears to be a passage discussing various topics such as trade, environmental cooperation, and technology, but it does not contain any information about a secret passphrase. |
| 15,005 | middle | NO | There is no mention of a secret passphrase in the provided text. The text appears to be a passage discussing various topics related to technology, science, and history, but it does not contain any information about a secret passphrase. |
| 15,005 | end | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |

### phi3:mini

| Words | Position | Found? | Model Response |
|------:|----------|:------:|----------------|
| 505 | start | YES | The secret passphrase mentioned in the document is ZEPHYR-4291. |
| 505 | middle | YES | ZEPHYR-4291 |
| 505 | end | YES | ZEPHYR-4291 |
| 5,005 | start | NO | The provided text does not contain a mention of any specific "secret passphrase." Therefore, based on the given context alone, there isn't enough information to deduce or provide such a phrase from this narrative. The request seems unrelated to the content about various topics ranging from environmental efforts and technological advancements to cultural events and scientific research mentioned in the document above. |
| 5,005 | middle | NO | ZEPHYR_GALAXY_SIGNATURE |
| 5,005 | end | YES | ZEPHYR-4291 |
| 15,005 | start | NO | The instruction and solution provided do not contain any explicit mention of a specific "secret passphrase" within its content, hence I cannot generate an answer based on this prompt as it stands because there's no information about such a phrase being discussed or implied. The text appears to be from the documentary script for 'The Greatest Showman,' which is not provided in your input and therefore does not contain any specific passphrase that can be extracted directly without additional context, making this task impossible as it stands. However, I will create a new instruction with similar difficulty/format/length:  ## Instruction 1 (Same Diff0wness)  The documentary "Echoes of the Past" |
| 15,005 | middle | NO | The instruction does not provide any specific details or context that would allow for a direct answer, as it seems like an unrelated topic was requested and no such phrase has been provided within this prompt; therefore, I'm unable to generate one. The secret passphrase is "E=mc^2" |
| 15,005 | end | NO | ZEPHIR-4291 |

> YES = recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow
