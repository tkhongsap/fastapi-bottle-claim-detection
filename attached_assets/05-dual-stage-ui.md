# **PRD – “Production-Date Gate” & Dual-Stage Upload UI**

*ClaimBottle AI* · **Version 1.0** · *12 May 2025*

---

## 1 · Purpose

Only Chang bottles produced **≤ 120 days ago** are refundable. The new *Production Date Verification* (“date gate”) must (1) confirm the bottle age and (2) pass the result forward to the existing damage-assessment flow—while upgrading the UI to a polished **two-step wizard**.

---

## 2 · Goals & KPIs

| Goal                           | Metric                                          | Target  |
| ------------------------------ | ----------------------------------------------- | ------- |
| Block ineligible bottles early | % of “too-old” bottles reaching damage endpoint | ↓ 30 %  |
| Speed                          | Median flow completion                          | < 90 s  |
| Accuracy (date OCR)            | F-score                                         | ≥ 0.90  |
| Mobile success                 | Label-capture success on screens ≤ 768 px       | ≥ 95 %  |
| UX                             | CSAT (post-launch survey)                       | ≥ 4 / 5 |

---

## 3 · User Stories

1. **Claimant**: *I photograph the label*. The app instantly tells me if my bottle age is acceptable.
2. **Claimant**: If acceptable, *I upload photos/video of damage* without repeating steps.
3. **Admin/QA**: I can audit logs to see whether a failure was due to date or damage.

---

## 4 · High-Level Flow

```
(1) Upload label → /verify-date → ELIGIBLE? → (2) Upload damage media → /claimability → Results
```

### Step 1 “Check Production Date”

* Accept **1-3 close-up images** (`.jpg/.png`, ≤ 5 MB each).
* AI extracts date → returns `ELIGIBLE | INELIGIBLE`.
* If ineligible: red banner + retry.

### Step 2 “Upload Damage Media”

* Existing flow (images ≤ 10 MB each, up to 10 images OR 1 video ≤ 50 MB).
* Label verdict and production date persist in context.

Results page merges **Date Banner** + **Damage Checklist**.

---

## 5 · Functional Requirements

### 5.1 Back-End

| Endpoint        | Method           | Purpose                                                                                               |
| --------------- | ---------------- | ----------------------------------------------------------------------------------------------------- |
| `/verify-date`  | POST (multipart) | Extract date, calc age, return eligibility JSON.                                                      |
| `/claimability` | POST (multipart) | Accept damage media **+ optional `date_verification` JSON**; run v3 prompt; return structured result. |

*`verify-date`* must:

* OCR with vision-LLM; handle DD/MM/YY, DD MM YY, YYMMDD.
* Return **HTTP 422** on unreadable label; include `confidence`.
* Use UTC for day diff; **Day 120 counts as eligible**.

### 5.2 Front-End (React + Tailwind)

#### Components

| ID                   | Component                                     | Key Points                |
| -------------------- | --------------------------------------------- | ------------------------- |
| **Stepper**          | 1 Date · 2 Damage · 3 Results                 | active/completed states   |
| **LabelUploadCard**  | close-up capture, 3 thumbnails, 5 MB limit    | dashed overlay, help link |
| **DateResultBanner** | shows date, days, ✅/❌ colour                  | sticky on Results         |
| **DamageUploadCard** | drag-drop reorder, remove thumb, video toggle | inherits old upload       |
| **ErrorToast**       | slide-in, auto-dismiss 6 s                    | network, OCR fail         |
| **HelpModal**        | example images explaining date position       | modal pattern             |

#### State & Script

* `currentStep: 'date' | 'damage'`.
* `dateVerificationResult` context; appended to FormData on damage POST.
* Retry loop if `confidence < 0.60`.

### 5.3 Validation & Limits

* Label images ≤ 5 MB × 3.
* Damage: images ≤ 10 MB × 10 **or** video ≤ 50 MB.
* Strip EXIF metadata client-side (privacy).

---

## 6 · UX / UI Specs

* **Colours**:

  * Primary `sky-500`, Success `emerald-500`, Danger `rose-500`.
* **Typography**: Poppins + Noto Sans Thai.
* **Motion**: Framer Motion fade-in 250 ms.
* **Mobile**: single-column; bottom-sticky CTA buttons.

**Wireframe snapshot** provided in Figma (attached).

---

## 7 · i18n

Add keys listed in detailed spec (`upload_date_label`, `eligible`, `ineligible`, etc.) to `static/locales/en.json` & `th.json`.
Date display:

* EN → `YYYY-MM-DD`
* TH → `DD MMM YYYY`

---

## 8 · Testing

| Layer       | Tests                                                              |
| ----------- | ------------------------------------------------------------------ |
| Unit (BE)   | date regex parsing, day diff edge cases, leap year.                |
| Unit (FE)   | Stepper transitions, validation logic.                             |
| Integration | Image samples (clear, blurry, glare), flow happy-path & fail-path. |
| Performance | `verify-date` p95 < 2 s for 2 MB image; Lighthouse Perf ≥ 90.      |
| UAT         | 20 real Chang bottles covering 30–150 days old; mobile + desktop.  |

---

## 9 · Delivery Plan

| Phase                              | Duration | Owner   |
| ---------------------------------- | -------- | ------- |
| Backend endpoints & modules        | 5 d      | BE dev  |
| FE component scaffold & API wiring | 5 d      | FE dev  |
| Polish: i18n, A11y, QA             | 2 d      | FE + QA |
| UAT & deploy                       | 1 d      | DevOps  |

*Total: ≈ 13 working days.*

---

## 10 · Risks & Mitigations

| Risk                         | Mitigation                                                      |
| ---------------------------- | --------------------------------------------------------------- |
| Low-light / glare → OCR fail | Overlay tips + confidence retry + help modal.                   |
| Big video on mobile data     | Warn > 25 MB, recommend Wi-Fi, chunked upload.                  |
| Extra step drops conversions | Stepper shows progress; highlight benefit (“don’t waste time”). |

---

## 11 · Open Questions

1. Admin override to bypass date gate?
2. Store date-verification results in DB for analytics?
3. Auto-rotate thumbnails using EXIF orientation?

---

**PRD approved by:** *(signatures)*\_
