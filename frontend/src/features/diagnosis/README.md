# diagnosis/

The symptom checker. A guided flow, not a wall of checkboxes.

1. Choose the affected plant part (symptom categories, large tap targets).
2. Answer yes / no / not-sure per symptom. Tri-state — "no" is real evidence and the
   engine uses it to rule diseases out.
3. After each answer, debounced POST /diagnosis/preview updates a live ranked list.
4. Surface `next_best_questions` as "answering this would help most".
5. "Get result" posts to /diagnosis/sessions and routes to /check/:sessionId.

The result view always shows evidence — matched, contradicting, still unknown —
never a bare percentage. The no-match state is a designed screen that offers the
feedback form, not an error toast.
