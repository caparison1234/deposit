# Design System: Editorial Fluidity for '예금하기 좋은 날'

## 1. Overview & Creative North Star
**Creative North Star: "The Radiant Harbor"**

Traditional fintech is often rigid, cold, and boxed-in. This design system breaks the "banking template" by treating the UI as a series of luminescent, floating layers rather than a static grid. We aim for a **"High-End Editorial"** feel—where whitespace is a functional tool, and typography carries the weight of the brand's authority. 

By leveraging intentional asymmetry, oversized "heroic" typography, and the rejection of hard structural lines, we create an experience that feels less like a ledger and more like a premium lifestyle concierge. We are not just showing data; we are curating a "Good Day" for the user’s financial future.

---

## 2. Colors & Surface Philosophy
The palette is rooted in a crisp, airy base, accented by a deep, authoritative Blue and a vibrant Coral.

*   **The "No-Line" Rule:** To achieve a premium look, **1px solid borders are strictly prohibited** for sectioning. Boundaries must be defined through tonal shifts. For example, a `surface-container-low` section should sit on a `surface` background to create a "valley" or "peak" effect.
*   **Surface Hierarchy & Nesting:** Treat the UI as physical layers. 
    *   **Level 0 (Base):** `surface` (#f8f9fd)
    *   **Level 1 (Sections):** `surface-container-low` (#f2f3f7)
    *   **Level 2 (Cards):** `surface-container-lowest` (#ffffff)
*   **The "Glass & Gradient" Rule:** Main CTAs and high-impact Hero sections must use subtle gradients (e.g., `primary` to `primary_container`) to provide "soul." Use Glassmorphism (semi-transparent `surface` with 20px backdrop-blur) for floating navigation or sticky headers to integrate the UI into the background.

---

## 3. Typography: The Editorial Voice
We use a high-contrast scale to guide the eye. While the system tokens use `plusJakartaSans`, for Korean text, we pair this with **Pretendard** to maintain a modern, friendly readability.

*   **Display & Headline (The Hook):** Use `display-lg` for interest rates (e.g., "5.2%"). These should feel like art pieces, not just numbers.
*   **Title (The Narrative):** `title-lg` should be used for product names, providing a clear, bold anchor for each card.
*   **Body & Label (The Detail):** `body-md` is our workhorse. Use `label-sm` in all-caps or high-weight for metadata to create a "tag" feel without needing a box.

*Constraint:* Never use more than three levels of hierarchy in a single component. Let the size difference do the talking.

---

## 4. Elevation & Depth
We move away from the "shadow-on-everything" approach. Depth is achieved through **Tonal Layering.**

*   **Ambient Shadows:** When a card must float (e.g., the primary Hero card), use a shadow with a 24px-32px blur at 6% opacity. The shadow color should be tinted with `primary` (blue) rather than grey to maintain the "Bright and Friendly" vibe.
*   **The "Ghost Border":** If a container is placed on a background of the same color (e.g., white on white), use a 1px border with `outline_variant` at **15% opacity**. It should be felt, not seen.
*   **Tactile Interaction:** On press, a component should not just darken; it should "sink" by shifting from `surface-container-lowest` to `surface-container-high`.

---

## 5. Components

### **The Hero Section (Split Layout)**
*   **Layout:** Use a 60/40 asymmetrical split.
*   **Left:** `label-md` (Coral/Tertiary) + `headline-md` (On-Surface).
*   **Right:** `display-lg` (Primary Blue) for the rate.
*   **Detail:** Place this on a `surface-container-low` background with a `md` (1.5rem) corner radius.

### **Pill-Style Rank Badges**
*   **Style:** `full` (9999px) roundedness. 
*   **Color:** Use `secondary_container` for the background and `on_secondary_container` for the text. No borders.
*   **Typography:** `label-md` Bold.

### **Rate List Cards**
*   **Structure:** No dividers. Use `DEFAULT` (1rem) vertical spacing between rows.
*   **Surface:** `surface-container-lowest` (White).
*   **Radius:** `md` (1.5rem) to feel approachable but professional.
*   **Interaction:** Subtle `surface_bright` hover state.

### **Buttons (The Signature CTA)**
*   **Primary:** Gradient from `primary` to `primary_container`. `full` roundedness. Large padding (16px vertical).
*   **Secondary:** Ghost style. No background, `primary` text, with a `Ghost Border` on hover only.

### **Input Fields**
*   **Style:** Minimalist. No bottom line. Use a `surface-container-high` background with `sm` (0.5rem) corners.
*   **Focus State:** A 2px `primary` "Ghost Border" (20% opacity) that expands slightly outward.

---

## 6. Do's and Don'ts

### **Do:**
*   **Do** use asymmetrical margins (e.g., 24px left, 20px right) to create a dynamic, editorial flow.
*   **Do** use `tertiary` (Coral) sparingly as a "heartbeat" color—only for alerts, high-yield highlights, or active states.
*   **Do** prioritize vertical white space. If the content feels tight, double the spacing.

### **Don't:**
*   **Don't** use black (#000000). Use `on_surface` (#191c1f) for all "black" text to keep the depth soft.
*   **Don't** use standard "Grey" for shadows. Always tint shadows with a hint of the `primary` blue.
*   **Don't** use divider lines to separate list items. Use the change in background color or 16px of whitespace instead.
*   **Don't** use sharp corners. Every interaction point must have at least a `sm` (0.5rem) radius to stay "friendly."