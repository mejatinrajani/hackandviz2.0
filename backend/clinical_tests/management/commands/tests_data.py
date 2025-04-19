from django.core.management.base import BaseCommand
from clinical_tests.models import Test, Question

tests_data = {
    "Beck Depression Inventory (BDI-II)": {
        "questions": [
            "1. Sadness:\n0 - I do not feel sad.\n1 - I feel sad much of the time.\n2 - I am sad all the time.\n3 - I am so sad or unhappy that I can't stand it.",
            "2. Pessimism:\n0 - I am not discouraged about my future.\n1 - I feel more discouraged about my future than I used to.\n2 - I do not expect things to work out for me.\n3 - I feel my future is hopeless.",
            "3. Past Failure:\n0 - I do not feel like a failure.\n1 - I have failed more than I should.\n2 - As I look back, I see failures.\n3 - I feel I am a complete failure.",
            "4. Loss of Pleasure:\n0 - I get as much pleasure as I ever did.\n1 - I enjoy things less.\n2 - I get little pleasure from anything.\n3 - I can't get any pleasure from anything.",
            "5. Guilty Feelings:\n0 - I don't feel particularly guilty.\n1 - I feel guilty much of the time.\n2 - I feel quite guilty most of the time.\n3 - I feel guilty all of the time.",
            "6. Punishment Feelings:\n0 - I don't feel I'm being punished.\n1 - I feel I may be punished.\n2 - I expect to be punished.\n3 - I feel I'm being punished.",
            "7. Self-Dislike:\n0 - I feel the same about myself.\n1 - I have lost confidence in myself.\n2 - I am disappointed in myself.\n3 - I dislike myself.",
            "8. Self-Criticalness:\n0 - I don't criticize myself more than usual.\n1 - I'm more critical of myself.\n2 - I criticize myself for all my faults.\n3 - I blame myself for everything bad.",
            "9. Suicidal Thoughts:\n0 - I don't have thoughts of harming myself.\n1 - I have thoughts of harming myself but wouldn't act.\n2 - I would like to kill myself.\n3 - I would kill myself if I had the chance.",
            "10. Crying:\n0 - I don't cry more than usual.\n1 - I cry more than I used to.\n2 - I cry all the time.\n3 - I used to be able to cry, but now I can't.",
            "11. Agitation:\n0 - I am no more restless than usual.\n1 - I feel more restless.\n2 - I'm so restless I can't sit still.\n3 - I'm restless and have to keep moving.",
            "12. Loss of Interest:\n0 - I haven't lost interest in others.\n1 - I'm less interested in others.\n2 - I've lost most of my interest in others.\n3 - I've lost all interest in others.",
            "13. Indecisiveness:\n0 - I make decisions as well as ever.\n1 - I avoid decisions more than before.\n2 - I have great difficulty making decisions.\n3 - I can't make any decisions at all.",
            "14. Worthlessness:\n0 - I don't feel worthless.\n1 - I don't feel as worthwhile as before.\n2 - I feel worthless.\n3 - I feel completely worthless.",
            "15. Loss of Energy:\n0 - I have as much energy as ever.\n1 - I have less energy.\n2 - I don't have enough energy for anything.\n3 - I have no energy at all.",
            "16. Sleep Changes:\n0 - My sleep hasn't changed.\n1 - I sleep slightly more/less than usual.\n2 - I sleep much more/less than usual.\n3 - I can't sleep or sleep all day.",
            "17. Irritability:\n0 - I'm no more irritable than usual.\n1 - I'm more irritable than usual.\n2 - I'm much more irritable.\n3 - I'm irritable all the time.",
            "18. Appetite Changes:\n0 - My appetite hasn't changed.\n1 - My appetite is slightly less/better.\n2 - My appetite is much less/better.\n3 - I have no appetite or overeat constantly.",
            "19. Concentration Difficulty:\n0 - I concentrate as well as ever.\n1 - I can't concentrate as well.\n2 - It's hard to focus on anything.\n3 - I can't concentrate at all.",
            "20. Fatigue:\n0 - I'm no more tired than usual.\n1 - I get tired more easily.\n2 - I'm too tired to do most things.\n3 - I'm too tired to do anything.",
            "21. Loss of Interest in Sex:\n0 - I haven't noticed changes in my sex drive.\n1 - I'm less interested in sex.\n2 - I'm much less interested in sex.\n3 - I've lost all interest in sex."
        ],
        "scoring": "21 items scored 0-3. Total range: 0-63.\nSeverity: 0–13 (Minimal), 14–19 (Mild), 20–28 (Moderate), 29–63 (Severe)."
    },
    "Generalized Anxiety Disorder 7 (GAD-7)": {
        "questions": [
            "1. Feeling nervous, anxious, or on edge:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "2. Not being able to stop/control worrying:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "3. Worrying too much about different things:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "4. Trouble relaxing:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "5. Being restless/fidgety:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "6. Becoming easily annoyed/irritable:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day",
            "7. Feeling afraid of something awful happening:\n0 - Not at all\n1 - Several days\n2 - More than half the days\n3 - Nearly every day"
        ],
        "scoring": "7 items scored 0-3. Total range: 0-21.\nSeverity: 0–4 (Minimal), 5–9 (Mild), 10–14 (Moderate), 15–21 (Severe)."
    },
    "Penn State Worry Questionnaire (PSWQ)": {
        "questions": [
            "1. If I don’t have enough time to do everything, I don’t worry about it (Reverse scored):\n1 - Not at all typical\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "2. My worries overwhelm me:\n1 - Not at all typical\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "3. I don’t tend to worry about things (Reverse scored):\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "4. Many situations make me worry:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "5. I can't help worrying about things:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "6. When under pressure, I worry a lot:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "7. I'm always worrying about something:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "8. I find it easy to dismiss worrisome thoughts (Reverse scored):\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "9. After finishing tasks, I worry about what's next:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "10. I never worry about anything (Reverse scored):\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "11. When nothing can be done, I stop worrying (Reverse scored):\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "12. I've been a worrier all my life:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "13. I notice I've been worrying:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "14. Once I start worrying, I can’t stop:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "15. I worry all the time:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical",
            "16. I worry until tasks are done:\n1 - Not at all\n2 - Somewhat not\n3 - Neutral\n4 - Somewhat\n5 - Very typical"
        ],
        "scoring": "16 items scored 1-5. Reverse scores: 1,3,8,10,11 (5→1, 4→2, etc.). Total: 16-80.\nHigher scores = pathological worry."
    },
    "Perceived Stress Scale (PSS-10)": {
        "questions": [
            "1. In the last month, how often have you been upset because of something unexpected?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "2. How often felt unable to control important things?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "3. How often felt nervous/stressed?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "4. How often felt confident handling problems? (Reverse scored)\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "5. How often felt things were going your way? (Reverse scored)\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "6. How often couldn't cope with all your responsibilities?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "7. How often controlled irritations? (Reverse scored)\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "8. How often felt on top of things? (Reverse scored)\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "9. How often angered by things outside control?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often",
            "10. How often felt difficulties were overwhelming?\n0 - Never\n1 - Almost never\n2 - Sometimes\n3 - Fairly often\n4 - Very often"
        ],
        "scoring": "10 items scored 0-4. Reverse items 4,5,7,8. Total: 0-40.\nHigher = more stress. Norms: 0-13 (Low), 14-26 (Moderate), 27-40 (High)."
    },
    "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)": {
        "questions": [
            "1. Time spent on obsessions:\n0 - None\n1 - Mild (<1 hr/day)\n2 - Moderate (1-3 hrs)\n3 - Severe (3-8 hrs)\n4 - Extreme (>8 hrs)",
            "2. Obsession interference:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Severe\n4 - Extreme",
            "3. Distress from obsessions:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Severe\n4 - Extreme",
            "4. Resistance to obsessions:\n0 - Full resistance\n1 - Try to resist most\n2 - Some effort\n3 - Yields reluctantly\n4 - Completely yields",
            "5. Control over obsessions:\n0 - Complete\n1 - Much control\n2 - Moderate\n3 - Little\n4 - None",
            "6. Time spent on compulsions:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Severe\n4 - Extreme",
            "7. Compulsion interference:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Severe\n4 - Extreme",
            "8. Distress if prevented:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Severe\n4 - Extreme",
            "9. Resistance to compulsions:\n0 - Always resists\n1 - Delays most\n2 - Some resistance\n3 - Yields reluctantly\n4 - No resistance",
            "10. Control over compulsions:\n0 - Complete\n1 - Much control\n2 - Moderate\n3 - Little\n4 - None"
        ],
        "scoring": "10 items scored 0-4. Total: 0-40.\nSeverity: 0-7 (Subclinical), 8-15 (Mild), 16-23 (Moderate), 24-31 (Severe), 32-40 (Extreme)."
    },
    "Mood Disorder Questionnaire (MDQ)": {
        "questions": [
            "1. Has there been a period when you... (Yes/No):",
            "a. Felt so good/hyper others noticed?",
            "b. Were so irritable you started fights?",
            "c. Felt much more self-confident?",
            "d. Slept less but didn't miss it?",
            "e. Were more talkative/spoke faster?",
            "f. Had racing thoughts?",
            "g. Were easily distracted?",
            "h. Had much more energy?",
            "i. Were much more active?",
            "j. Were more social/outgoing?",
            "k. Had increased interest in sex?",
            "l. Did risky/unusual things?",
            "m. Spent money causing problems?",
            "2. Did several happen during the same period? (Yes/No)",
            "3. How much problem did this cause?\n0 - None\n1 - Minor\n2 - Moderate\n3 - Serious"
        ],
        "scoring": "Screen positive: 7+ 'Yes' in Q1a-m + Q2 Yes + Q3 ≥ Moderate."
    },
    "Addiction Severity Index (ASI)": {
        "questions": [
            "Medical Status:",
            "1. How many days in past 30 were you bothered by medical problems?",
            "2. How troubled by these problems? (0-4)",
            "3. Importance of treatment? (0-4)",
            "Employment/Support:",
            "4. Days worked in past 30?",
            "5. Days unemployed seeking work?",
            "6. How troubled by employment issues? (0-4)",
            "Alcohol Use:",
            "7. Days used alcohol past 30?",
            "8. Days had alcohol problems?",
            "9. How troubled by alcohol use? (0-4)",
            "Drug Use:",
            "10. Days used drugs past 30?",
            "11. Days had drug problems?",
            "12. How troubled by drug use? (0-4)",
            "Legal Status:",
            "13. Days incarcerated past 30?",
            "14. How troubled by legal issues? (0-4)"
        ],
        "scoring": "Composite scores (0-1) per domain:\nMedical = (Q2 + Q3)/9\nAlcohol = (Q8 + Q9)/9\nDrug = (Q11 + Q12)/9\netc. Higher = more severe."
    },
    "Brief Psychiatric Rating Scale (BPRS)": {
        "questions": [
            "1. Somatic concern:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "2. Anxiety:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "3. Emotional withdrawal:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "4. Conceptual disorganization:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "5. Guilt feelings:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "6. Tension:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "7. Mannerisms/posturing:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "8. Grandiosity:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "9. Depressive mood:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "10. Hostility:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "11. Suspiciousness:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "12. Hallucinations:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "13. Motor retardation:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "14. Uncooperativeness:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "15. Unusual thought content:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "16. Blunted affect:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "17. Excitement:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe",
            "18. Disorientation:\n1 - Not present\n2 - Very mild\n3 - Mild\n4 - Moderate\n5 - Moderately severe\n6 - Severe\n7 - Extremely severe"
        ],
        "scoring": "18 items scored 1-7. Total range: 18-126.\nClinical thresholds: 31+ (Mild), 41+ (Moderate), 53+ (Severe)."
    },
    "Drug Abuse Screening Test (DAST-10)": {
        "questions": [
            "1. Used non-prescribed drugs?\n0 - No\n1 - Yes",
            "2. Abused OTC/prescription drugs?\n0 - No\n1 - Yes",
            "3. Tried to reduce drug use?\n0 - No\n1 - Yes",
            "4. Experienced withdrawal?\n0 - No\n1 - Yes",
            "5. Memory loss from drugs?\n0 - No\n1 - Yes",
            "6. Failed responsibilities?\n0 - No\n1 - Yes",
            "7. Used longer than intended?\n0 - No\n1 - Yes",
            "8. Social/work problems?\n0 - No\n1 - Yes",
            "9. Legal issues?\n0 - No\n1 - Yes",
            "10. Failed quit attempts?\n0 - No\n1 - Yes"
        ],
        "scoring": "10 items scored 0-1. Total range: 0-10.\nCutoff: 3+ indicates substance use disorder (6+ = severe)."
    },
    "Adult ADHD Self-Report Scale (ASRS-v1.1)": {
        "questions": [
            "1. Difficulty sustaining attention:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "2. Careless mistakes:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "3. Difficulty focusing:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "4. Fidgeting/squirming:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "5. Restlessness:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "6. Difficulty listening:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "7. Interrupting others:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "8. Forgetting tasks:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "9. Acting immediately:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often",
            "10. Following instructions:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often"
        ],
        "scoring": "10 items scored 0-4. Total range: 0-40.\nCutoff: 14+ suggests ADHD. Clinical diagnosis required."
    },
    "Pittsburgh Sleep Quality Index (PSQI)": {
        "questions": [
            "1. Sleep latency (>30 mins to fall asleep):\n0 - Not during past month\n1 - Less than once/week\n2 - 1-2 times/week\n3 - ≥3 times/week",
            "2. Nighttime awakenings:\n0 - Not during past month\n1 - Less than once/week\n2 - 1-2 times/week\n3 - ≥3 times/week",
            "3. Subjective sleep quality:\n0 - Very good\n1 - Fairly good\n2 - Fairly bad\n3 - Very bad",
            "4. Sleep duration:\n0 - >7 hours\n1 - 6-7 hours\n2 - 5-6 hours\n3 - <5 hours",
            "5. Daytime dysfunction:\n0 - No problem\n1 - Mild\n2 - Moderate\n3 - Severe",
            "6. Sleep medication use:\n0 - Not during past month\n1 - Less than once/week\n2 - 1-2 times/week\n3 - ≥3 times/week",
            "7. Sleep efficiency (% time asleep in bed):\n0 - >85%\n1 - 75-84%\n2 - 65-74%\n3 - <65%"
        ],
        "scoring": "7 components scored 0-3. Total range: 0-21.\nPoor sleep: ≥5. Higher scores = worse sleep quality."
    },
    "Barratt Impulsiveness Scale (BIS-11)": {
        "questions": [
            "1. I plan tasks carefully (Reverse scored):\n1 - Rarely/Never\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "2. I act without thinking:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "3. I ignore consequences:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "4. Easily distracted:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "5. Get bored easily:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "6. Trouble sitting still:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "7. Act on impulse:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "8. Prefer routine (Reverse scored):\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "9. Hard to concentrate:\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always",
            "10. Upset by changes (Reverse scored):\n1 - Rarely\n2 - Occasionally\n3 - Often\n4 - Almost Always"
        ],
        "scoring": "30 items (abbreviated here) scored 1-4. Reverse scores: 1,8,10.\nTotal range: 30-120. Norms: 52-71 (Average), 72+ (High impulsivity)."
    },
    "Clinician-Administered PTSD Scale (CAPS-5)": {
        "questions": [
            "1. Intrusive memories:\n0 - None\n1 - Mild (1x/month)\n2 - Moderate (2-3x/month)\n3 - Severe (1x/week)\n4 - Extreme (daily)",
            "2. Distressing dreams:\n0 - None\n1 - Mild (occasional)\n2 - Moderate (weekly)\n3 - Severe (3-4x/week)\n4 - Extreme (nightly)",
            "3. Flashbacks/dissociation:\n0 - Absent\n1 - Mild (brief)\n2 - Moderate (prolonged)\n3 - Severe (hours)\n4 - Extreme (incapacitating)",
            "4. Psychological cue reactivity:\n0 - None\n1 - Mild distress\n2 - Moderate distress\n3 - Severe distress\n4 - Panic/overwhelm",
            "5. Physiological cue reactivity:\n0 - None\n1 - Mild (sweating)\n2 - Moderate (racing heart)\n3 - Severe (tremors)\n4 - Extreme (collapse)",
            "6. Avoidance of thoughts:\n0 - Never\n1 - Rare avoidance\n2 - Occasional avoidance\n3 - Frequent avoidance\n4 - Total avoidance",
            "7. Avoidance of reminders:\n0 - Never\n1 - Rare\n2 - Occasional\n3 - Frequent\n4 - Complete isolation",
            "8. Trauma-related amnesia:\n0 - Full recall\n1 - Minor gaps\n2 - Moderate gaps\n3 - Major gaps\n4 - Complete amnesia",
            "9. Negative beliefs:\n0 - None\n1 - Mild self-doubt\n2 - Moderate guilt\n3 - Severe worthlessness\n4 - Delusional self-blame",
            "10. Distorted blame:\n0 - None\n1 - Mild self-criticism\n2 - Moderate guilt\n3 - Severe shame\n4 - Irrational responsibility",
            "11. Negative emotions:\n0 - None\n1 - Occasional sadness\n2 - Frequent fear\n3 - Persistent anger\n4 - Constant despair",
            "12. Loss of interest:\n0 - None\n1 - Mild reduction\n2 - Moderate loss\n3 - Severe disinterest\n4 - Complete withdrawal",
            "13. Detachment:\n0 - None\n1 - Occasional distance\n2 - Frequent isolation\n3 - Severe numbness\n4 - Complete alienation",
            "14. Positive emotion deficit:\n0 - Normal\n1 - Mild restriction\n2 - Moderate limitation\n3 - Severe deficit\n4 - Total absence",
            "15. Irritability/anger:\n0 - None\n1 - Mild annoyance\n2 - Moderate arguments\n3 - Frequent outbursts\n4 - Violence/destruction",
            "16. Reckless behavior:\n0 - None\n1 - Occasional risks\n2 - Drug misuse\n3 - Self-harm\n4 - Life-threatening acts",
            "17. Hypervigilance:\n0 - None\n1 - Mild scanning\n2 - Moderate suspicion\n3 - Severe monitoring\n4 - Paranoia",
            "18. Startle response:\n0 - Normal\n1 - Mild jumpiness\n2 - Moderate reactions\n3 - Severe panic\n4 - Debilitating fear",
            "19. Concentration issues:\n0 - None\n1 - Mild distraction\n2 - Moderate focus loss\n3 - Severe impairment\n4 - Unable to function",
            "20. Sleep disturbance:\n0 - None\n1 - Occasional insomnia\n2 - Frequent awakenings\n3 - Severe sleep deficit\n4 - No restorative sleep"
        ],
        "scoring": (
            "20 items scored 0-4 (combining frequency/intensity).\n"
            "Total severity: 0-80.\n"
            "DSM-5 diagnosis requires:\n"
            "1+ intrusion symptoms (Q1-5)\n"
            "1+ avoidance (Q6-7)\n"
            "2+ cognition/mood symptoms (Q8-14)\n"
            "2+ arousal symptoms (Q15-20)\n"
            "Severity ranges: 0-19 (Subclinical), 20-39 (Mild), 40-59 (Moderate), 60-80 (Severe)"
        )
    },
    "Eating Disorder Examination Questionnaire (EDE-Q 6.0)": {
        "questions": [
            "1. Objective binge episodes (past 28 days):\n0 - None\n1 - 1-5 times\n2 - 6-12 times\n3 - 13-20 times\n4 - 21-27 times\n5 - 28+ times\n6 - Multiple daily",
            "2. Loss of control during eating:\n0 - Never\n1 - Rarely\n2 - Sometimes\n3 - Often\n4 - Very Often\n5 - Usually\n6 - Always",
            "3. Vomiting for weight control:\n0 - Never\n1 - 1-5 times\n2 - 6-12 times\n3 - 13-20 times\n4 - 21-27 times\n5 - 28+ times\n6 - Multiple daily",
            "4. Laxative misuse:\n0 - Never\n1 - 1-5 times\n2 - 6-12 times\n3 - 13-20 times\n4 - 21-27 times\n5 - 28+ times\n6 - Multiple daily",
            "5. Compulsive exercise:\n0 - Never\n1 - 1-5 days\n2 - 6-12 days\n3 - 13-20 days\n4 - 21-27 days\n5 - Daily\n6 - Multiple times/day",
            "6. Weight dissatisfaction:\n0 - Not at all\n1 - Slightly\n2 - Mildly\n3 - Moderately\n4 - Markedly\n5 - Severely\n6 - Extremely",
            "7. Shape dissatisfaction:\n0 - Not at all\n1 - Slightly\n2 - Mildly\n3 - Moderately\n4 - Markedly\n5 - Severely\n6 - Extremely",
            "8. Body checking discomfort:\n0 - Not at all\n1 - Slightly\n2 - Mildly\n3 - Moderately\n4 - Markedly\n5 - Severely\n6 - Extremely",
            "9. Weight preoccupation:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Strong\n4 - Severe\n5 - Extreme\n6 - All-consuming",
            "10. Fear of weight gain:\n0 - None\n1 - Mild\n2 - Moderate\n3 - Strong\n4 - Severe\n5 - Extreme\n6 - Paralyzing"
        ],
        "scoring": (
            "Items 1-5: Behavioral frequency (0-6)\n"
            "Items 6-10: Cognitive severity (0-6)\n"
            "Global Score = (Restraint + Eating Concern + Shape Concern + Weight Concern) / 4\n"
            "Clinical cutoff: ≥4.0\n"
            "Norms: 2.3 (Community), 4.5 (Anorexia/Bulimia)"
        )
    },
    
    "General Psychological Screening": {
    "questions": [
        "1. How often do you experience distress or unease in daily life?\n0 - Not at all\n1 - Sometimes\n2 - Often\n3 - Always",
        "2. How often do you feel overwhelmed by daily tasks?\n0 - Not at all\n1 - Sometimes\n2 - Often\n3 - Always",
        "3. Do you feel you have adequate support in your daily life?\n0 - Always\n1 - Often\n2 - Sometimes\n3 - Not at all",
        "4. How often do you experience difficulty concentrating?\n0 - Not at all\n1 - Sometimes\n2 - Often\n3 - Always",
        "5. How often do you feel hopeful about the future?\n0 - Always\n1 - Often\n2 - Sometimes\n3 - Not at all"
    ],
    "scoring": "5 items scored 0-3. Total range: 0-15. Severity: 0–5 (Low), 6–10 (Moderate), 11–15 (High). Consult professional for interpretation."
    },

    "Minnesota Multiphasic Personality Inventory (MMPI-2-RF)": {
        "questions": [
            "1. I often feel anxious or nervous:\nTrue\nFalse",
            "2. I rarely have trouble sleeping:\nTrue\nFalse",
            "3. Large crowds make me uncomfortable:\nTrue\nFalse",
            "4. I sometimes feel watched/followed:\nTrue\nFalse",
            "5. I worry excessively about minor things:\nTrue\nFalse",
            "6. My mood is usually cheerful:\nTrue\nFalse",
            "7. I hear voices others don't:\nTrue\nFalse",
            "8. I prefer solitary activities:\nTrue\nFalse",
            "9. I feel unforgivably guilty:\nTrue\nFalse",
            "10. I sometimes feel thoughts scare me:\nTrue\nFalse"
        ],
        "scoring": (
            "567 items (sample shown).\n"
            "Validity scales: L (Lie), F (Infrequency), K (Defensiveness)\n"
            "Clinical scales (T-scores):\n"
            "- Hypochondriasis (Hs)\n"
            "- Depression (D)\n"
            "- Hysteria (Hy)\n"
            "- Psychopathy (Pd)\n"
            "- Paranoia (Pa)\n"
            "Interpretation:\n"
            "T ≥ 65 = Clinically significant\n"
            "T ≥ 80 = Severe psychopathology\n"
            "Must be administered/scored by licensed professionals"
        )
    }
}

class Command(BaseCommand):
    help = 'Load test data into the database'

    def handle(self, *args, **kwargs):
        copyrighted_tests = [
            "Beck Depression Inventory (BDI-II)",
            "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)",
            "Clinician-Administered PTSD Scale (CAPS-5)",
            "Eating Disorder Examination Questionnaire (EDE-Q 6.0)",
            "Minnesota Multiphasic Personality Inventory (MMPI-2-RF)",
            "Addiction Severity Index (ASI)",
            "Brief Psychiatric Rating Scale (BPRS)"
        ]

        for test_name, data in tests_data.items():
            is_placeholder = test_name in copyrighted_tests
            test, created = Test.objects.get_or_create(
                name=test_name,
                defaults={
                    'scoring_rules': data['scoring'],
                    'is_placeholder': is_placeholder
                }
            )
            order = 1
            for question_text in data['questions']:
                lines = question_text.split('\n')
                question_text_clean = lines[0]
                is_open_ended = (
                    "Open-ended" in question_text or
                    test_name == "Pittsburgh Sleep Quality Index (PSQI)" and order <= 4 or
                    test_name == "Addiction Severity Index (ASI)" and order in [1, 4, 5, 7, 8, 10, 11, 13]
                )
                options = []
                if not is_open_ended:
                    if test_name == "Mood Disorder Questionnaire (MDQ)" and order == 1:
                        # Skip Q1 header
                        continue
                    elif test_name == "Mood Disorder Questionnaire (MDQ)" and question_text.startswith(('a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.', 'i.', 'j.', 'k.', 'l.', 'm.')):
                        options = [
                            {'text': 'Yes', 'score': 1},
                            {'text': 'No', 'score': 0}
                        ]
                    elif test_name == "Minnesota Multiphasic Personality Inventory (MMPI-2-RF)":
                        options = [
                            {'text': 'True', 'score': 1},
                            {'text': 'False', 'score': 0}
                        ]
                    else:
                        options = [
                            {'text': line.split(' - ')[1], 'score': int(line.split(' - ')[0])}
                            for line in lines[1:] if ' - ' in line and line.split(' - ')[0].replace('.', '').isdigit()
                        ]
                        if not options and any('Yes' in line or 'No' in line for line in lines[1:]):
                            options = [
                                {'text': line.strip(), 'score': 1 if 'Yes' in line else 0}
                                for line in lines[1:] if 'Yes' in line or 'No' in line
                            ]
                Question.objects.get_or_create(
                    test=test,
                    order=order,
                    defaults={
                        'text': question_text_clean,
                        'options': options,
                        'is_open_ended': is_open_ended
                    }
                )
                order += 1
        self.stdout.write(self.style.SUCCESS('Successfully loaded test data'))