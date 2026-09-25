import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { ShaderBackground } from "../ShaderBackground";

describe("ShaderBackground", () => {
  it("renders canvas element without throwing in standard DOM environment", () => {
    const { container } = render(<ShaderBackground />);
    const canvas = container.querySelector("canvas");
    expect(canvas).toBeInTheDocument();
  });
});
