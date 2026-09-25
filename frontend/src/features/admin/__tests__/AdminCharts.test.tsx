import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import "@/i18n";
import {
  OutbreakTrendChart,
  SymptomDistributionChart,
  ConfidenceDistributionChart,
  DiagnosticHealthGauges,
} from "../components/AdminCharts";
import type { DailyChecksTrend, TopSymptom, NoMatchPattern } from "@/types/api";

const mockTrendData: DailyChecksTrend[] = [
  { date: "2026-09-01", count: 12 },
  { date: "2026-09-02", count: 18 },
  { date: "2026-09-03", count: 25 },
];

const mockSymptoms: TopSymptom[] = [
  { symptom_id: 1, code: "SYM_01", label: "Yellow Spots on Leaves", count: 42 },
  { symptom_id: 2, code: "SYM_02", label: "White Powdery Coating", count: 28 },
  { symptom_id: 3, code: "SYM_03", label: "Stem Canker", count: 14 },
];

const mockPatterns: NoMatchPattern[] = [
  { symptoms: ["Wilting stem", "Yellow spots"], count: 3 },
];

describe("AdminCharts Components", () => {
  it("renders OutbreakTrendChart with summary stats and time range selector", () => {
    render(<OutbreakTrendChart data={mockTrendData} />);
    expect(screen.getByText(/Disease Outbreak & Activity Trend/i)).toBeInTheDocument();
    expect(screen.getByText("7 Days")).toBeInTheDocument();
    expect(screen.getByText("14 Days")).toBeInTheDocument();
    expect(screen.getByText("30 Days")).toBeInTheDocument();
    expect(screen.getByText("55")).toBeInTheDocument(); // 12+18+25 total
  });

  it("renders SymptomDistributionChart with view toggles and breakdown items", () => {
    render(<SymptomDistributionChart topSymptoms={mockSymptoms} />);
    expect(screen.getByText(/Symptom Observation Frequency/i)).toBeInTheDocument();
    expect(screen.getByText("Donut Chart")).toBeInTheDocument();
    expect(screen.getByText("Ranked Bar")).toBeInTheDocument();
    expect(screen.getByText(/Yellow Spots on Leaves/i)).toBeInTheDocument();
    expect(screen.getByText(/White Powdery Coating/i)).toBeInTheDocument();
  });

  it("renders ConfidenceDistributionChart with confidence tiers", () => {
    render(
      <ConfidenceDistributionChart checksTotal={100} noMatchPatterns={mockPatterns} />,
    );
    expect(screen.getByText(/Diagnostic Confidence Distribution/i)).toBeInTheDocument();
    expect(screen.getByText(/High \(85-100%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Inconclusive \(<50%\)/i)).toBeInTheDocument();
  });

  it("renders DiagnosticHealthGauges with match rate, feedback, and active coverage", () => {
    render(
      <DiagnosticHealthGauges
        checksTotal={100}
        noMatchPatterns={mockPatterns}
        pendingFeedback={2}
        topSymptomsCount={8}
      />,
    );
    expect(screen.getByText(/Diagnostic Quality & Health Metrics/i)).toBeInTheDocument();
    expect(screen.getByText(/Conclusive Match Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Agronomist Feedback Resolution/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Symptom Coverage/i)).toBeInTheDocument();
  });
});

