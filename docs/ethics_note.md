# Ethics Note

**Project:** Conversational Clustering on UCDP GEDEvent 25.1  
**Document:** `docs/ethics_note.md`  
**Version:** v0.1

---

## 1. Scope

This note covers dataset ethics, human-rater ethics, privacy, and project-level handling of sensitive conflict-event content.

---

## 2. Dataset Ethics

The project uses the UCDP Georeferenced Event Dataset (GED) 25.1, a public academic dataset produced by Uppsala University.

- The unit of analysis is an event, not an individual person.
- The dataset contains no direct personal identifiers.
- Actor fields identify organizations, not private individuals.
- The `where_description` field is a location description, not a personal identifier.

Because the dataset is public, non-personal, and academic in origin, no anonymization is required for the dataset itself.

---

## 3. Sensitive Content

The dataset describes real organized violence, including fatalities and violence against civilians. Even without graphic imagery, the content is sensitive.

Project handling rules:

- event text must be treated as conflict-sensitive material
- LLM refusals or safety-filter interruptions must be logged, not silently dropped
- generated labels or summaries shown to human raters should be reviewed so they do not sensationalize or trivialize violence
- findings are methodological, not operational or policy guidance

The project does not claim to provide a definitive representation of the war. It studies clustering behavior on an observable conflict dataset with known reporting biases.

---

## 4. Human Rater Ethics

Human raters were recruited as voluntary course peers for the H3 pairwise rating task.

- Participation is voluntary.
- Raters may stop at any time.
- The task contains descriptions of military conflict events and casualty information.
- No graphic imagery is used.

The consent artifact is documented in `docs/rater_consent_form.md`, and task instructions are documented in `docs/rater_instructions.md`.

---

## 5. Data Collected From Raters

The rating workflow collects only:

- forced-choice pairwise preferences
- optional free-text comments
- an anonymous rater identifier

The project does not collect names, email addresses, or demographic data.

---

## 6. Storage, Privacy, and Reporting

- Human-rating data is stored in anonymized form.
- Reporting is done at the aggregate level.
- No individual rater is identified in the repository, report, or presentation.
- The repository may include anonymized rating outputs needed for replication.

The project therefore treats human-rating data as low-risk but still keeps it out of personally identifiable form.

---

## 7. IRB / Review Position

For the dataset itself, no IRB-style review is required because the source is public, academic, and non-personal.

For the human-rating component, the project uses a lightweight informed-consent procedure appropriate to a low-risk course study:

- participants are told the study purpose
- participants receive a content warning
- participation is voluntary
- responses are anonymized and reported only in aggregate

---

## 8. Limitations and Responsible Use

This project has ethical and interpretive limits:

- the underlying data inherits reporting biases from conflict-event collection
- the project studies methodological validity, not battlefield truth
- low inter-rater reliability in H3 means the human reference signal is weak
- strong displayed-label bias in the oracle means H3 failed as evidence for oracle validity

These limitations should be stated clearly in the final report rather than hidden behind aggregate scores.
