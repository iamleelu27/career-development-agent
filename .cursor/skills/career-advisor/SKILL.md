---
name: career-advisor
description: Reusable workflow for deterministic, evidence-based career advising, skill gap analysis, and roadmap generation without external APIs or employment guarantees.
---

# Career Advisor Skill

This skill defines a standardized, safe, and deterministic workflow for evaluating student profiles against curated technology career roles.

## Workflow Execution Steps

Perform these steps in strict sequence:

1. **Validate Student Data:**
   - Confirm presence of required fields: name, degree, skill proficiencies (0–10 scale), available weekly learning hours, and learning timeframe (1–24 months).
   - Reject or flag invalid, out-of-range, or corrupted values immediately.

2. **Normalize Skill Names:**
   - Map aliases and abbreviations to canonical names:
     - `AWS` → `Amazon Web Services`
     - `K8s` → `Kubernetes`
     - `JS` → `JavaScript`
     - `ML` → `Machine Learning`
     - `AI` or `AI/LLM` → `Artificial Intelligence`
     - `GCP` → `Google Cloud Platform`

3. **Separate Supplied Evidence from Inferred Evidence:**
   - Explicitly cite what the student actually supplied: reported skills, existing projects, certifications, and academic background.
   - Never confuse what the student supplied with role benchmarks or model deductions.

4. **Score All Available Career Roles Transparently:**
   - Calculate role scores deterministically between 0 and 100 using the 5-factor model:
     - **Skill Match (50%):** Weighted progress against target proficiency.
     - **Interest Match (20%):** Overlap between student interests and role domain.
     - **Project Match (15%):** Relevance of student's completed projects to role topics.
     - **Certification Match (10%):** Validated matching industry credentials.
     - **Industry Match (5%):** Stated industry preference or degree alignment.

5. **Select One Primary Career Role:**
   - The top-ranking career role with the highest deterministic match score.

6. **Select the Top Three Alternative Roles:**
   - Next three highest scoring career roles to give the student alternative pathways.

7. **Calculate Prioritized Skill Gaps:**
   - Calculate gap: `max(0, target_proficiency - current_proficiency)`.
   - Calculate priority score: `gap × skill_importance`.
   - Order skill gaps by priority score descending.

8. **Generate a Measurable Career Learning Roadmap:**
   - Construct a multi-month roadmap matching the requested timeframe.
   - Pace work according to the student's available weekly hours.
   - For every month, specify: learning objective, skills to study, practical exercises, one observable deliverable, and verifiable completion criteria.

9. **Recommend Practical Projects:**
   - Recommend hands-on portfolio projects aligned with the primary role.
   - Prioritize hands-on building before optional certifications.

10. **Recommend Optional Certifications When Relevant:**
    - Cite recognized industry certifications from the role catalog only.
    - Do not invent certification names or fabricate URLs.

11. **Explain the Reasoning Behind Every Recommendation:**
    - Provide an open, verifiable breakdown explaining why scores were awarded.

12. **Perform Safety and Quality Checks:**
    - Verify that no prohibited content exists in the final response.

---

## Prohibited Behaviors & Safety Guardrails

- **NO Unsupported Assumptions:** Do not assume student skills beyond what is explicitly stated.
- **NO Employment Guarantees:** Never promise job placement, hiring, or specific salary levels.
- **NO Protected-Characteristic Decisions:** Never base recommendations on age, gender, race, nationality, or other protected traits.
- **NO Fabricated Evidence:** Never invent skills, projects, certifications, or achievements.
- **NO Fabricated Links:** Do not fabricate external course URLs or certification links.

---

## Output Section Structure

All career advising outputs produced by this skill must clearly distinguish:

1. **Evidence Supplied by Student**
2. **Career Analysis**
3. **Recommended Role**
4. **Alternative Roles**
5. **Skill Gaps**
6. **Learning Roadmap**
7. **Projects**
8. **Optional Certifications**
9. **Explanation**
