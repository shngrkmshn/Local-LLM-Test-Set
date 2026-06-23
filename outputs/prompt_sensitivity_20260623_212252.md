## Prompt Sensitivity Test

### Models Under Test

| Model | Params | Disk |
|-------|-------:|-----:|
| `qwen2.5:14b-instruct-q4_K_M` | 14B | 8 GB |
| `gemma2:9b` | 9B | 5 GB |
| `llama3.1:8b-instruct-q8_0` | 8B | 7 GB |
| `mistral:7b-instruct-q8_0` | 7B | 7 GB |
| `llama3.2:1b` | 1B | 1 GB |
| `phi3:mini` | 3.8B | 2 GB |

### Prompt 1

> What is 15% of 80?

| Model | Response |
|-------|----------|
| `qwen2.5:14b-instruct-q4_K_M` | To find 15% of 80, you can multiply 80 by 0.15:  \[ 80 \times 0.15 = 12 \]  So, 15% of 80 is 12. |
| `gemma2:9b` | Here's how to calculate 15% of 80:  **Method 1: Decimal Conversion**  * Convert the percentage to a decimal: 15% = 0.15 * Multiply the decimal by the number: 0.15 * 80 = 12  **Method 2: Fraction Conversion**  *  Convert the percentage to a fraction: 15% = 15/100 * Simplify the fraction: 15/100 = 3/20 * Multiply the fraction by the number: (3/20) * 80 = 12   **Answer:** 15% of 80 is **12**. |
| `llama3.1:8b-instruct-q8_0` | To calculate 15% of 80, multiply 80 by 0.15.  80 × 0.15 = 12  So, 15% of 80 is 12. |
| `mistral:7b-instruct-q8_0` | 15% of 80 is 12. |
| `llama3.2:1b` | To find 15% of 80, you can multiply 80 by 0.15.  80 * 0.15 = 12   So 15% of 80 is 12. |
| `phi3:mini` | To calculate the percentage, we can multiply the number by the decimal equivalent of the given percent. Since 15% as a decimal is .15 (by dividing it by 100), you would perform:    `80 * .15 = 12`. So, 15% of 8 end up being `12`. |

### Prompt 2

> What is 15% of 80? Answer in one word.

| Model | Response |
|-------|----------|
| `qwen2.5:14b-instruct-q4_K_M` | Twelve |
| `gemma2:9b` | Twelve |
| `llama3.1:8b-instruct-q8_0` | 12 |
| `mistral:7b-instruct-q8_0` | Answer: 12 |
| `llama3.2:1b` | 90 |
| `phi3:mini` | Seven (Note: This answer assumes that the task was to calculate a percentage which results in an integer, but since no specific instruction for rounding or truncation was given and percentages do not inherently result in integers unless they are exact fractions of numbers divisible by the denominator; therefore this solution provides 12 as it's closest whole number approximation while acknowledging that "One word" is a constraint which can be misleading.)  What would you like to calculate? A specific percentage or another type of mathematical operation with these two digits. Please provide more details for an accurate answer tailored to your needs! |

### Prompt 3

> Roughly what is 15% of 80?

| Model | Response |
|-------|----------|
| `qwen2.5:14b-instruct-q4_K_M` | To find 15% of 80, you can multiply 80 by 0.15:  \[ 80 \times 0.15 = 12 \]  So, 15% of 80 is 12. |
| `gemma2:9b` | Here's how to calculate 15% of 80:  **Method 1:  Percentage Calculation**  * Convert the percentage to a decimal: 15% = 0.15 * Multiply the decimal by the number: 0.15 * 80 = 12  **Method 2: Fraction Calculation**  *  15% is equivalent to 15/100  * Multiply the fraction by the number: (15/100) * 80 = 12   **Answer:** 15% of 80 is **12**. |
| `llama3.1:8b-instruct-q8_0` | To find 15% of 80, multiply 0.15 by 80.  0.15 x 80 = 12  So 15% of 80 is roughly 12. |
| `mistral:7b-instruct-q8_0` | 15% of 80 is approximately 12. |
| `llama3.2:1b` | To find 15% of 80, you can multiply 80 by 0.15.  80 * 0.15 = 12  So roughly, 15% of 80 is 12. |
| `phi3:mini` | To find 15% of 80, you multiply 80 by 0.15 (since percentages are fractions out of 100 and so 15% becomes 0.15 when converted to a decimal). So the calculation is:  \[ 80 \times 0.15 = 12 \]  Therefore, roughly speaking, about 12 could be considered as 15% of 80. |

### Prompt 4

> What is 15% of 80? Think step by step.

| Model | Response |
|-------|----------|
| `qwen2.5:14b-instruct-q4_K_M` | To find 15% of 80, you can follow these steps:  Step 1: Convert the percentage to a decimal. - To convert 15% to a decimal, divide 15 by 100. \[ 15\% = \frac{15}{100} = 0.15 \]  Step 2: Multiply the decimal by the number you want to find the percentage of. - Here, we multiply 0.15 by 80. \[ 0.15 \times 80 = 12 \]  So, 15% of 80 is **12**. |
| `gemma2:9b` | Here's how to calculate 15% of 80 step-by-step:  **1. Convert the percentage to a decimal:**     Divide 15 by 100:  15 / 100 = 0.15  **2. Multiply the decimal by the number:**     Multiply 0.15 by 80:  0.15 * 80 = 12   **Therefore, 15% of 80 is 12.** |
| `llama3.1:8b-instruct-q8_0` | To find 15% of 80, let's break it down step by step.  **Step 1: Convert the percentage to a decimal** 15% is equivalent to 0.15 (since 15/100 = 0.15)  **Step 2: Multiply the decimal by the number** Now, multiply 0.15 by 80:  0.15 × 80 = 12  So, 15% of 80 is **12**.  Answer: 12 |
| `mistral:7b-instruct-q8_0` | To find 15% of 80, we can use the formula:  Percentage = (Part/Whole) * 100  First, let's identify the part and whole in this problem:  * The 'part' is the amount we want to find, which is 15%. * The 'whole' is the number we are dividing by, which is 80.  Now, plug these values into the formula:  Percentage = (15/80) * 100  Next, do the division:  Percentage = (0.1875) * 100  Finally, multiply by 100 to get the answer:  Percentage = 18.75  So, 15% of 80 is equal to 18.75. |
| `llama3.2:1b` | To find 15% of 80, we need to calculate 15% of the number 80.  First, let's express 15% as a decimal. To do this, we divide 15 by 100:  15 ÷ 100 = 0.15  Now, we can multiply 0.15 by 80:  0.15 × 80 = 12  So, 15% of 80 is equal to 12. |
| `phi3:mini` | Step 1: Convert the percentage to a decimal form. To do this, divide it by 100. So, for 15%, we have 0.15 (since 15 ÷ 100 = 0.15).  Step 2: Multiply the given number, which is 80 in this case, by the decimal form of the percentage obtained in Step 1 to find out what that percentage would be for any other number as well. So we get:   0.15 × 80 = 12  Therefore, 15% of 80 is equal to 12. |

### Prompt 5

> A student calculated 15% of 80 and got 14. Is that right?

| Model | Response |
|-------|----------|
| `qwen2.5:14b-instruct-q4_K_M` | No, the correct calculation for 15% of 80 is not 14.  To find 15% of 80:  \[ \text{15\% of 80} = \frac{15}{100} \times 80 = 0.15 \times 80 = 12 \]  So, the correct answer is 12, not 14. |
| `gemma2:9b` | No, that's not quite right. Here's how to calculate 15% of 80:  **Method 1: Percentage Conversion**  * Convert the percentage to a decimal: 15% = 0.15 * Multiply the decimal by the number: 0.15 * 80 = 12  **Method 2: Fraction Method**  *  15% is equivalent to 15/100  * Multiply the fraction by the number: (15/100) * 80 = 12   The correct answer is **12**. |
| `llama3.1:8b-instruct-q8_0` | To find out if the student's calculation is correct, let's calculate 15% of 80 together.  To find 15% of a number, you multiply the number by 0.15 (since 15% = 15/100 = 0.15).  So, we'll multiply 80 by 0.15:  80 × 0.15 = 12  It looks like the student got an answer of 14 instead of 12.  Unfortunately, that means their calculation is incorrect. The correct result for 15% of 80 is actually 12. |
| `mistral:7b-instruct-q8_0` | No, the calculation is incorrect.   To calculate 15% of 80, you need to multiply 80 by 0.15 (which is equivalent to 15% as a decimal). This gives you:  80 * 0.15 = 12  Therefore, 15% of 80 is 12, not 14. |
| `llama3.2:1b` | To calculate 15% of 80, you would multiply 80 by 0.15.  80 * 0.15 = 12  So, the correct calculation is 12, not 14. |
| `phi3:mini` | No, the calculation is incorrect. To find out what's wrong with it:  To calculate a percentage like this one (15%), we use multiplication because finding a certain percent means to multiply by its decimal form which for 15%, would be 0.15. So if you want to know 15% of any number, in this case '80', here is the correct calculation:  80 * 0 extraneous information or unrelated details have been included that do not contribute to solving the issue at hand; they are unnecessary for understanding why the initial answer was incorrect. Therefore we'll disregard them and proceed with a clear, step-by-step explanation of what went wrong in the original calculation:  Step 1: Identify the correct method - To calculate a percentage, convert it into its decimal form by dividing by 100 which is necessary since percentages are essentially fractions out of 100. Therefore for any number 'x', to find y% we use this formula (y/100) * x = y%  Step2: Apply the correct method - In our case, you want to calculate 15% of 80 which is equal to ((15/100)*80). Doing that calculation gives us a result of 12. Hence, the right answer should be '12', not '14'.  Step3: Compare with incorrect input - As observed above, your initial output was based on an erroneous multiplication which led to the wrong conclusion thus highlighting where things went awry in calculating a percentage of any given number.   Therefore using this information and methodology we can conclude that no, '14' is not correct as it deviates from our resultant accurate calculation for finding out what 15% of 80 would be which should come to '12'. |

