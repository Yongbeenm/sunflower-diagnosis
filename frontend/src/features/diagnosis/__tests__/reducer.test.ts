import { describe, it, expect } from "vitest";
import { checkerReducer, initialCheckerState, countDefiniteAnswers } from "../reducer";
import type { CheckerState } from "../reducer";

describe("checkerReducer", () => {
  it("has empty answers and null activeCategoryId initially", () => {
    expect(initialCheckerState.activeCategoryId).toBeNull();
    expect(initialCheckerState.answers).toEqual({});
  });

  it("handles SELECT_CATEGORY", () => {
    const nextState = checkerReducer(initialCheckerState, {
      type: "SELECT_CATEGORY",
      categoryId: 42,
    });
    expect(nextState.activeCategoryId).toBe(42);
    expect(nextState.answers).toEqual({});
  });

  it("handles SET_ANSWER for yes, no, and unknown", () => {
    let state = checkerReducer(initialCheckerState, {
      type: "SET_ANSWER",
      symptomId: 1,
      answer: "yes",
    });
    expect(state.answers[1]).toBe("yes");

    state = checkerReducer(state, {
      type: "SET_ANSWER",
      symptomId: 2,
      answer: "no",
    });
    expect(state.answers[2]).toBe("no");

    state = checkerReducer(state, {
      type: "SET_ANSWER",
      symptomId: 1,
      answer: "unknown",
    });
    expect(state.answers[1]).toBe("unknown");
    expect(state.answers[2]).toBe("no");
  });

  it("handles SET_BATCH_ANSWERS to auto-check multiple symptoms", () => {
    const batchState = checkerReducer(initialCheckerState, {
      type: "SET_BATCH_ANSWERS",
      answers: { 10: "yes", 11: "yes", 12: "no" },
    });
    expect(batchState.answers[10]).toBe("yes");
    expect(batchState.answers[11]).toBe("yes");
    expect(batchState.answers[12]).toBe("no");
  });

  it("handles RESET back to initialCheckerState", () => {
    const dirtyState: CheckerState = {
      activeCategoryId: 5,
      answers: { 1: "yes", 2: "no", 3: "unknown" },
    };

    const resetState = checkerReducer(dirtyState, { type: "RESET" });
    expect(resetState).toEqual(initialCheckerState);
  });

  it("counts only definite answers (yes/no) and ignores unknown", () => {
    expect(countDefiniteAnswers({})).toBe(0);
    expect(
      countDefiniteAnswers({
        1: "unknown",
        2: "unknown",
      }),
    ).toBe(0);

    expect(
      countDefiniteAnswers({
        1: "yes",
        2: "no",
        3: "unknown",
      }),
    ).toBe(2);

    expect(
      countDefiniteAnswers({
        1: "yes",
        2: "yes",
        3: "no",
        4: "no",
      }),
    ).toBe(4);
  });
});
