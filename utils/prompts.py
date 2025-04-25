"""
Prompt Templates

This module contains prompt templates used across the application.
"""

# Story generation prompt template used for OpenAI vision model

# Characteristic from gpt-4o-mini =========================================================================================================
# CLAIM_CRITERIAS = """
# 1.	Type: All bottles are green glass, typically used for beer packaging.
# 2.	Breakage:
#   o	Varied degrees of breakage, with several exhibiting significant jagged breaks and others featuring clean separations.
#   o	Some have irregular and violent break patterns, indicating rough handling or impact.
# 3.	Shards:
#   o	Multiple sharp edges and several large shards visible in most cases, posing safety hazards.
#   o	Many bottles contain numerous small, sharp fragments scattered around.
# 4.	Condition:
#   o   Most bottles remain mostly intact below the break but are generally deemed unusable due to structural instability.
#   o	Some bottles retain intact bases but have unusable necks or tops.
# 5.	Caps: Multiple examples show that caps remain attached, highlighting that liquid contents may have been present before breakage.
# 6.	Liquid Presence: Signs of liquid spillage are evident in several cases, indicating recent use.
# 7.	Safety Risks: The presence of sharp edges from breakage raises significant safety concerns across nearly all bottles.
# 8.	Reuse Potential: Only a few bottles might still be usable, while most will require careful handling due to sharp shards.
# 9.	Impact Residue: Indicators of rough impacts are noted in several descriptions, suggesting prior violent handling or dropping.
# 10. Structural Integrity: Several bottles show cracks within the body, indicating impending failure despite partial integrity being maintained.
# """

# UNCLAIM_CRITERIAS = """
# 1.	Type: All observed bottles are green glass, typically indicating beer packaging.
# 2.	Breakage:
#   o	Most bottles exhibit jagged breaks, particularly evident at the neck or top sections.
#   o	Several show extensive fragmentation, indicating a significant impact or drop.
# 3.	Shards:
#   o	Numerous sharp edges and a combination of large and small shards are noted, raising safety concerns.
#   o	Various bottles have visibly jagged pieces scattered around, suggesting violent breakage.
# 4.	Condition:
#   o	Many bottles are mostly intact below the break but are deemed unusable due to instability from significant upper damage.
#   o	Some bottles retain their caps, indicating contents may have been present at the time of breakage.
# 5.	Liquid Presence: Visible liquid spills in some instances suggest that the bottles were recently in use prior to breaking.
# 6.	Safety Risks: Sharp edges from broken glass pose substantial safety hazards across all bottles.
# 7.	Structural Integrity: Compromised structures are a common theme, making nearly all bottles unsafe for handling.
# 8.	Fragmentation: The extent of fragmentation across the bottles reveals a pattern of severe breakage, indicating high impacts.
# 9.	Indications of Use: Several descriptions highlight the presence of liquid, reinforcing the likelihood that these bottles were filled prior to being damaged.
# """
# ========================================================================================================================================

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
5.	Base Separation
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
# ========================================================================================================================================


# STORY_GENERATION_PROMPT="""
# You will receive an image or multiple images of one bottle or a video of a broken bottle.
# Your task is to classify claim or unclaim based on the provided images or video and give reasons why you decide to do that.
# The answer have to specify that the bottle can claim or unclaim and which part of the bottle has broken
# and evaluate condition of completeness of the bottle as percentage if it below 80% it unclaim otherwise it can claim

# You will receive the image and examine to provide an accurate answer.

# # Steps
# 1. **Detect brand of bottle:**
#    - Check whether what brand is this bottle
#    - if it's "Chang" or "ช้าง" need to be considered in the next step
#    - if it is not "Chang" or "ช้าง" response as unclaim without consider next step and give a reason "This bottle is not brand Chang cannot claim".
# 2. **Examine each part of the bottle:**
#    - **There are 4 main parts of a bottle** 1.cap 2.neck 3.body 4.bottom
#    - **Check the cap** Is there the cap? Is it thighly close?
#    - **Check the neck** Is there still the neck? Is it break or damage? If it not damage too much it can claim
#    - **Check the body** Is there still the body? Is it break or damage? If it not damage too much it can claim
#    - **Check the bottom** Is there still the bottom? Is it break or damage? If it not damage too much it can claim
#    - **Assess the overall condition of the bottle:** calculate score as percentage of condition of completeness of the bottle.
# 3. **Deciding calim or unclaim:**
#    - From the evaluated score decide whether it can claim if the score higher than 80% otherwise it unclaim.
 
# # Notes
# - Always prioritize accuracy and clarity in your responses.
# - Always answer claim or unclaim and reasons
# - Ensure reasoning steps logically lead to the conclusions before stating your final answer.
 
# # Example
# - Can claim condition(80%) because the bottom has broken but overall still intact.
# - Can claim condition(80%) because the neck of the bottle has broken but the shatters are still intact.
# - Unclaim condition(50%) because the bottle has broken and most of shatters has missed.
# - Unclaim condition(50%) beacuse the body of the bottle has missed.
 
# # Output format
# Return ONLY a JSON object with these fields:
# - english: Answer claim or unclaim with reasons
# - thai: The description translated to Thai
# """

NEW_PROMPT = f"""
You will receive an image or multiple images of one bottle or a video of a broken bottle.
Your task is to classify claim or unclaim based on the provided images or video and give reasons following specific criteria.
The answer must clearly specify whether the bottle can claim or unclaim,
and evaluate the condition of completeness of the bottle as a percentage (if below 80% it's unclaim, otherwise it can claim).

# Steps
1. **Detect brand of bottle:**
   - Check whether what brand is this bottle
   - if it's "Chang" or "ช้าง" need to be considered in the next step
   - if it is not "Chang" or "ช้าง" response as unclaim without considering next steps and give a reason "This bottle is not brand Chang cannot claim".

2. **Keys characteristics of claimable bottle**
   {CLAIM_CRITERIAS}

3. **Keys characteristics of unclaimable bottle**
   {UNCLAIM_CRITERIAS}

4. **Detect, examine and assess score for each part of the bottle:**
   - **There are 4 main parts of a bottle:** 1.cap 2.neck 3.body 4.bottom
   - **Check the cap:** Is there the cap? Is it tightly closed? Calculate score as percentage of this part
   - **Check the neck:** Is there still the neck? Is it broken or damaged? Calculate score as percentage of this part
   - **Check the body:** Is there still the body? Is it broken or damaged? Calculate score as percentage of this part
   - **Check the bottom:** Is there still the bottom? Is it broken or damaged? Calculate score as percentage of this part

5. **Decide claim or unclaim:**
   - From the evaluated scores, decide whether it can claim if the overall score is higher than 80%, otherwise it's unclaim.
 
# Notes
- Always prioritize accuracy and clarity in your responses.
- Always answer claim or unclaim with clear reasons.
- Use checkmarks (✅) for passing conditions and X marks (❌) for failing conditions.
- Ensure reasoning steps logically lead to the conclusions before stating your final answer.
 
# Output Format
For each assessment, use the following format:

**Bottle Assessment:**
✅/❌ [Cap condition]
✅/❌ [Neck condition]
✅/❌ [Body condition]
✅/❌ [Bottom condition]
✅/❌ **CLAIM/UNCLAIM** [Overall percentage and final decision]

Then provide a JSON object with:
- english: Use output format to answer
- thai: The description translated to Thai
"""