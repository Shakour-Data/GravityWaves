# Index Page Documentation

## Overview
The Index page serves as the home page of the Gravity Analysis web application. It provides an introduction to the platform, user authentication options, and a grid of analysis summaries with expandable descriptions.

---

## Input
- `analyses` (list of dict): List of analysis objects passed from the backend, each containing:
  - `title` (str): Title of the analysis.
  - `short_desc` (str): Short description for preview.
  - `long_desc` (str): Detailed description for expanded view.
- `analyses_json` (JSON string): JSON serialized version of `analyses` for client-side scripting.

---

## Process
- Renders a header with logo, title, and slogan.
- Displays an introductory image.
- Shows login and register buttons for user authentication.
- Dynamically generates a responsive grid of analysis boxes (3 columns or auto-fit).
- Each analysis box shows a title and truncated description (50 words).
- Includes a "More"/"Less" toggle button to expand or collapse the detailed description (up to 250 words).
- Client-side JavaScript handles description truncation and toggle behavior.
- Footer displays copyright information.

---

## Output
- Fully rendered HTML page with styled content and interactive analysis description toggles.

---

## Feedback
- Console logs errors if analysis data or DOM elements are missing during toggle operations.
- Visual feedback via button text changes and description expansion/collapse.

---

## Page Structure
- Header: Logo image, site title, slogan.
- Main:
  - Introductory image.
  - Authentication buttons (Login, Register).
  - Analysis grid: Responsive layout with multiple analysis boxes.
    - Each box contains:
      - Title (h3)
      - Description div with truncated text
      - Toggle button for expanding/collapsing description
- Footer: Copyright notice.

---

## Required Backend APIs
- API to fetch the list of analyses with their titles, short and long descriptions.
- User authentication APIs for login and registration.

---

## Diagrams

### UML Component Diagram

```mermaid
componentDiagram
    component IndexPage {
        [Header]
        [Intro Image]
        [Auth Buttons]
        [Analysis Grid]
        [Footer]
    }
    component AnalysisGrid {
        [AnalysisBox] --> [Title]
        [AnalysisBox] --> [Description]
        [AnalysisBox] --> [ToggleButton]
    }
```

### BPMN Diagram

```mermaid
bpmnDiagram
    startEvent(Start) --> task(Render Header)
    task(Render Header) --> task(Render Intro Image)
    task(Render Intro Image) --> task(Render Auth Buttons)
    task(Render Auth Buttons) --> task(Render Analysis Grid)
    task(Render Analysis Grid) --> task(Setup Toggle JS)
    task(Setup Toggle JS) --> endEvent(End)
```

### Flowchart: Description Toggle Logic

```mermaid
flowchart TD
    A[User clicks toggle button] --> B{Is description expanded?}
    B -- No --> C[Expand description to 250 words]
    C --> D[Change button text to "Less"]
    B -- Yes --> E[Collapse description to 50 words]
    E --> F[Change button text to "More"]
```

---

This documentation provides a detailed understanding of the Index page structure, behavior, and backend dependencies.
