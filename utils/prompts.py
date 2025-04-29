"""
Prompt Templates

This module contains prompt templates used across the application.
"""


# Story generation prompt template used for OpenAI vision model

# Characteristic from gpt-4.1 =========================================================================================================

CLAIM_CRITERIAS = """
1.	Repeated Break Locations
  o	Bottles frequently broke at structurally weak areas, specifically the neck/shoulder or the base/bottom.
2.	Jagged, Sharp Edges
  o	All broken sections have irregular, sharp, and dangerous edges, posing significant handling risks.
3.	Fragmentation and Cracking
  o	Multiple examples of extensive crack lines, often radiating from the main break point, with some bottles experiencing catastrophic shattering into many pieces.
  o	Large and medium shards are common, often accompanied by numerous small fragments.
4.	Detached Neck and Cap
  o	In cases of neck/shoulder fracture, the neck segment (usually with the cap still sealed) is separated cleanly from the main body and often placed beside it.
5.	Base Separation is considered as claim
  o	Several bottles display a relatively clean separation of the base/bottom, often forming a “cap” of glass left aside.
6.	Visible Internal Cracks
  o	Many bottles show pronounced internal cracks, sometimes running through the label area or the full length of the body, indicating propagation of stress.
7.	Unopened/Sealed State at Time of Breakage
  o	The majority of bottles have their caps still sealed on the broken neck, confirming they were not opened by hand but rather broke while sealed/full.
8.	Main Body Integrity
  o	Even when the top or base is missing, the remaining main body often stays upright but is structurally compromised.
9.	Label Condition
  o	Main labels are typically intact, though in shattering events, parts of the label may be torn or fragmented with the glass.
10.	Evidence of Spillage
  o	Several images document liquid leakage or stains in trays, especially for bottles that appear to have broken under pressure or while filled.
11.	Multiple Shards and Shard Sizes
  o	Both large breakaway pieces and many small, invisible fragments or splinters are present, increasing cleanup hazard.
12.	Foreign material appearance
  o	Occasionally, foreign debris or packaging material remains attached to the fractured bottle sections, suggesting potential contamination.
13.	Broken While Full/Pressurized
  o	Spillage and residue are consistent with breakage occurring while bottles were full or pressurized during the incident.
14.	High-Risk Cleanup and Handling
  o	The sharpness and number of fragments create major safety risks for anyone handling the broken bottles, requiring proper PPE.
15.	Root Cause Implications
  o	The similarity and location patterns of breakage suggest issues possibly related to bottle manufacturing, glass quality, handling/transport shock, or stress/pressure during processing or filling.
"""

UNCLAIM_CRITERIAS = """
1.	Breakage Consistently at Neck/Shoulder
  o	Nearly all bottles show primary breakage around the neck or shoulder area, resulting in the complete loss or severe fragmentation of the neck and upper portion.
2.	Jagged and Dangerous Edges
  o	The broken edges are consistently jagged, sharp, and irregular, presenting a serious risk of cuts and injuries.
3.	Detached Neck and Sealed Cap
  o	Detached necks, typically with the cap still sealed, are found inside or lying next to the bottle body, indicating breakage happened before opening.
4.	Variable Fragmentation
  o	Some bottles are broken into only a few large pieces, but several involve catastrophic fragmentation into many large and small shards (including label fragments).
5.	Extensive Crack Propagation
  o	Internal and external cracks radiate in multiple directions from the main break points, with spiderweb, linear, and branching patterns observed.
6.	Secondary Damage and Spillage
  o	Evidence of liquid residue or spillage is common, suggesting many bottles were broken while filled.
7.	Labels Generally Intact but Sometimes Torn
  o	The main bottle label is usually intact on the main body, but may be torn, found among fragments, or missing in cases of severe breakage.
8.	Visible Glass Residue or Internal Particulate
  o	Green glass particulate and residue are sometimes visible in the bottle body, increasing contamination and cleanup difficulty.
9.	Hazardous Shard Distribution
  o	Both small and large fragments are present, sometimes scattered around the tray, increasing the chance of missing smaller pieces during cleanup.
10.	Pointed Shard Protrusions
  o	Many broken bottles feature tall, pointed shards protruding from the rim of the remaining body, greatly increasing the risk of injury.
11.	Structural Instability
  o	Even when standing, all remaining bottle bodies are severely compromised by cracks and missing sections, making them unstable and unsafe for any use.
12.	Foreign Material Presence
  o	Occasional attachment of foreign objects such as packaging debris is noted on broken bottles, increasing contamination risk.
13.	Consistency in Pattern
  o	The nature and pattern of breakage (location, crack type, fragmentation, etc.) is consistent across different bottles, suggesting a recurring problem (handling, process, or material flaw).
"""


<<<<<<< utils/prompts.py
NEW_PROMPT = f"""
You will receive an image or multiple images of one bottle or a video of a broken bottle.
Your task is to classify claim or unclaim based on the provided images or video.
The answer must clearly specify whether the bottle can claim or unclaim,

# Steps
1. **Detect brand of bottle:**
   - Check whether what brand is this bottle.
   - if it's "Chang" or "ช้าง" need to be considered in the next step.
   - if it is not "Chang" or "ช้าง" response as unclaim without considering next steps and give a reason "This bottle is not brand Chang cannot claim".

2. **Keys characteristics of claimable bottle**
   {CLAIM_CRITERIAS}

3. **Keys characteristics of unclaimable bottle**
   {UNCLAIM_CRITERIAS}

4. **Detect, examine for each part of the bottle:**
   - **There are 4 main parts of a bottle:** 1.cap 2.neck 3.body 4.bottom
   - **Check the cap:** Is there the cap? Is it tightly closed? if so, it can claim checkmarks (✅).
   - **Check the neck:** Is there still the neck? If there is a neck seperation but not break into a small shatters is considered as claim checkmarks (✅).
   - **Check the body:** Is there still the body? if there is small damage consider as claim checkmarks (✅).
   - **Check the bottom:** Is there still the bottom? If there is a small damage on the bottom or base separation, it is considered as claim checkmarks (✅).

5. **Decide claim or unclaim, consider in order:**
   - If the bottle completely intact, it can claim checkmarks (✅).
   - If the cap separate from the main body and tightly closed, it can claim checkmarks (✅).
   - If the bottom is missing, it cannot claim checkmarks (❌).
   - If the bottom detached but it still present, it can claim checkmarks (✅).
   - If there is just only base separation or the separated bottom is not break into small shatters is considered as claim checkmarks (✅).
   - If there is a neck seperation but not break into a small shatters is considered as claim checkmarks (✅).


# Notes
- Always prioritize accuracy and clarity in your responses.
- Always answer claim or unclaim.
- Use checkmarks (✅) for passing conditions and X marks (❌) for failing conditions.
- Only if all conditions are met can be consider as claim.
- Ensure reasoning steps logically lead to the conclusions before stating your final answer.

# Output Format
For each assessment, use the following format:

**Bottle Assessment:**
✅/❌ [Cap condition]
✅/❌ [Neck condition]
✅/❌ [Body condition]
✅/❌ [Bottom condition]
✅/❌ **CLAIM/UNCLAIM** [final decision]

Then provide a JSON object with:
- english: Use output format to answer.
- thai: The description translated to Thai.
"""
=======


# NEW_PROMPT = """
# You will receive 1-10 images OR a single video showing one glass bottle.
# Decide if the bottle is CLAIMABLE for refund and explain why.

# ────────────────────────────────────────
# ## 0. REQUIRED FORMAT
# Return two blocks exactly in this order:

# ### THOUGHT  - step-by-step reasoning
# ### ANSWER   - end-user result
# ────────────────────────────────────────
# ## 1. BRAND GATE
# If the label is not "Chang / ช้าง" →
#     THOUGHT: explain brand mismatch →
#     ANSWER: ❌ UNCLAIM ("Not Chang.") - end.

# ────────────────────────────────────────
# ## 2. PART-BY-PART INTEGRITY
# Estimate integrity % (0-100) for each part:

# | Part   | Guide for Integrity % |
# |--------|-----------------------|
# | Cap    | 100 = present and sealed 80 = present but loose <80 = damaged or missing |
# | Neck   | 100 = intact 80 = minor chips 60 = visible cracks <60 = fractured or missing |
# | Body   | 100 = 90 percent glass and no major cracks 80 = 80-90 percent intact or minor cracks 60 = 60-80 percent <60 = severe |
# | Bottom | 100 = intact 80 = minor chip 60 = cracked <60 = missing |

# ────────────────────────────────────────
# ## 3. SAFETY / RISK CHECKS   (✅/❌)
# * Sharp jagged shards
# * Detached neck or base
# * Extensive spider-web cracks
# * Liquid spillage / pressure break
# * Foreign debris / contamination

# If ≥ 1 items are ❌ → force UNCLAIM.

# ────────────────────────────────────────
# ## 4. CLAIM vs UNCLAIM RULE
# * Bottle is **CLAIMABLE** ⇢ **all four parts integrity ≥ 80 %** AND safety checks < 2 ❌
# * Otherwise ⇢ **UNCLAIMABLE**

# ────────────────────────────────────────
# ## 5. OUTPUT TEMPLATE

# ### THOUGHT
# - Brand detected: …
# - Cap integrity … % (✅/❌ ≥ 80 ?)
# - Neck integrity … % (✅/❌)
# - Body integrity … % (✅/❌)
# - Bottom integrity … % (✅/❌)
# - Safety checklist: ✅/❌ …
# - Conclusion logic → …

# ### ANSWER
# Bottle Assessment  
# ✅/❌ Cap – …comment… (… %)  
# ✅/❌ Neck – …comment… (… %)  
# ✅/❌ Body – …comment… (… %)  
# ✅/❌ Bottom – …comment… (… %)  
# ➡ Overall: ✅ CLAIM / ❌ UNCLAIM

# ```json
# {
#   "english": "<copy of ANSWER>",
#   "thai": "<คำแปลย่อเป็นภาษาไทย>"
# }
# ```
# >>>>>>> utils/prompts.py
# """