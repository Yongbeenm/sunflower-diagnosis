/**
 * Pure reducer for the symptom checker answer state.
 * No React dependencies — unit-testable in isolation.
 */

import type { Answer } from "@/types/api";

export interface CheckerState {
  /** Currently selected category ID, or null if none selected */
  activeCategoryId: number | null;
  /** Map of symptom_id → answer */
  answers: Record<number, Answer>;
}

export type CheckerAction =
  | { type: "SET_ANSWER"; symptomId: number; answer: Answer }
  | { type: "SET_BATCH_ANSWERS"; answers: Record<number, Answer> }
  | { type: "SELECT_CATEGORY"; categoryId: number }
  | { type: "RESET" };

export const initialCheckerState: CheckerState = {
  activeCategoryId: null,
  answers: {},
};

export function checkerReducer(state: CheckerState, action: CheckerAction): CheckerState {
  switch (action.type) {
    case "SET_ANSWER":
      return {
        ...state,
        answers: {
          ...state.answers,
          [action.symptomId]: action.answer,
        },
      };

    case "SET_BATCH_ANSWERS":
      return {
        ...state,
        answers: {
          ...state.answers,
          ...action.answers,
        },
      };

    case "SELECT_CATEGORY":
      return {
        ...state,
        activeCategoryId: action.categoryId,
      };

    case "RESET":
      return initialCheckerState;

    default:
      return state;
  }
}

/**
 * Count how many non-"unknown" answers exist.
 * "Unknown" is the tri-state default and means "the grower didn't say."
 */
export function countDefiniteAnswers(answers: Record<number, Answer>): number {
  return Object.values(answers).filter((a) => a !== "unknown").length;
}
