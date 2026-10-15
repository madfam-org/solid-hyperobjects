# Hinged ring shell

Two semicircular shells with complementary same-side hinge knuckles and a separate pin; nominal assembly clearance only.

Original first-principles construction for Jewelry Studio. Units: mm; Z-up.
`size` scales planar dimensions from the 20 mm reference. `section` scales axial depths, not material thickness compensation. Both parameters reach the generator.

Expected solid count: 3. Multiple bodies are a loose component layout, not solved articulation.

Census: compared against all 512 existing solid manifests. The nearest generic base is `jewelry-blank`; this family's distinguishing interface is described above. No plain ring, signet, open bangle, aglet or magnetic snap is duplicated. This is a proposed new family, subject to reviewer census and consolidation before publication.

Geometry checks cover native B-Rep and tessellated mesh at declared parameter samples. They do not establish manufacture, gem retention, comfort, spring action, hinge function, strength, closure, allergy suitability or process compensation. Hardware and gems absent from the model must be specified separately.

Use: inspect the STEP; measure all intended mating interfaces; prototype with the actual process and material before wear. Wood grain and metal behaviour are unqualified.

CERN-OHL-W-2.0. Original source, no copied design. English and Spanish authored here; language review remains part of commons review.

Nominal assembly inspection: keep the first shell at its native origin; translate the second body by `(-32 * S, 0, 0)` and the pin by `(-53 * S, 0, 0)`, where `S = size / 20`. The resulting hinge axis is `(11 * S, 0)`. Shell edges are separated by `0.2 * S` mm; knuckles occupy axial intervals `[0, 2.4]` and `[2.6, 5]` multiplied by `S * section`. Pin radius is `0.8 * S` mm within the `1.0 * S` mm bore. These nominal clearances and zero positive-volume interference are native geometric checks only. No latch, closure stop, mechanical hinge life or wear qualification is supplied.
